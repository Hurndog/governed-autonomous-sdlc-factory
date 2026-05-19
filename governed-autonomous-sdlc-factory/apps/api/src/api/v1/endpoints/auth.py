"""Authentication endpoints — Security Phase 1."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select, func

from src.core.auth import (
    ALLOW_BOOTSTRAP,
    AuthContext,
    BootstrapRequest,
    CreateUserRequest,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
    Role,
    UpdateUserRequest,
    UserResponse,
    create_access_token,
    get_current_user,
    hash_password,
    require_permission,
    verify_password,
)
from src.core.database import get_db
from src.models import AuditLog, User

router = APIRouter()


# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, request: Request, db=Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        # Audit failed login
        await _audit(db, None, "login.failed", "user", None, {"email": body.email}, request)
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        await _audit(db, user.id, "login.failed_inactive", "user", user.id, {}, request)
        raise HTTPException(status_code=401, detail="Account is deactivated")
    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()
    # Audit successful login
    await _audit(db, user.id, "login.success", "user", user.id, {}, request)
    token = create_access_token(user)
    return LoginResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: AuthContext = Depends(get_current_user)):
    return UserResponse(
        id=user.user_id,
        email=user.email,
        display_name=user.display_name,
        role=user.role.value,
        is_active=True,
    )


@router.post("/bootstrap-admin", include_in_schema=ALLOW_BOOTSTRAP)
async def bootstrap_admin(body: BootstrapRequest, request: Request, db=Depends(get_db)):
    if not ALLOW_BOOTSTRAP:
        raise HTTPException(status_code=404, detail="Not found")
    # Check if any user exists
    result = await db.execute(select(func.count(User.id)))
    count = result.scalar()
    if count and count > 0:
        raise HTTPException(status_code=409, detail="Users already exist — bootstrap disabled")
    user = User(
        email=body.email,
        display_name=body.display_name,
        password_hash=hash_password(body.password),
        role=Role.ADMIN.value,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    await _audit(db, user.id, "bootstrap.admin_created", "user", user.id, {"email": user.email}, request)
    token = create_access_token(user)
    return LoginResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            last_login_at=None,
        ),
    )


# ---------------------------------------------------------------------------
# User management (admin only)
# ---------------------------------------------------------------------------


@router.get("/users", dependencies=[Depends(require_permission("system.manage_users"))])
async def list_users(db=Depends(get_db)):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return {"users": [_user_to_response(u) for u in users]}


@router.post("/users", dependencies=[Depends(require_permission("system.manage_users"))])
async def create_user(body: CreateUserRequest, request: Request, user: AuthContext = Depends(get_current_user), db=Depends(get_db)):
    # Validate role
    try:
        role = Role(body.role)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid role: {body.role}")
    # Check email uniqueness
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    new_user = User(
        email=body.email,
        display_name=body.display_name,
        password_hash=hash_password(body.password),
        role=role.value,
        is_active=True,
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    await _audit(db, user.user_id, "user.created", "user", new_user.id, {"email": new_user.email, "role": new_user.role}, request)
    return _user_to_response(new_user)


@router.get("/users/{user_id}", dependencies=[Depends(require_permission("system.manage_users"))])
async def get_user(user_id: str, db=Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_to_response(u)


@router.patch("/users/{user_id}", dependencies=[Depends(require_permission("system.manage_users"))])
async def update_user(user_id: str, body: UpdateUserRequest, request: Request, user: AuthContext = Depends(get_current_user), db=Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    changes = {}
    if body.display_name is not None:
        changes["display_name"] = {"old": u.display_name, "new": body.display_name}
        u.display_name = body.display_name
    if body.role is not None:
        try:
            role = Role(body.role)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid role: {body.role}")
        changes["role"] = {"old": u.role, "new": role.value}
        u.role = role.value
    if body.is_active is not None:
        changes["is_active"] = {"old": u.is_active, "new": body.is_active}
        u.is_active = body.is_active
    await db.flush()
    await _audit(db, user.user_id, "user.updated", "user", u.id, changes, request)
    return _user_to_response(u)


@router.post("/users/{user_id}/reset-password", dependencies=[Depends(require_permission("system.manage_users"))])
async def reset_password(user_id: str, body: ResetPasswordRequest, request: Request, user: AuthContext = Depends(get_current_user), db=Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.password_hash = hash_password(body.new_password)
    await db.flush()
    await _audit(db, user.user_id, "user.password_reset", "user", u.id, {}, request)
    return {"status": "password_reset"}


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------


@router.get("/audit-log", dependencies=[Depends(require_permission("system.view_audit_log"))])
async def list_audit_log(
    limit: int = 100,
    offset: int = 0,
    action: str | None = None,
    db=Depends(get_db),
):
    query = select(AuditLog).order_by(AuditLog.created_at.desc())
    if action:
        query = query.where(AuditLog.action == action)
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    entries = result.scalars().all()
    return {
        "entries": [
            {
                "id": e.id,
                "user_id": e.user_id,
                "workspace_id": e.workspace_id,
                "project_id": e.project_id,
                "action": e.action,
                "resource_type": e.resource_type,
                "resource_id": e.resource_id,
                "metadata_json": e.metadata_json,
                "ip_address": e.ip_address,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ],
        "limit": limit,
        "offset": offset,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _user_to_response(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "display_name": u.display_name,
        "role": u.role,
        "is_active": u.is_active,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
    }


async def _audit(db, user_id, action, resource_type, resource_id, metadata, request: Request):
    """Write an audit log entry."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=metadata,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(entry)
    await db.flush()
