"""Settings endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models import SystemSetting

router = APIRouter()


@router.get("/")
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemSetting))
    items = result.scalars().all()
    return {s.key: {"value": s.value, "type": s.value_type, "description": s.description} for s in items}


@router.put("/{key}")
async def update_setting(key: str, value: str, value_type: str = "string", db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = value
        setting.value_type = value_type
    else:
        setting = SystemSetting(key=key, value=value, value_type=value_type)
        db.add(setting)
    await db.flush()
    return {"key": key, "value": value}


@router.delete("/{key}")
async def delete_setting(key: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    await db.delete(setting)
    return {"key": key, "deleted": True}


@router.put("/bulk")
async def bulk_update_settings(settings: dict, db: AsyncSession = Depends(get_db)):
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
