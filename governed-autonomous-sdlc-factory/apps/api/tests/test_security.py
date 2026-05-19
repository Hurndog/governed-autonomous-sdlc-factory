"""Security Phase 1 — Authentication & RBAC tests."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Set env vars BEFORE importing anything that depends on settings
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-tests")
os.environ.setdefault("ALLOW_BOOTSTRAP", "true")

from src.core.auth import hash_password, create_access_token, Role, verify_password


# ===========================================================================
# Password hashing tests
# ===========================================================================


def test_hash_password_produces_different_hashes():
    """Same password should produce different hashes (bcrypt salt)."""
    h1 = hash_password("TestPass123!")
    h2 = hash_password("TestPass123!")
    assert h1 != h2
    assert h1.startswith("$2b$")


def test_verify_password_correct():
    h = hash_password("TestPass123!")
    assert verify_password("TestPass123!", h) is True


def test_verify_password_incorrect():
    h = hash_password("TestPass123!")
    assert verify_password("WrongPass!", h) is False


def test_verify_password_empty_hash():
    assert verify_password("TestPass123!", "") is False


# ===========================================================================
# JWT tests
# ===========================================================================


def test_create_access_token_returns_string():
    user = MagicMock()
    user.id = "test-uuid"
    user.email = "test@test.com"
    user.display_name = "Test"
    user.role = "admin"
    token = create_access_token(user)
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_valid_token():
    from src.core.auth import decode_token
    user = MagicMock()
    user.id = "test-uuid"
    user.email = "test@test.com"
    user.display_name = "Test"
    user.role = "admin"
    token = create_access_token(user)
    payload = decode_token(token)
    assert payload["sub"] == "test-uuid"
    assert payload["email"] == "test@test.com"
    assert payload["role"] == "admin"


def test_decode_expired_token():
    from src.core.auth import decode_token
    import jwt as pyjwt
    from datetime import datetime, timedelta, timezone
    # Create an expired token
    payload = {
        "sub": "test-uuid",
        "email": "test@test.com",
        "display_name": "Test",
        "role": "admin",
        "iat": datetime.now(timezone.utc) - timedelta(hours=48),
        "exp": datetime.now(timezone.utc) - timedelta(hours=24),
    }
    expired_token = pyjwt.encode(payload, "test-secret-key-for-tests", algorithm="HS256")
    with pytest.raises(Exception) as exc_info:
        decode_token(expired_token)
    assert "expired" in str(exc_info.value).lower() or "401" in str(exc_info.value)


def test_decode_invalid_token():
    from src.core.auth import decode_token
    with pytest.raises(Exception):
        decode_token("this-is-not-a-valid-token")


# ===========================================================================
# Role & Permission tests
# ===========================================================================


def test_admin_has_all_permissions():
    assert Role.ADMIN in Role
    from src.core.auth import role_has_permission
    assert role_has_permission(Role.ADMIN, "system.manage_users") is True
    assert role_has_permission(Role.ADMIN, "runs.create") is True
    assert role_has_permission(Role.ADMIN, "settings.edit") is True
    assert role_has_permission(Role.ADMIN, "*") is True  # Admin wildcard check


def test_engineer_permissions():
    from src.core.auth import role_has_permission
    assert role_has_permission(Role.ENGINEER, "runs.create") is True
    assert role_has_permission(Role.ENGINEER, "runs.view") is True
    assert role_has_permission(Role.ENGINEER, "runs.control") is True
    assert role_has_permission(Role.ENGINEER, "artifacts.view") is True
    assert role_has_permission(Role.ENGINEER, "artifacts.edit") is True
    assert role_has_permission(Role.ENGINEER, "logs.view") is True
    assert role_has_permission(Role.ENGINEER, "tokenomics.view") is True
    # Should NOT have
    assert role_has_permission(Role.ENGINEER, "system.manage_users") is False
    assert role_has_permission(Role.ENGINEER, "settings.edit") is False
    assert role_has_permission(Role.ENGINEER, "system.view_audit_log") is False


def test_executive_viewer_permissions():
    from src.core.auth import role_has_permission
    assert role_has_permission(Role.EXECUTIVE_VIEWER, "runs.view") is True
    assert role_has_permission(Role.EXECUTIVE_VIEWER, "governance.view") is True
    assert role_has_permission(Role.EXECUTIVE_VIEWER, "tokenomics.view") is True
    assert role_has_permission(Role.EXECUTIVE_VIEWER, "system.view_health") is True
    # Should NOT have
    assert role_has_permission(Role.EXECUTIVE_VIEWER, "runs.create") is False
    assert role_has_permission(Role.EXECUTIVE_VIEWER, "runs.control") is False
    assert role_has_permission(Role.EXECUTIVE_VIEWER, "artifacts.edit") is False
    assert role_has_permission(Role.EXECUTIVE_VIEWER, "logs.view") is False


def test_auditor_permissions():
    from src.core.auth import role_has_permission
    assert role_has_permission(Role.AUDITOR, "evidence.view") is True
    assert role_has_permission(Role.AUDITOR, "evidence.export") is True
    assert role_has_permission(Role.AUDITOR, "governance.view") is True
    assert role_has_permission(Role.AUDITOR, "integrity.verify") is True
    assert role_has_permission(Role.AUDITOR, "logs.view") is True
    assert role_has_permission(Role.AUDITOR, "system.view_audit_log") is True
    assert role_has_permission(Role.AUDITOR, "artifacts.view") is True
    # Should NOT have
    assert role_has_permission(Role.AUDITOR, "runs.create") is False
    assert role_has_permission(Role.AUDITOR, "runs.control") is False
    assert role_has_permission(Role.AUDITOR, "artifacts.edit") is False


def test_governance_reviewer_permissions():
    from src.core.auth import role_has_permission
    assert role_has_permission(Role.GOVERNANCE_REVIEWER, "governance.view") is True
    assert role_has_permission(Role.GOVERNANCE_REVIEWER, "governance.approve") is True
    assert role_has_permission(Role.GOVERNANCE_REVIEWER, "evidence.view") is True
    assert role_has_permission(Role.GOVERNANCE_REVIEWER, "evidence.export") is True
    assert role_has_permission(Role.GOVERNANCE_REVIEWER, "logs.view") is True
    # Should NOT have
    assert role_has_permission(Role.GOVERNANCE_REVIEWER, "runs.create") is False
    assert role_has_permission(Role.GOVERNANCE_REVIEWER, "runs.control") is False
    assert role_has_permission(Role.GOVERNANCE_REVIEWER, "system.manage_users") is False


def test_operator_permissions():
    from src.core.auth import role_has_permission
    assert role_has_permission(Role.OPERATOR, "runs.view") is True
    assert role_has_permission(Role.OPERATOR, "runs.control") is True
    assert role_has_permission(Role.OPERATOR, "logs.view") is True
    assert role_has_permission(Role.OPERATOR, "providers.view") is True
    assert role_has_permission(Role.OPERATOR, "system.view_health") is True
    # Should NOT have
    assert role_has_permission(Role.OPERATOR, "runs.create") is False
    assert role_has_permission(Role.OPERATOR, "governance.approve") is False
    assert role_has_permission(Role.OPERATOR, "system.manage_users") is False


def test_architect_permissions():
    from src.core.auth import role_has_permission
    assert role_has_permission(Role.ARCHITECT, "runs.create") is True
    assert role_has_permission(Role.ARCHITECT, "runs.view") is True
    assert role_has_permission(Role.ARCHITECT, "artifacts.view") is True
    assert role_has_permission(Role.ARCHITECT, "artifacts.edit") is True
    assert role_has_permission(Role.ARCHITECT, "projects.manage") is True
    assert role_has_permission(Role.ARCHITECT, "integrity.verify") is True
    # Should NOT have
    assert role_has_permission(Role.ARCHITECT, "runs.control") is False
    assert role_has_permission(Role.ARCHITECT, "system.manage_users") is False
    assert role_has_permission(Role.ARCHITECT, "settings.edit") is False


# ===========================================================================
# AuthContext tests
# ===========================================================================


def test_auth_context_has_permission():
    from src.core.auth import AuthContext
    ctx = AuthContext(
        user_id="test-id",
        email="admin@test.com",
        display_name="Admin",
        role=Role.ADMIN,
    )
    assert ctx.has_permission("system.manage_users") is True
    assert ctx.has_permission("*") is True  # Admin wildcard


def test_auth_context_engineer_has_limited_permissions():
    from src.core.auth import AuthContext
    ctx = AuthContext(
        user_id="test-id",
        email="eng@test.com",
        display_name="Eng",
        role=Role.ENGINEER,
    )
    assert ctx.has_permission("runs.create") is True
    assert ctx.has_permission("system.manage_users") is False


def test_auth_context_not_authenticated():
    from src.core.auth import AuthContext
    ctx = AuthContext(
        user_id="test-id",
        email="test@test.com",
        display_name="Test",
        role=Role.ENGINEER,
        is_authenticated=False,
    )
    assert ctx.has_permission("runs.view") is False


# ===========================================================================
# Agent ID validation tests
# ===========================================================================


def test_validate_agent_id_valid():
    from src.core.auth import validate_agent_id
    assert validate_agent_id("specification_engine") == "specification_engine"
    assert validate_agent_id("model-router") == "model-router"
    assert validate_agent_id("test.engine") == "test.engine"


def test_validate_agent_id_none():
    from src.core.auth import validate_agent_id
    assert validate_agent_id(None) is None


def test_validate_agent_id_invalid():
    from src.core.auth import validate_agent_id
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        validate_agent_id("123-invalid")  # starts with number
    with pytest.raises(HTTPException):
        validate_agent_id("")  # empty
    with pytest.raises(HTTPException):
        validate_agent_id("has spaces")  # has spaces


# ===========================================================================
# Secret redaction tests
# ===========================================================================


def test_is_secret_key():
    from src.api.v1.endpoints.settings import _is_secret_key
    assert _is_secret_key("openai_api_key") is True
    assert _is_secret_key("github_token") is True
    assert _is_secret_key("database_password") is True
    assert _is_secret_key("jwt_secret") is True
    assert _is_secret_key("log_level") is False
    assert _is_secret_key("max_retries") is False


def test_redact_value():
    from src.api.v1.endpoints.settings import _redact_value
    assert _redact_value("openai_api_key", "sk-12345") == "***REDACTED***"
    assert _redact_value("log_level", "INFO") == "INFO"
    assert _redact_value("github_token", "ghp_abc") == "***REDACTED***"
    assert _redact_value("max_retries", "3") == "3"
