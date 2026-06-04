from __future__ import annotations

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


def test_scan_code_validation_and_model_unavailable(client: TestClient) -> None:
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
    monkeypatch.setattr(scan_service_module.inference_service, "predict", _fake_predict)

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
    monkeypatch.setattr(scan_service_module.inference_service, "predict", _fake_predict)

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

    async def missing_checkpoint(checkpoint_name: str) -> None:
        raise FileNotFoundError(checkpoint_name)

    monkeypatch.setattr(model_service_module.model_manager, "change_checkpoint", missing_checkpoint)
    missing = client.post("/api/v1/model/select", json={"checkpoint_name": "missing.pt"})
    assert missing.status_code == 404
    _assert_error_envelope(missing.json(), "CHECKPOINT_NOT_FOUND")

    async def load_failed(checkpoint_name: str) -> None:
        raise RuntimeError("bad checkpoint")

    monkeypatch.setattr(model_service_module.model_manager, "change_checkpoint", load_failed)
    failed = client.post("/api/v1/model/select", json={"checkpoint_name": "bad.pt"})
    assert failed.status_code == 503
    _assert_error_envelope(failed.json(), "CHECKPOINT_LOAD_FAILED")


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
