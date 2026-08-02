from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, get_user_workspace
from app.scoring import compare_versions
from app.search_index import index_document

router = APIRouter(prefix="/api/versions", tags=["versions"])

@router.post("/compare")
def compare(payload: schemas.VersionCompareIn, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ws = get_user_workspace(db, user)
    document = db.query(models.Document).filter(models.Document.id == payload.document_id, models.Document.workspace_id == ws.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    result = compare_versions(document.text, payload.new_text)

    version = models.DocumentVersion(
        document_id=document.id,
        version_number=document.version_number + 1,
        text=payload.new_text,
        diff_summary=result,
    )
    db.add(version)
    document.text = payload.new_text
    document.version_number += 1
    db.commit()

    index_document(db, ws.id, document.id, document.name, document.doc_type, payload.new_text)
    return result

@router.get("/{document_id}/history")
def history(document_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    versions = db.query(models.DocumentVersion).filter(models.DocumentVersion.document_id == document_id).order_by(models.DocumentVersion.version_number).all()
    return [{"version": v.version_number, "diff": v.diff_summary, "at": v.created_at} for v in versions]
