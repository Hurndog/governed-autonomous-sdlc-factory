"""Settings endpoints — with auth and secret redaction."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import AuthContext, Role, get_current_user, require_permission
from src.core.database import get_db
from src.models import SystemSetting

router = APIRouter()

# Keys that contain secrets and should be redacted
_SECRET_KEY_PATTERNS = [
    "api_key", "apikey", "secret", "token", "password", "private_key",
    "access_key", "auth_key", "bearer", "credential",
]


def _is_secret_key(key: str) -> bool:
    kl = key.lower()
    return any(pat in kl for pat in _SECRET_KEY_PATTERNS)


def _redact_value(key: str, value: str) -> str:
    if _is_secret_key(key) and value:
        return "***REDACTED***"
    return value


@router.get("/", dependencies=[Depends(require_permission("settings.view"))])
async def get_settings(user: AuthContext = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemSetting))
    items = result.scalars().all()
    settings = {}
    for s in items:
        settings[s.key] = {
            "value": _redact_value(s.key, s.value) if s.value else s.value,
            "type": s.value_type,
            "description": s.description,
            "is_secret": _is_secret_key(s.key),
        }
    return {"settings": settings}


@router.put("/{key}", dependencies=[Depends(require_permission("settings.edit"))])
async def update_setting(key: str, value: str, value_type: str = "string", user: AuthContext = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = value
        setting.value_type = value_type
    else:
        setting = SystemSetting(key=key, value=value, value_type=value_type)
        db.add(setting)
    await db.flush()
    return {"key": key, "value": _redact_value(key, value)}


@router.delete("/{key}", dependencies=[Depends(require_permission("settings.edit"))])
async def delete_setting(key: str, user: AuthContext = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    await db.delete(setting)
    return {"key": key, "deleted": True}


@router.put("/bulk", dependencies=[Depends(require_permission("settings.edit"))])
async def bulk_update_settings(settings: dict, user: AuthContext = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    updated = []
    for key, value in settings.items():
        result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = str(value)
        else:
            setting = SystemSetting(key=key, value=str(value))
            db.add(setting)
        updated.append(key)
    await db.flush()
    return {"updated": updated, "count": len(updated)}
