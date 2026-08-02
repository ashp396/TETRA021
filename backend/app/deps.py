from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import decode_access_token
from app import models

bearer_scheme = HTTPBearer()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    user_id = decode_access_token(creds.credentials)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired, please log in again")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def get_user_workspace(db: Session, user: models.User) -> models.Workspace:
    """The workspace this user owns. Every user gets exactly one on
    signup; co-founders are added to it as members instead of getting a
    second workspace, so the whole team looks at the same documents."""
    ws = db.query(models.Workspace).filter(models.Workspace.owner_id == user.id).first()
    if not ws:
        ws = models.Workspace(name=f"{user.name}'s fundraising round", owner_id=user.id)
        db.add(ws)
        db.commit()
        db.refresh(ws)
    return ws

def get_accessible_workspaces(db: Session, user: models.User) -> list[models.Workspace]:
    """Workspaces this user can see: the one they own, plus any they were
    invited into as a co-founder. Access is persistent, not a live
    session, so a co-founder can open Finvestor any time and see the same
    documents, score, and discrepancy threads without needing to be
    online at the same moment as anyone else."""
    owned = db.query(models.Workspace).filter(models.Workspace.owner_id == user.id).all()
    member_ws_ids = [m.workspace_id for m in db.query(models.WorkspaceMember).filter(models.WorkspaceMember.user_id == user.id).all()]
    invited = db.query(models.Workspace).filter(models.Workspace.id.in_(member_ws_ids)).all() if member_ws_ids else []
    seen = {}
    for ws in owned + invited:
        seen[ws.id] = ws
    return list(seen.values())

def get_workspace_or_403(db: Session, user: models.User, workspace_id: str) -> models.Workspace:
    ws = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    is_owner = ws.owner_id == user.id
    is_member = db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.workspace_id == workspace_id,
        models.WorkspaceMember.user_id == user.id,
    ).first() is not None
    if not (is_owner or is_member):
        raise HTTPException(status_code=403, detail="You do not have access to this workspace")
    return ws
