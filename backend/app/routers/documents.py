from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, get_user_workspace
from app.parsing import extract_text
from app.search_index import index_document, delete_document

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("", response_model=List[schemas.DocumentOut])
def list_documents(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ws = get_user_workspace(db, user)
    return db.query(models.Document).filter(models.Document.workspace_id == ws.id).all()

@router.post("/upload", response_model=schemas.DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    ws = get_user_workspace(db, user)
    raw = await file.read()
    text = extract_text(file.filename, raw)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text was found in this file")
    document = models.Document(
        workspace_id=ws.id, name=file.filename, doc_type=doc_type,
        text=text, version_number=1, uploaded_by=user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    index_document(db, ws.id, document.id, document.name, document.doc_type, text)
    return document

@router.post("/paste", response_model=schemas.DocumentOut)
def paste_document(
    name: str = Form(...),
    doc_type: str = Form(...),
    text: str = Form(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    ws = get_user_workspace(db, user)
    document = models.Document(
        workspace_id=ws.id, name=name, doc_type=doc_type,
        text=text, version_number=1, uploaded_by=user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    index_document(db, ws.id, document.id, document.name, document.doc_type, text)
    return document

@router.delete("/{document_id}")
def remove_document(document_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ws = get_user_workspace(db, user)
    doc = db.query(models.Document).filter(models.Document.id == document_id, models.Document.workspace_id == ws.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    delete_document(db, doc.id)
    db.delete(doc)
    db.commit()
    return {"ok": True}
