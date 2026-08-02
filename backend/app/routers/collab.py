"""Comment threads and task assignment on each discrepancy, so co founders
can divide up fixes. This is persistent, not a live multiplayer feed: a
co founder opens the workspace later and sees the same comments and
tasks, the way a shared document works, rather than watching updates
appear in real time while someone else is typing."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/api/discrepancies", tags=["collaboration"])

@router.get("/{discrepancy_id}/comments")
def list_comments(discrepancy_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    comments = db.query(models.Comment).filter(models.Comment.discrepancy_id == discrepancy_id).order_by(models.Comment.created_at).all()
    result = []
    for c in comments:
        author = db.query(models.User).get(c.user_id)
        result.append({"id": c.id, "text": c.text, "user": author.name if author else "Someone", "at": c.created_at})
    return result

@router.post("/{discrepancy_id}/comments")
def add_comment(discrepancy_id: str, payload: schemas.CommentIn, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    disc = db.query(models.Discrepancy).get(discrepancy_id)
    if not disc:
        raise HTTPException(status_code=404, detail="Discrepancy not found")
    comment = models.Comment(discrepancy_id=discrepancy_id, user_id=user.id, text=payload.text)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"id": comment.id, "text": comment.text, "user": user.name}

@router.get("/{discrepancy_id}/tasks")
def list_tasks(discrepancy_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    tasks = db.query(models.Task).filter(models.Task.discrepancy_id == discrepancy_id).order_by(models.Task.created_at).all()
    return [{"id": t.id, "text": t.text, "done": t.done, "assigned_to": t.assigned_to} for t in tasks]

@router.post("/{discrepancy_id}/tasks")
def add_task(discrepancy_id: str, payload: schemas.TaskIn, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    disc = db.query(models.Discrepancy).get(discrepancy_id)
    if not disc:
        raise HTTPException(status_code=404, detail="Discrepancy not found")
    task = models.Task(discrepancy_id=discrepancy_id, text=payload.text, assigned_to=payload.assigned_to)
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"id": task.id, "text": task.text, "done": task.done}

@router.post("/tasks/{task_id}/toggle")
def toggle_task(task_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.done = not task.done
    db.commit()
    return {"id": task.id, "done": task.done}
