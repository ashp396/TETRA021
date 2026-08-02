from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, get_user_workspace
from app.search_index import retrieve
from app.llm import chat as llm_chat

router = APIRouter(prefix="/api/chat", tags=["chat"])

SYSTEM = (
    "You are PennyPal, a friendly, plain spoken fundraising assistant inside "
    "Finvestor, an Indian startup readiness tool. Answer only from the given "
    "excerpts and analysis. If they do not say something, say so plainly "
    "instead of guessing. Keep answers short and conversational, two to four "
    "sentences unless asked for more detail. Amounts are in Indian Rupees "
    "unless stated otherwise. If asked about legal or SEBI compliance, answer "
    "only in terms of the general disclosure hygiene checked (private "
    "placement paperwork, valuation support, related party flags) and say "
    "plainly that a company secretary or securities lawyer should confirm "
    "actual compliance, since you are not able to give legal advice."
)

@router.post("/message")
def send_message(payload: schemas.ChatIn, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ws = get_user_workspace(db, user)
    db.add(models.ChatMessage(workspace_id=ws.id, user_id=user.id, role="user", text=payload.message))
    db.commit()

    hits = retrieve(db, ws.id, payload.message, top_k=8)
    context = "\n\n".join(f"[{h['document_name']}] {h['text']}" for h in hits) or "No matching document excerpts were found."

    latest = (
        db.query(models.AnalysisResult)
        .filter(models.AnalysisResult.workspace_id == ws.id)
        .order_by(models.AnalysisResult.created_at.desc())
        .first()
    )
    analysis_summary = f"Composite score: {latest.composite_score}/850. {latest.summary}" if latest else "No readiness check has been run yet."

    prompt = f"Relevant document excerpts:\n{context}\n\nCurrent analysis: {analysis_summary}\n\nQuestion: {payload.message}"
    answer = llm_chat(SYSTEM, prompt, max_tokens=500)

    db.add(models.ChatMessage(workspace_id=ws.id, user_id=user.id, role="assistant", text=answer))
    db.commit()
    return {"answer": answer}

@router.get("/history")
def history(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ws = get_user_workspace(db, user)
    msgs = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.workspace_id == ws.id)
        .order_by(models.ChatMessage.created_at.asc())
        .all()
    )
    return [{"role": m.role, "text": m.text, "at": m.created_at} for m in msgs]
