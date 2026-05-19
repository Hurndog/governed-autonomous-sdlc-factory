"""Authentication and authorization module — Security Phase 1."""
from __future__ import annotations

import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from src.core.database import get_db
from src.models import User

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))
ALLOW_BOOTSTRAP = os.getenv("ALLOW_BOOTSTRAP", "false").lower() == "true"

# ---------------------------------------------------------------------------
# Roles & Permissions
# ---------------------------------------------------------------------------


class Role(str, Enum):
    ADMIN = "admin"
    ARCHITECT = "architect"
    ENGINEER = "engineer"
    GOVERNANCE_REVIEWER = "governance_reviewer"
    EXECUTIVE_VIEWER = "executive_viewer"
    AUDITOR = "auditor"
    OPERATOR = "operator"


# Permission definitions
PERMISSIONS = {
    # System
    "system.manage_users": {Role.ADMIN},
    "system.manage_settings": {Role.ADMIN},
    "system.view_health": {Role.ADMIN, Role.ARCHITECT, Role.ENGINEER, Role.GOVERNANCE_REVIEWER, Role.EXECUTIVE_VIEWER, Role.AUDITOR, Role.OPERATOR},
    "system.view_audit_log": {Role.ADMIN, Role.AUDITOR},
    # Runs
    "runs.create": {Role.ADMIN, Role.ARCHITECT, Role.ENGINEER},
    "runs.view": {Role.ADMIN, Role.ARCHITECT, Role.ENGINEER, Role.GOVERNANCE_REVIEWER, Role.EXECUTIVE_VIEWER, Role.AUDITOR, Role.OPERATOR},
    "runs.control": {Role.ADMIN, Role.ENGINEER, Role.OPERATOR},
    # Artifacts
    "artifacts.view": {Role.ADMIN, Role.ARCHITECT, Role.ENGINEER, Role.GOVERNANCE_REVIEWER, Role.AUDITOR},
    "artifacts.edit": {Role.ADMIN, Role.ARCHITECT, Role.ENGINEER},
    # Evidence
    "evidence.view": {Role.ADMIN, Role.ARCHITECT, Role.ENGINEER, Role.GOVERNANCE_REVIEWER, Role.AUDITOR},
    "evidence.export": {Role.ADMIN, Role.ARCHITECT, Role.GOVERNANCE_REVIEWER, Role.AUDITOR},
    # Governance
    "governance.view": {Role.ADMIN, Role.ARCHITECT, Role.ENGINEER, Role.GOVERNANCE_REVIEWER, Role.EXECUTIVE_VIEWER, Role.AUDITOR},
    "governance.approve": {Role.ADMIN, Role.GOVERNANCE_REVIEWER},
    # Integrity
    "integrity.verify": {Role.ADMIN, Role.ARCHITECT, Role.ENGINEER, Role.GOVERNANCE_REVIEWER, Role.AUDITOR},
    # Tokenomics
    "tokenomics.view": {Role.ADMIN, Role.ARCHITECT, Role.ENGINEER, Role.EXECUTIVE_VIEWER},
    # Logs
    "logs.view": {Role.ADMIN, Role.ARCHITECT, Role.ENGINEER, Role.GOVERNANCE_REVIEWER, Role.AUDITOR, Role.OPERATOR},
    "logs.view_sensitive": {Role.ADMIN},
    # Settings
    "settings.view": {Role.ADMIN},
    "settings.edit": {Role.ADMIN},
    # Providers
    "providers.view": {Role.ADMIN, Role.ARCHITECT, Role.ENGINEER, Role.OPERATOR},
    "providers.edit": {Role.ADMIN},
    # Workspaces / Projects
    "workspaces.manage": {Role.ADMIN},
    "projects.manage": {Role.ADMIN, Role.ARCHITECT},
}


def role_has_permission(role: Role, permission: str) -> bool:
    """Check whether *role* has *permission*."""
    if permission == "*":
        return role == Role.ADMIN
    allowed = PERMISSIONS.get(permission, set())
    return role in allowed


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class AuthContext(BaseModel):
    user_id: str
    email: str
    display_name: str
    role: Role
    is_authenticated: bool = True

    def has_permission(self, permission: str) -> bool:
        if not self.is_authenticated:
            return False
        return role_has_permission(self.role, permission)


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    role: str
    is_active: bool
    created_at: Optional[str] = None
    last_login_at: Optional[str] = None


class CreateUserRequest(BaseModel):
    email: str
    display_name: str
    password: str
    role: str = "engineer"


class UpdateUserRequest(BaseModel):
    display_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class ResetPasswordRequest(BaseModel):
    new_password: str


class BootstrapRequest(BaseModel):
    email: str
    password: str
    display_name: str = "Admin"


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(_BCRYPT_ROUNDS)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except Exception:
        return False


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------


def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role,
        "iat": now,
        "exp": now + timedelta(hours=JWT_EXPIRY_HOURS),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    db=Depends(get_db),
) -> AuthContext:
    """Dependency that extracts and validates the current user from JWT."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    # Load user from DB to verify still active
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return AuthContext(
        user_id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=Role(user.role),
        is_authenticated=True,
    )


def require_permission(permission: str):
    """Factory for a dependency that enforces *permission* on an endpoint."""

    async def _checker(user: AuthContext = Depends(get_current_user)) -> AuthContext:
        if not user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {permission} required",
            )
        return user

    return _checker


# ---------------------------------------------------------------------------
# Agent-ID validation (reused from costs endpoint)
# ---------------------------------------------------------------------------

_AGENT_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_.\-]{0,127}$")


def validate_agent_id(agent_id: Optional[str]) -> Optional[str]:
    if agent_id is None:
        return None
    if not _AGENT_ID_RE.match(agent_id):
        raise HTTPException(
            status_code=422,
            detail="agent_id must start with a letter and contain only alphanumeric characters, underscores, dots, or hyphens (max 128 chars)",
        )
    return agent_id


# ---------------------------------------------------------------------------
# Backward-compatible alias (deprecated — use get_current_user instead)
# ---------------------------------------------------------------------------

def get_current_auth() -> AuthContext:
    """Deprecated: use get_current_user dependency instead."""
    return AuthContext(
        user_id="local-admin",
        email="local@admin",
        display_name="Local Admin",
        role=Role.ADMIN,
        is_authenticated=True,
    )
