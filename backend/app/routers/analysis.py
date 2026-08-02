from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, get_user_workspace
from app.scoring import run_full_analysis, STAGE_BENCHMARKS, REGULATORY_DISCLAIMER

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

def _serialize(analysis: models.AnalysisResult) -> dict:
    return {
        "id": analysis.id,
        "composite_score": analysis.composite_score,
        "category_scores": analysis.category_scores,
        "category_notes": analysis.category_notes,
        "summary": analysis.summary,
        "created_at": analysis.created_at,
        "discrepancies": [schemas.DiscrepancyOut.model_validate(d).model_dump() for d in analysis.discrepancies],
        "follow_ups": [f.question for f in analysis.follow_ups],
        "regulatory_disclaimer": REGULATORY_DISCLAIMER,
    }

@router.post("/run")
def run_analysis(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ws = get_user_workspace(db, user)
    docs = db.query(models.Document).filter(models.Document.workspace_id == ws.id).all()
    if len(docs) < 2:
        raise HTTPException(status_code=400, detail="Add at least two documents before running a readiness check")

    doc_names = [d.name for d in docs]
    result = run_full_analysis(db, ws.id, doc_names)

    analysis = models.AnalysisResult(
        workspace_id=ws.id,
        composite_score=result["compositeScore"],
        category_scores=result.get("categoryScores", {}),
        category_notes=result.get("categoryNotes", {}),
        summary=result.get("summary", ""),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    for d in result.get("discrepancies", []):
        db.add(models.Discrepancy(
            analysis_id=analysis.id, title=d.get("title", ""), category=d.get("category", ""),
            classification=d.get("classification", "unresolved inconsistency"),
            description=d.get("description", ""), sources=d.get("sources", []),
            severity=d.get("severity", "medium"),
        ))
    for q in result.get("followUpQuestions", []):
        db.add(models.FollowUpQuestion(analysis_id=analysis.id, question=q))
    db.commit()
    db.refresh(analysis)
    return _serialize(analysis)

@router.get("/latest")
def latest_analysis(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ws = get_user_workspace(db, user)
    analysis = (
        db.query(models.AnalysisResult)
        .filter(models.AnalysisResult.workspace_id == ws.id)
        .order_by(models.AnalysisResult.created_at.desc())
        .first()
    )
    if not analysis:
        return None
    return _serialize(analysis)

@router.get("/benchmarks")
def benchmarks():
    return STAGE_BENCHMARKS
