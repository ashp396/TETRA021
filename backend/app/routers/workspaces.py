from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app import models
from app.deps import get_current_user, get_user_workspace, get_accessible_workspaces

router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])

class InviteIn(BaseModel):
    email: EmailStr

@router.get("")
def list_workspaces(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    get_user_workspace(db, user)  # make sure the owned one exists
    workspaces = get_accessible_workspaces(db, user)
    return [
        {"id": w.id, "name": w.name, "isOwner": w.owner_id == user.id}
        for w in workspaces
    ]

@router.post("/invite")
def invite_cofounder(payload: InviteIn, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Gives a co-founder persistent access to the same workspace. This is
    not a live multiplayer session: whoever is invited can log in at any
    time afterwards and see the same documents, score, and discrepancy
    comments, the way a shared drive folder works rather than a video call."""
    ws = get_user_workspace(db, user)
    invitee = db.query(models.User).filter(models.User.email == payload.email).first()
    if not invitee:
        raise HTTPException(status_code=404, detail="No Finvestor account with that email yet. Ask your co founder to sign up first, then invite them.")
    if invitee.id == user.id:
        raise HTTPException(status_code=400, detail="That is your own account")
    existing = db.query(models.WorkspaceMember).filter(
        models.WorkspaceMember.workspace_id == ws.id,
        models.WorkspaceMember.user_id == invitee.id,
    ).first()
    if existing:
        return {"ok": True, "message": f"{invitee.name} already has access"}
    db.add(models.WorkspaceMember(workspace_id=ws.id, user_id=invitee.id, role="editor"))
    db.commit()
    return {"ok": True, "message": f"{invitee.name} can now access this workspace"}

@router.get("/members")
def list_members(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ws = get_user_workspace(db, user)
    members = db.query(models.WorkspaceMember).filter(models.WorkspaceMember.workspace_id == ws.id).all()
    result = [{"name": ws.owner.name, "email": ws.owner.email, "role": "owner"}]
    for m in members:
        u = db.query(models.User).get(m.user_id)
        if u:
            result.append({"name": u.name, "email": u.email, "role": m.role})
    return result
