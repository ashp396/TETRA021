from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, get_user_workspace
from app.report import build_report_pdf

router = APIRouter(prefix="/api/report", tags=["report"])

@router.get("/pdf")
def download_report(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ws = get_user_workspace(db, user)
    analysis = (
        db.query(models.AnalysisResult)
        .filter(models.AnalysisResult.workspace_id == ws.id)
        .order_by(models.AnalysisResult.created_at.desc())
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=400, detail="Run a readiness check before exporting a report")
    docs = db.query(models.Document).filter(models.Document.workspace_id == ws.id).all()
    analysis_dict = {
        "compositeScore": analysis.composite_score,
        "categoryScores": analysis.category_scores,
        "categoryNotes": analysis.category_notes,
        "summary": analysis.summary,
        "discrepancies": [schemas.DiscrepancyOut.model_validate(d).model_dump() for d in analysis.discrepancies],
        "followUpQuestions": [f.question for f in analysis.follow_ups],
    }
    doc_dicts = [{"name": d.name, "doc_type": d.doc_type} for d in docs]
    pdf_bytes = build_report_pdf(ws.name, analysis_dict, doc_dicts)
    return Response(content=pdf_bytes, media_type="application/pdf",
                     headers={"Content-Disposition": "attachment; filename=finvestor_readiness_report.pdf"})
