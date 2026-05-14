"""Authentication stub and role models."""
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class Role(str, Enum):
    ADMIN = "admin"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    GOVERNANCE_REVIEWER = "governance_reviewer"
    VIEWER = "viewer"


ROLE_PERMISSIONS = {
    Role.ADMIN: ["*"],
    Role.ARCHITECT: ["projects.*", "runs.*", "architecture.*", "evidence.*", "patterns.*"],
    Role.DEVELOPER: ["projects.read", "runs.*", "artifacts.*", "tasks.*", "test.*"],
    Role.REVIEWER: ["projects.read", "runs.read", "artifacts.read", "approvals.*"],
    Role.GOVERNANCE_REVIEWER: ["projects.read", "runs.read", "governance.*", "approvals.*"],
    Role.VIEWER: ["projects.read", "runs.read", "artifacts.read", "evidence.read"],
}


class AuthContext(BaseModel):
    user_id: str = "local-admin"
    role: Role = Role.ADMIN
    is_authenticated: bool = True

    def has_permission(self, resource: str) -> bool:
        permissions = ROLE_PERMISSIONS.get(self.role, [])
        if "*" in permissions:
            return True
        return resource in permissions


# Local auth context — always admin in local mode
local_auth = AuthContext()


def get_current_auth() -> AuthContext:
    """Return the current authentication context. In local mode, always returns admin."""
    return local_auth
