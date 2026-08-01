from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    runs = relationship("AnalysisRun", back_populates="owner")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("analysis_runs.id"))
    doc_type = Column(String, nullable=False)   # pitch, financials, mis, projections, captable
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=True)
    extracted_metrics = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("AnalysisRun", back_populates="documents")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    company_name = Column(String, nullable=False)
    status = Column(String, default="pending")   # pending, processing, complete, failed
    readiness_score = Column(Integer, nullable=True)
    category_scores = Column(JSON, nullable=True)
    findings = Column(JSON, nullable=True)
    questions = Column(JSON, nullable=True)
    summary_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="runs")
    documents = relationship("Document", back_populates="run")
