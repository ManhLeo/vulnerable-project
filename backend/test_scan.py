from __future__ import annotations

import pytest

from app.ai.inference import InferenceOutput
from app.api import dependencies
from app.core.auth_dependencies import require_role
from app.core.config import settings
from app.core.limiter import get_rate_limit
from app.db.repositories.in_memory_scan_repository import InMemoryScanRepository
from app.models.user_models import Role, UserInDB
from app.services import scan_service as scan_service_module
from app.services.scan_service import ScanService


def test_require_role_allows_admin_enum_with_string_role() -> None:
    checker = require_role([Role.ADMIN.value])
    admin = UserInDB(
        _id="admin-id",
        email="admin@example.com",
        role=Role.ADMIN,
        password_hash="hash",
    )

    assert checker(admin) == admin


def test_require_role_denies_non_admin() -> None:
    checker = require_role([Role.ADMIN.value])
    user = UserInDB(
        _id="user-id",
        email="user@example.com",
        role=Role.USER,
        password_hash="hash",
    )

    with pytest.raises(Exception):
        checker(user)


def test_in_memory_repository_providers_are_singletons(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "use_in_memory_repository", True)

    assert dependencies.get_scan_repository() is dependencies.get_scan_repository()
    assert dependencies.get_user_repository() is dependencies.get_user_repository()
    assert dependencies.get_audit_repository() is dependencies.get_audit_repository()


def test_scan_rate_limit_policy_by_role() -> None:
    assert get_rate_limit("guest:127.0.0.1") == "5/minute"
    assert get_rate_limit("user:127.0.0.1") == "30/minute"
    assert get_rate_limit("admin:127.0.0.1") == "200/minute"


@pytest.mark.asyncio
async def test_scan_user_id_persists_and_history_is_owner_scoped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_predict(source_code: str, language: str) -> InferenceOutput:
        return InferenceOutput(
            is_vulnerable=False,
            confidence=0.95,
            vulnerability_probability=0.05,
        )

    monkeypatch.setattr(scan_service_module.inference_service, "predict", fake_predict)

    repository = InMemoryScanRepository()
    service = ScanService(repository=repository)

    result = await service.scan_code(
        source_code='#include <string.h>\nvoid f(char *s){ char b[8]; strcpy(b, s); }',
        language="c",
        user_id="user-1",
    )

    owner_history = await service.get_scan_history(user_id="user-1")
    other_history = await service.get_scan_history(user_id="user-2")
    detail = await service.get_scan_record(result["scan_id"])

    assert owner_history["total"] == 1
    assert other_history["total"] == 0
    assert detail is not None
    assert detail["user_id"] == "user-1"


@pytest.mark.asyncio
async def test_in_memory_history_survives_between_service_instances(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_predict(source_code: str, language: str) -> InferenceOutput:
        return InferenceOutput(
            is_vulnerable=False,
            confidence=0.9,
            vulnerability_probability=0.1,
        )

    monkeypatch.setattr(scan_service_module.inference_service, "predict", fake_predict)

    repository = InMemoryScanRepository()
    first_service = ScanService(repository=repository)
    second_service = ScanService(repository=repository)

    await first_service.scan_code(
        source_code="int add(int a, int b) { return a + b; }",
        language="c",
    )

    history = await second_service.get_scan_history()
    assert history["total"] == 1
