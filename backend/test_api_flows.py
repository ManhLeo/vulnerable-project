from __future__ import annotations

import csv
import io
from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.ai.inference import InferenceOutput
from app.ai.model_manager import LoadedModelInfo
from app.api import dependencies
from app.core.config import settings
from app.core.limiter import limiter
from app.core.security import get_password_hash
from app.main import ensure_admin_account
from app.main import app
from app.models.user_models import Role, UserInDB
from app.services import health_service as health_service_module
from app.services import model_service as model_service_module
from app.services import scan_service as scan_service_module
from app.api.routes.scan import _validate_upload_filename
from app.core.exceptions import BadRequestException


@pytest.fixture(autouse=True)
def in_memory_mode(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setattr(settings, "use_in_memory_repository", True)
    previous_limiter_enabled = limiter.enabled
    limiter.enabled = False
    dependencies.reset_in_memory_repositories()
    yield
    limiter.enabled = previous_limiter_enabled
    dependencies.reset_in_memory_repositories()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app, base_url="https://testserver")


def _client() -> TestClient:
    return TestClient(app, base_url="https://testserver")


async def _fake_predict(source_code: str, language: str) -> InferenceOutput:
    return InferenceOutput(
        is_vulnerable=False,
        confidence=0.9,
        vulnerability_probability=0.1,
    )


async def _fake_predict_with_checkpoint(
    source_code: str,
    language: str,
    checkpoint_name: str,
) -> InferenceOutput:
    confidence = 0.91 if checkpoint_name == "best_graphcodebert_linevul.pt" else 0.72
    return InferenceOutput(
        is_vulnerable=True,
        confidence=confidence,
        vulnerability_probability=confidence,
    )


async def _create_user(email: str, password: str, role: Role = Role.USER) -> UserInDB:
    repo = dependencies.get_user_repository()
    return await repo.create_user(
        UserInDB(
            _id="temp",
            email=email,
            role=role,
            password_hash=get_password_hash(password),
        )
    )


def _assert_error_envelope(payload: dict, error_code: str) -> None:
    assert payload["status"] == "error"
    assert isinstance(payload["message"], str)
    assert payload["error_code"] == error_code
    assert isinstance(payload["request_id"], str)


def test_auth_register_login_me_logout_success_envelopes(client: TestClient) -> None:
    email = f"user-{uuid4()}@example.com"
    password = "Password123"

    register = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert register.status_code == 200
    assert register.json()["status"] == "success"
    assert register.json()["data"]["email"] == email

    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    assert login.json()["status"] == "success"
    assert "access_token" in client.cookies

    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["data"]["email"] == email

    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 200
    assert logout.json()["data"]["authenticated"] is False


@pytest.mark.asyncio
async def test_auth_errors_are_enveloped(client: TestClient) -> None:
    await _create_user("auth-errors@example.com", "Password123")

    wrong_password = client.post(
        "/api/v1/auth/login",
        json={"email": "auth-errors@example.com", "password": "WrongPass123"},
    )
    assert wrong_password.status_code == 401
    _assert_error_envelope(wrong_password.json(), "UNAUTHORIZED")
    assert wrong_password.json()["message"] == "Invalid credentials"

    missing_field = client.post("/api/v1/auth/login", json={"email": "auth-errors@example.com"})
    assert missing_field.status_code == 422
    _assert_error_envelope(missing_field.json(), "VALIDATION_ERROR")

    weak_password = client.post(
        "/api/v1/auth/register",
        json={"email": "weak@example.com", "password": "password"},
    )
    assert weak_password.status_code == 400
    _assert_error_envelope(weak_password.json(), "BAD_REQUEST")

    unauthenticated = client.get("/api/v1/auth/me")
    assert unauthenticated.status_code == 401
    _assert_error_envelope(unauthenticated.json(), "UNAUTHORIZED")
    assert unauthenticated.json()["message"] == "Not authenticated"

    invalid_token = client.get(
        "/api/v1/auth/me",
        headers={"Cookie": "access_token=invalid-token"},
    )
    assert invalid_token.status_code == 401
    _assert_error_envelope(invalid_token.json(), "UNAUTHORIZED")
    assert invalid_token.json()["message"] == "Invalid token"


@pytest.mark.asyncio
async def test_rbac_admin_allowed_user_and_guest_denied(client: TestClient) -> None:
    await _create_user("admin@example.com", "Password123", Role.ADMIN)
    await _create_user("plain-user@example.com", "Password123", Role.USER)

    guest = client.get("/api/v1/admin/stats")
    assert guest.status_code == 401
    _assert_error_envelope(guest.json(), "UNAUTHORIZED")

    user_client = _client()
    user_client.post(
        "/api/v1/auth/login",
        json={"email": "plain-user@example.com", "password": "Password123"},
    )
    user_denied = user_client.get("/api/v1/admin/stats")
    assert user_denied.status_code == 403
    _assert_error_envelope(user_denied.json(), "FORBIDDEN")

    admin_client = _client()
    admin_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Password123"},
    )
    admin_allowed = admin_client.get("/api/v1/admin/stats")
    assert admin_allowed.status_code == 200


@pytest.mark.asyncio
async def test_scan_ownership_stats_and_admin_delete(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(scan_service_module.inference_service, "predict", _fake_predict)
    await _create_user("owner@example.com", "Password123", Role.USER)
    await _create_user("other@example.com", "Password123", Role.USER)
    await _create_user("scan-admin@example.com", "Password123", Role.ADMIN)

    owner_client = _client()
    owner_client.post("/api/v1/auth/login", json={"email": "owner@example.com", "password": "Password123"})
    scan = owner_client.post(
        "/api/v1/scan/code",
        json={"code": "int main(){ return 0; }", "language": "c_cpp"},
    )
    assert scan.status_code == 200
    scan_id = scan.json()["data"]["scan_id"]

    history = owner_client.get("/api/v1/scan/history")
    assert history.status_code == 200
    assert history.json()["data"]["total"] == 1

    stats = owner_client.get("/api/v1/scan/stats")
    assert stats.status_code == 200
    assert stats.json()["data"]["total_scans"] == 1

    other_client = _client()
    other_client.post("/api/v1/auth/login", json={"email": "other@example.com", "password": "Password123"})
    not_owner = other_client.get(f"/api/v1/scan/{scan_id}")
    assert not_owner.status_code == 404
    _assert_error_envelope(not_owner.json(), "SCAN_NOT_FOUND")

    admin_client = _client()
    admin_client.post("/api/v1/auth/login", json={"email": "scan-admin@example.com", "password": "Password123"})
    admin_detail = admin_client.get(f"/api/v1/scan/{scan_id}")
    assert admin_detail.status_code == 200
    deleted = admin_client.delete(f"/api/v1/scan/{scan_id}")
    assert deleted.status_code == 200


@pytest.mark.asyncio
async def test_scan_code_validation_and_model_unavailable(client: TestClient) -> None:
    await _create_user("scan-validation@example.com", "Password123", Role.USER)
    client.post("/api/v1/auth/login", json={"email": "scan-validation@example.com", "password": "Password123"})

    unsupported = client.post(
        "/api/v1/scan/code",
        json={"source_code": "print('x')", "language": "python"},
    )
    assert unsupported.status_code == 400
    _assert_error_envelope(unsupported.json(), "INVALID_LANGUAGE")

    missing_source = client.post("/api/v1/scan/code", json={"language": "c"})
    assert missing_source.status_code == 422
    _assert_error_envelope(missing_source.json(), "VALIDATION_ERROR")

    model_not_loaded = client.post(
        "/api/v1/scan/code",
        json={"source_code": "int main(){return 0;}", "language": "c"},
    )
    assert model_not_loaded.status_code == 503
    _assert_error_envelope(model_not_loaded.json(), "MODEL_NOT_LOADED")


def test_scan_file_upload_validation(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import asyncio

    monkeypatch.setattr(scan_service_module.inference_service, "predict", _fake_predict)
    asyncio.run(_create_user("file-validation@example.com", "Password123", Role.USER))
    client.post("/api/v1/auth/login", json={"email": "file-validation@example.com", "password": "Password123"})

    valid = client.post(
        "/api/v1/scan/file",
        files={"file": ("sample.c", b"int main(){return 0;}", "text/plain")},
    )
    assert valid.status_code == 200

    empty = client.post(
        "/api/v1/scan/file",
        files={"file": ("empty.c", b"", "text/plain")},
    )
    assert empty.status_code == 400
    _assert_error_envelope(empty.json(), "EMPTY_FILE")

    blocked = client.post(
        "/api/v1/scan/file",
        files={"file": ("sample.cpp.exe", b"MZ", "application/octet-stream")},
    )
    assert blocked.status_code == 400
    _assert_error_envelope(blocked.json(), "INVALID_FILE_EXTENSION")

    with pytest.raises(BadRequestException) as exc_info:
        _validate_upload_filename("bad\x00name.c")
    assert exc_info.value.error_code == "INVALID_FILENAME"

    oversized = client.post(
        "/api/v1/scan/file",
        files={"file": ("big.c", b"a" * (settings.max_upload_size_bytes + 1), "text/plain")},
    )
    assert oversized.status_code == 400
    _assert_error_envelope(oversized.json(), "FILE_TOO_LARGE")


def test_scan_file_extension_aliases_wrong_hint_and_non_utf8(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import asyncio

    monkeypatch.setattr(scan_service_module.inference_service, "predict", _fake_predict)
    asyncio.run(_create_user("file-aliases@example.com", "Password123", Role.USER))
    client.post("/api/v1/auth/login", json={"email": "file-aliases@example.com", "password": "Password123"})

    header = client.post(
        "/api/v1/scan/file",
        files={"file": ("sample.h", b"int main(){return 0;}", "text/plain")},
    )
    assert header.status_code == 200

    hpp = client.post(
        "/api/v1/scan/file",
        files={"file": ("sample.hpp", b"int main(){return 0;}", "text/plain")},
    )
    assert hpp.status_code == 200

    wrong_hint = client.post(
        "/api/v1/scan/file",
        data={"language": "python"},
        files={"file": ("sample.cpp", b"int main(){return 0;}", "text/plain")},
    )
    assert wrong_hint.status_code == 400
    _assert_error_envelope(wrong_hint.json(), "INVALID_LANGUAGE")

    non_utf8 = client.post(
        "/api/v1/scan/file",
        files={"file": ("sample.c", b"\xff\xfeint main(){return 0;}", "text/plain")},
    )
    assert non_utf8.status_code == 200


@pytest.mark.asyncio
async def test_history_query_validation_and_unsafe_filters(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(scan_service_module.inference_service, "predict", _fake_predict)
    await _create_user("history@example.com", "Password123", Role.USER)
    client.post("/api/v1/auth/login", json={"email": "history@example.com", "password": "Password123"})

    invalid_page = client.get("/api/v1/scan/history", params={"page": 0})
    assert invalid_page.status_code == 422
    _assert_error_envelope(invalid_page.json(), "VALIDATION_ERROR")

    invalid_limit = client.get("/api/v1/scan/history", params={"limit": 101})
    assert invalid_limit.status_code == 422
    _assert_error_envelope(invalid_limit.json(), "VALIDATION_ERROR")

    unsafe_filename = client.get("/api/v1/scan/history", params={"filename": "bad$name"})
    assert unsafe_filename.status_code == 400
    _assert_error_envelope(unsafe_filename.json(), "INVALID_FILTER")

    unsafe_search = client.get("/api/v1/scan/history", params={"search": "bad.name"})
    assert unsafe_search.status_code == 400
    _assert_error_envelope(unsafe_search.json(), "INVALID_FILTER")


def test_error_envelope_validation_malformed_json_and_body_too_large(client: TestClient) -> None:
    malformed = client.post(
        "/api/v1/scan/code",
        content="{bad json",
        headers={"Content-Type": "application/json"},
    )
    assert malformed.status_code == 422
    _assert_error_envelope(malformed.json(), "VALIDATION_ERROR")

    too_large = client.post(
        "/api/v1/scan/code",
        content="{}",
        headers={
            "Content-Type": "application/json",
            "Content-Length": str(settings.max_request_body_size + 1),
        },
    )
    assert too_large.status_code == 413
    _assert_error_envelope(too_large.json(), "PAYLOAD_TOO_LARGE")


def test_health_reports_degraded_database_and_model(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "use_in_memory_repository", False)
    monkeypatch.setattr(health_service_module.database_manager, "_client", None)
    monkeypatch.setattr(health_service_module.database_manager, "_db", None)
    monkeypatch.setattr(
        health_service_module.model_manager,
        "info",
        lambda: LoadedModelInfo(
            model_name="test-model",
            device="cpu",
            loaded=False,
            active_checkpoint="missing.pt",
            available_checkpoints=[],
        ),
    )

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "degraded"
    assert data["degraded"] is True
    assert data["database"]["status"] == "disconnected"
    assert data["model"]["status"] == "not_loaded"
    assert isinstance(data["timestamp"], str)


def test_model_info_and_select_error_envelopes(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        model_service_module.model_manager,
        "info",
        lambda: LoadedModelInfo(
            model_name="test-model",
            device="cpu",
            loaded=True,
            active_checkpoint="active.pt",
            available_checkpoints=["active.pt"],
        ),
    )

    info = client.get("/api/v1/model/info")
    assert info.status_code == 200
    assert info.json()["data"]["active_checkpoint"] == "active.pt"

    async def _create_admin_user() -> None:
        await _create_user("model-admin-errors@example.com", "Password123", Role.ADMIN)

    import asyncio

    asyncio.run(_create_admin_user())

    admin_client = _client()
    admin_client.post(
        "/api/v1/auth/login",
        json={"email": "model-admin-errors@example.com", "password": "Password123"},
    )

    async def missing_checkpoint(checkpoint_name: str) -> None:
        raise FileNotFoundError(checkpoint_name)

    monkeypatch.setattr(model_service_module.model_manager, "change_checkpoint", missing_checkpoint)
    missing = admin_client.post("/api/v1/model/select", json={"checkpoint_name": "missing.pt"})
    assert missing.status_code == 404
    _assert_error_envelope(missing.json(), "CHECKPOINT_NOT_FOUND")

    async def load_failed(checkpoint_name: str) -> None:
        raise RuntimeError("bad checkpoint")

    monkeypatch.setattr(model_service_module.model_manager, "change_checkpoint", load_failed)
    failed = admin_client.post("/api/v1/model/select", json={"checkpoint_name": "bad.pt"})
    assert failed.status_code == 503
    _assert_error_envelope(failed.json(), "CHECKPOINT_LOAD_FAILED")


@pytest.mark.asyncio
async def test_model_select_is_admin_only(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    await _create_user("model-user@example.com", "Password123", Role.USER)
    await _create_user("model-admin@example.com", "Password123", Role.ADMIN)

    guest = client.post("/api/v1/model/select", json={"checkpoint_name": "best_codebert_linevul.pt"})
    assert guest.status_code == 401
    _assert_error_envelope(guest.json(), "UNAUTHORIZED")

    user_client = _client()
    user_client.post("/api/v1/auth/login", json={"email": "model-user@example.com", "password": "Password123"})
    denied = user_client.post("/api/v1/model/select", json={"checkpoint_name": "best_codebert_linevul.pt"})
    assert denied.status_code == 403
    _assert_error_envelope(denied.json(), "FORBIDDEN")

    async def _noop_change_checkpoint(checkpoint_name: str) -> None:
        return None

    monkeypatch.setattr(model_service_module.model_manager, "change_checkpoint", _noop_change_checkpoint)
    admin_client = _client()
    admin_client.post("/api/v1/auth/login", json={"email": "model-admin@example.com", "password": "Password123"})
    allowed = admin_client.post("/api/v1/model/select", json={"checkpoint_name": "best_codebert_linevul.pt"})
    assert allowed.status_code == 200


def test_model_info_includes_graphcodebert_and_ensemble_option(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        model_service_module.model_manager,
        "info",
        lambda: LoadedModelInfo(
            model_name="test-model",
            device="cpu",
            loaded=True,
            active_checkpoint="best_codebert_linevul.pt",
            available_checkpoints=[
                "best_codebert_linevul.pt",
                "best_graphcodebert_linevul.pt",
            ],
        ),
    )
    monkeypatch.setattr(
        model_service_module.model_manager,
        "is_checkpoint_loaded",
        lambda checkpoint_name: checkpoint_name == "best_codebert_linevul.pt",
    )

    response = client.get("/api/v1/model/info")
    assert response.status_code == 200
    data = response.json()["data"]
    assert "best_graphcodebert_linevul.pt" in data["available_checkpoints"]
    option_names = [item["checkpoint_name"] for item in data["available_model_options"]]
    assert "__ensemble_best_confidence__" in option_names
    assert data["supported_modes"] == ["single", "best_confidence"]


def test_scan_code_without_model_mode_preserves_legacy_behavior(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import asyncio

    monkeypatch.setattr(scan_service_module.inference_service, "predict", _fake_predict)
    asyncio.run(_create_user("legacy-scan@example.com", "Password123", Role.USER))
    client.post("/api/v1/auth/login", json={"email": "legacy-scan@example.com", "password": "Password123"})

    response = client.post(
        "/api/v1/scan/code",
        json={"source_code": "int main(){return 0;}", "language": "c"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["metadata"]["model_mode"] == "single"


def test_demo_samples_and_scan_do_not_call_inference(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fail_predict(*args, **kwargs):
        raise AssertionError("demo scan must not call inference")

    monkeypatch.setattr(scan_service_module.inference_service, "predict", fail_predict)
    monkeypatch.setattr(scan_service_module.inference_service, "predict_with_checkpoint", fail_predict)

    samples = client.get("/api/v1/demo/samples")
    assert samples.status_code == 200
    sample_list = samples.json()["data"]
    assert sample_list
    assert {"id", "title", "language", "source_code", "description"} <= set(sample_list[0].keys())

    demo = client.post("/api/v1/demo/scan", json={"sample_id": "unsafe_strcpy"})
    assert demo.status_code == 200
    payload = demo.json()["data"]
    assert payload["scan_id"] == "demo-unsafe_strcpy"
    assert payload["is_demo"] is True
    assert payload["source_type"] == "demo"
    assert payload["metadata"]["model_mode"] == "demo"
    assert payload["metadata"]["inference_used"] is False
    assert payload["source_code"]
    assert payload["is_vulnerable"] is True
    assert payload["findings"]

    missing = client.post("/api/v1/demo/scan", json={"sample_id": "missing-sample"})
    assert missing.status_code == 404
    _assert_error_envelope(missing.json(), "DEMO_SAMPLE_NOT_FOUND")


@pytest.mark.asyncio
async def test_guest_scan_uses_findings_metrics_without_inference(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fail_predict(*args, **kwargs):
        raise AssertionError("guest scan must not call AI inference")

    def fail_model_manager(*args, **kwargs):
        raise AssertionError("guest scan must not call model manager")

    monkeypatch.setattr(scan_service_module.inference_service, "predict", fail_predict)
    monkeypatch.setattr(scan_service_module.inference_service, "predict_with_checkpoint", fail_predict)
    monkeypatch.setattr(scan_service_module.model_manager, "get_active_checkpoint", fail_model_manager)
    monkeypatch.setattr(scan_service_module.model_manager, "info", fail_model_manager)
    await _create_user("role-guest@example.com", "Password123", Role.GUEST)

    unauth_code = client.post(
        "/api/v1/scan/code",
        json={"source_code": '#include <string.h>\nvoid f(char *s){ char b[8]; strcpy(b, s); }', "language": "c"},
    )
    assert unauth_code.status_code == 200
    payload = unauth_code.json()["data"]
    assert payload["metadata"]["inference_used"] is False
    assert payload["metadata"]["model_mode"] == "findings_metrics_only"
    assert payload["metadata"]["model_name"] is None
    assert payload["metadata"]["model_version"] is None
    assert payload["analysis_mode"] == "guest_metrics"
    assert payload["findings_metrics"]["findings_count"] > 0
    assert payload["findings"]

    unauth_file = client.post(
        "/api/v1/scan/file",
        files={"file": ("sample.c", b"void f(char *s){ char b[8]; strcpy(b, s); }", "text/plain")},
    )
    assert unauth_file.status_code == 200
    assert unauth_file.json()["data"]["metadata"]["inference_used"] is False

    guest_client = _client()
    guest_client.post("/api/v1/auth/login", json={"email": "role-guest@example.com", "password": "Password123"})
    guest_code = guest_client.post(
        "/api/v1/scan/code",
        json={"source_code": "int main(){return 0;}", "language": "c"},
    )
    assert guest_code.status_code == 200
    assert guest_code.json()["data"]["metadata"]["inference_used"] is False

    guest_model_selection = guest_client.post(
        "/api/v1/scan/code",
        json={
            "source_code": "int main(){return 0;}",
            "language": "c",
            "model_mode": "single",
        },
    )
    assert guest_model_selection.status_code == 403
    _assert_error_envelope(guest_model_selection.json(), "MODEL_SELECTION_REQUIRES_AUTH")

    guest_file_model_selection = guest_client.post(
        "/api/v1/scan/file",
        data={"checkpoint_name": "best_graphcodebert_linevul.pt"},
        files={"file": ("sample.c", b"int main(){return 0;}", "text/plain")},
    )
    assert guest_file_model_selection.status_code == 403
    _assert_error_envelope(guest_file_model_selection.json(), "MODEL_SELECTION_REQUIRES_AUTH")


@pytest.mark.asyncio
async def test_user_admin_scan_uses_ai_and_metrics(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(scan_service_module.inference_service, "predict", _fake_predict)
    await _create_user("real-scan-user@example.com", "Password123", Role.USER)
    await _create_user("real-scan-admin@example.com", "Password123", Role.ADMIN)

    user_client = _client()
    user_client.post("/api/v1/auth/login", json={"email": "real-scan-user@example.com", "password": "Password123"})
    user_scan = user_client.post(
        "/api/v1/scan/code",
        json={"source_code": "int main(){return 0;}", "language": "c"},
    )
    assert user_scan.status_code == 200
    user_payload = user_scan.json()["data"]
    assert user_payload["metadata"]["inference_used"] is True
    assert user_payload["metadata"]["analysis_mode"] == "metrics_plus_ai"
    assert "findings_metrics" in user_payload

    admin_client = _client()
    admin_client.post("/api/v1/auth/login", json={"email": "real-scan-admin@example.com", "password": "Password123"})
    admin_scan = admin_client.post(
        "/api/v1/scan/code",
        json={"source_code": "int main(){return 0;}", "language": "c"},
    )
    assert admin_scan.status_code == 200
    assert admin_scan.json()["data"]["metadata"]["inference_used"] is True


@pytest.mark.asyncio
async def test_user_request_level_checkpoint_selection_allowed(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(scan_service_module.inference_service, "predict_with_checkpoint", _fake_predict_with_checkpoint)
    await _create_user("request-model-user@example.com", "Password123", Role.USER)
    client.post(
        "/api/v1/auth/login",
        json={"email": "request-model-user@example.com", "password": "Password123"},
    )

    response = client.post(
        "/api/v1/scan/code",
        json={
            "source_code": "int main(){return 0;}",
            "language": "c",
            "checkpoint_name": "best_graphcodebert_linevul.pt",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["metadata"]["selected_checkpoint"] == "best_graphcodebert_linevul.pt"


def test_scan_code_best_confidence_selects_highest_confidence_and_persists_metadata(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(scan_service_module.inference_service, "predict_with_checkpoint", _fake_predict_with_checkpoint)
    import asyncio

    asyncio.run(_create_user("ensemble-owner@example.com", "Password123", Role.USER))
    client.post("/api/v1/auth/login", json={"email": "ensemble-owner@example.com", "password": "Password123"})

    response = client.post(
        "/api/v1/scan/code",
        json={
            "source_code": "int main(){return 0;}",
            "language": "c",
            "model_mode": "best_confidence",
            "checkpoint_names": [
                "best_codebert_linevul.pt",
                "best_graphcodebert_linevul.pt",
            ],
        },
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["metadata"]["model_mode"] == "best_confidence"
    assert payload["metadata"]["selected_checkpoint"] == "best_graphcodebert_linevul.pt"
    assert len(payload["metadata"]["candidate_results"]) == 2

    detail = client.get(f"/api/v1/scan/{payload['scan_id']}")
    assert detail.status_code == 200
    assert detail.json()["data"]["metadata"]["selected_checkpoint"] == "best_graphcodebert_linevul.pt"


def test_scan_code_best_confidence_tie_breaks_by_severity(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def same_confidence(source_code: str, language: str, checkpoint_name: str) -> InferenceOutput:
        return InferenceOutput(
            is_vulnerable=True,
            confidence=0.9,
            vulnerability_probability=0.9,
        )

    risk_levels = iter(["MEDIUM", "HIGH"])
    monkeypatch.setattr(scan_service_module.inference_service, "predict_with_checkpoint", same_confidence)
    monkeypatch.setattr(scan_service_module, "classify_risk_level", lambda risk_score, findings: next(risk_levels))
    import asyncio

    asyncio.run(_create_user("tie-break-user@example.com", "Password123", Role.USER))
    client.post("/api/v1/auth/login", json={"email": "tie-break-user@example.com", "password": "Password123"})

    response = client.post(
        "/api/v1/scan/code",
        json={
            "source_code": "int main(){return 0;}",
            "language": "c",
            "model_mode": "best_confidence",
            "checkpoint_names": [
                "best_codebert_linevul.pt",
                "best_graphcodebert_linevul.pt",
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["metadata"]["selected_checkpoint"] == "best_graphcodebert_linevul.pt"


def test_scan_code_explicit_checkpoint_errors_are_enveloped(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def missing_checkpoint(source_code: str, language: str, checkpoint_name: str) -> InferenceOutput:
        from app.core.exceptions import NotFoundException

        raise NotFoundException(message="Checkpoint not found", error_code="CHECKPOINT_NOT_FOUND")

    monkeypatch.setattr(scan_service_module.inference_service, "predict_with_checkpoint", missing_checkpoint)
    import asyncio

    asyncio.run(_create_user("checkpoint-error-user@example.com", "Password123", Role.USER))
    client.post(
        "/api/v1/auth/login",
        json={"email": "checkpoint-error-user@example.com", "password": "Password123"},
    )
    missing = client.post(
        "/api/v1/scan/code",
        json={
            "source_code": "int main(){return 0;}",
            "language": "c",
            "checkpoint_name": "missing.pt",
        },
    )
    assert missing.status_code == 404
    _assert_error_envelope(missing.json(), "CHECKPOINT_NOT_FOUND")


@pytest.mark.asyncio
async def test_admin_bootstrap_works_in_in_memory_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "admin_email", "bootstrap-admin@example.com")
    monkeypatch.setattr(settings, "admin_password", "Password123")
    monkeypatch.setattr(settings, "use_in_memory_repository", True)

    await ensure_admin_account()

    repo = dependencies.get_user_repository()
    admin = await repo.get_user_by_email("bootstrap-admin@example.com")
    assert admin is not None
    assert admin.role == Role.ADMIN


@pytest.mark.asyncio
async def test_admin_csv_export_permissions_and_content(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vulnerability_results = iter([False, True])

    async def _predict_with_label(source_code: str, language: str) -> InferenceOutput:
        is_vulnerable = next(vulnerability_results)
        return InferenceOutput(
            is_vulnerable=is_vulnerable,
            confidence=0.88 if is_vulnerable else 0.91,
            vulnerability_probability=0.88 if is_vulnerable else 0.09,
        )

    monkeypatch.setattr(scan_service_module.inference_service, "predict", _predict_with_label)
    await _create_user("csv-user@example.com", "Password123", Role.USER)
    await _create_user("csv-admin@example.com", "Password123", Role.ADMIN)

    guest = client.get("/api/v1/admin/scan-sources/export.csv")
    assert guest.status_code == 401
    _assert_error_envelope(guest.json(), "UNAUTHORIZED")

    safe_source_code = 'int main(){\n  printf("hello, csv");\n  return 0;\n}'
    vulnerable_source_code = 'char buf[4];\nstrcpy(buf, "too long, quoted");\n'
    user_client = _client()
    user_client.post("/api/v1/auth/login", json={"email": "csv-user@example.com", "password": "Password123"})
    safe_scan = user_client.post(
        "/api/v1/scan/code",
        json={"source_code": safe_source_code, "language": "c"},
    )
    assert safe_scan.status_code == 200
    vulnerable_scan = user_client.post(
        "/api/v1/scan/code",
        json={"source_code": vulnerable_source_code, "language": "c"},
    )
    assert vulnerable_scan.status_code == 200

    denied = user_client.get("/api/v1/admin/scan-sources/export.csv")
    assert denied.status_code == 403
    _assert_error_envelope(denied.json(), "FORBIDDEN")

    admin_client = _client()
    admin_client.post("/api/v1/auth/login", json={"email": "csv-admin@example.com", "password": "Password123"})
    exported = admin_client.get("/api/v1/admin/scan-sources/export.csv")
    assert exported.status_code == 200
    assert "text/csv" in exported.headers["content-type"]
    assert "scan_sources_export_" in exported.headers["content-disposition"]

    reader = csv.DictReader(io.StringIO(exported.text))
    rows = list(reader)
    assert reader.fieldnames == [
        "scan_id",
        "user_id",
        "user_email",
        "created_at",
        "filename",
        "language",
        "risk_level",
        "vulnerable",
        "confidence",
        "model_mode",
        "selected_checkpoint",
        "source_code",
    ]
    rows_by_source = {row["source_code"]: row for row in rows}
    assert safe_source_code in rows_by_source
    assert vulnerable_source_code in rows_by_source
    assert rows_by_source[safe_source_code]["user_email"] == "csv-user@example.com"
    assert rows_by_source[safe_source_code]["vulnerable"] == "0"
    assert rows_by_source[vulnerable_source_code]["vulnerable"] == "1"
    assert rows_by_source[safe_source_code]["source_code"] == safe_source_code
    assert rows_by_source[vulnerable_source_code]["source_code"] == vulnerable_source_code
    assert "password_hash" not in exported.text
    assert "Password123" not in exported.text


@pytest.mark.asyncio
async def test_admin_user_management_delete_guards(client: TestClient) -> None:
    admin = await _create_user("delete-admin@example.com", "Password123", Role.ADMIN)
    normal_user = await _create_user("delete-user@example.com", "Password123", Role.USER)
    await _create_user("delete-actor@example.com", "Password123", Role.USER)

    user_client = _client()
    user_client.post("/api/v1/auth/login", json={"email": "delete-actor@example.com", "password": "Password123"})
    user_denied = user_client.delete(f"/api/v1/admin/users/{normal_user.id}")
    assert user_denied.status_code == 403
    _assert_error_envelope(user_denied.json(), "FORBIDDEN")

    admin_client = _client()
    admin_client.post("/api/v1/auth/login", json={"email": "delete-admin@example.com", "password": "Password123"})
    self_delete = admin_client.delete(f"/api/v1/admin/users/{admin.id}")
    assert self_delete.status_code == 400
    _assert_error_envelope(self_delete.json(), "CANNOT_DELETE_SELF")

    deleted = admin_client.delete(f"/api/v1/admin/users/{normal_user.id}")
    assert deleted.status_code == 200
