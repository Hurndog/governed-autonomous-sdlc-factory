"""Workspace and project access endpoints — Security Phase 1."""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from typing import Optional

from src.core.auth import (
    AuthContext,
    Role,
    get_current_user,
    require_permission,
)
from src.core.database import get_db
from src.models import AuditLog, Project, Workspace, WorkspaceMembership

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class CreateWorkspaceRequest(BaseModel):
    name: str
    description: Optional[str] = None


class UpdateWorkspaceRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class AddMemberRequest(BaseModel):
    user_id: str
    role: str = "engineer"


# ---------------------------------------------------------------------------
# Workspace endpoints
# ---------------------------------------------------------------------------


@router.get("/workspaces")
async def list_workspaces(user: AuthContext = Depends(get_current_user), db=Depends(get_db)):
    """List workspaces the user has access to."""
    if user.has_permission("workspaces.manage"):
        # Admin sees all workspaces
        result = await db.execute(select(Workspace).order_by(Workspace.created_at.desc()))
    else:
        # Non-admin: only workspaces they're a member of
        result = await db.execute(
            select(Workspace)
            .join(WorkspaceMembership, Workspace.id == WorkspaceMembership.workspace_id)
            .where(WorkspaceMembership.user_id == user.user_id)
            .order_by(Workspace.created_at.desc())
        )
    workspaces = result.scalars().all()
    return {"workspaces": [_ws_to_dict(w) for w in workspaces]}


@router.post("/workspaces", dependencies=[Depends(require_permission("workspaces.manage"))])
async def create_workspace(body: CreateWorkspaceRequest, request: Request, user: AuthContext = Depends(get_current_user), db=Depends(get_db)):
    ws = Workspace(
        name=body.name,
        description=body.description,
        created_by_user_id=user.user_id,
    )
    db.add(ws)
    await db.flush()
    await db.refresh(ws)
    # Add creator as admin member
    membership = WorkspaceMembership(
        workspace_id=ws.id,
        user_id=user.user_id,
        role=Role.ADMIN.value,
    )
    db.add(membership)
    await db.flush()
    await _audit(db, user.user_id, "workspace.created", "workspace", ws.id, {"name": ws.name}, request)
    return _ws_to_dict(ws)


@router.get("/workspaces/{workspace_id}")
async def get_workspace(workspace_id: str, user: AuthContext = Depends(get_current_user), db=Depends(get_db)):
    ws = await _get_workspace_or_404(db, workspace_id)
    await _check_workspace_access(db, user, workspace_id)
    return _ws_to_dict(ws)


@router.patch("/workspaces/{workspace_id}", dependencies=[Depends(require_permission("workspaces.manage"))])
async def update_workspace(workspace_id: str, body: UpdateWorkspaceRequest, request: Request, user: AuthContext = Depends(get_current_user), db=Depends(get_db)):
    ws = await _get_workspace_or_404(db, workspace_id)
    if body.name is not None:
        ws.name = body.name
    if body.description is not None:
        ws.description = body.description
    await db.flush()
    await _audit(db, user.user_id, "workspace.updated", "workspace", ws.id, {}, request)
    return _ws_to_dict(ws)


# ---------------------------------------------------------------------------
# Workspace membership
# ---------------------------------------------------------------------------


@router.post("/workspaces/{workspace_id}/members", dependencies=[Depends(require_permission("workspaces.manage"))])
async def add_workspace_member(workspace_id: str, body: AddMemberRequest, request: Request, user: AuthContext = Depends(get_current_user), db=Depends(get_db)):
    ws = await _get_workspace_or_404(db, workspace_id)
    # Check if already a member
    result = await db.execute(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == body.user_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="User is already a member")
    membership = WorkspaceMembership(
        workspace_id=workspace_id,
        user_id=body.user_id,
        role=body.role,
    )
    db.add(membership)
    await db.flush()
    await _audit(db, user.user_id, "workspace.member_added", "workspace", workspace_id, {"member_user_id": body.user_id, "role": body.role}, request)
    return {"status": "member_added"}


@router.delete("/workspaces/{workspace_id}/members/{member_user_id}", dependencies=[Depends(require_permission("workspaces.manage"))])
async def remove_workspace_member(workspace_id: str, member_user_id: str, request: Request, user: AuthContext = Depends(get_current_user), db=Depends(get_db)):
    await _get_workspace_or_404(db, workspace_id)
    result = await db.execute(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == member_user_id,
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    await db.delete(membership)
    await db.flush()
    await _audit(db, user.user_id, "workspace.member_removed", "workspace", workspace_id, {"member_user_id": member_user_id}, request)
    return {"status": "member_removed"}


# ---------------------------------------------------------------------------
# Project endpoints (scoped by workspace)
# ---------------------------------------------------------------------------


@router.get("/projects")
async def list_projects(workspace_id: str | None = None, user: AuthContext = Depends(get_current_user), db=Depends(get_db)):
    query = select(Project)
    if workspace_id:
        await _check_workspace_access(db, user, workspace_id)
        query = query.where(Project.workspace_id == workspace_id)
    elif not user.has_permission("workspaces.manage"):
        # Non-admin without workspace filter: only projects in their workspaces
        result = await db.execute(
            select(WorkspaceMembership.workspace_id).where(WorkspaceMembership.user_id == user.user_id)
        )
        ws_ids = [r[0] for r in result.all()]
        query = query.where(Project.workspace_id.in_(ws_ids))
    query = query.order_by(Project.created_at.desc())
    result = await db.execute(query)
    projects = result.scalars().all()
    return {"projects": [_proj_to_dict(p) for p in projects]}


@router.get("/projects/{project_id}")
async def get_project(project_id: str, user: AuthContext = Depends(get_current_user), db=Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    proj = result.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    if proj.workspace_id:
        await _check_workspace_access(db, user, proj.workspace_id)
    elif not user.has_permission("workspaces.manage"):
        raise HTTPException(status_code=403, detail="Access denied")
    return _proj_to_dict(proj)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_workspace_or_404(db, workspace_id: str) -> Workspace:
    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws


async def _check_workspace_access(db, user: AuthContext, workspace_id: str):
    if user.has_permission("workspaces.manage"):
        return  # Admin has access to all
    result = await db.execute(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user.user_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied to this workspace")


def _ws_to_dict(w: Workspace) -> dict:
    return {
        "id": w.id,
        "name": w.name,
        "description": w.description,
        "created_by_user_id": w.created_by_user_id,
        "created_at": w.created_at.isoformat() if w.created_at else None,
        "updated_at": w.updated_at.isoformat() if w.updated_at else None,
    }


def _proj_to_dict(p: Project) -> dict:
    return {
        "id": p.id,
        "workspace_id": p.workspace_id,
        "name": p.name,
        "slug": p.slug,
        "description": p.description,
        "status": p.status,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


async def _audit(db, user_id, action, resource_type, resource_id, metadata, request: Request):
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
