import uuid
from datetime import datetime
from sqlalchemy import (Column, String, Text, Float, Boolean, ForeignKey,
                         DateTime, Integer, JSON)
from sqlalchemy.orm import relationship
from app.database import Base

def uid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=uid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    startup_stage = Column(String, default="Seed")
    created_at = Column(DateTime, default=datetime.utcnow)
    workspaces = relationship("Workspace", back_populates="owner")

class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(String, primary_key=True, default=uid)
    name = Column(String, default="Fundraising round")
    owner_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User", back_populates="workspaces")
    documents = relationship("Document", back_populates="workspace")
    members = relationship("WorkspaceMember", back_populates="workspace")

class WorkspaceMember(Base):
    # lets more than one founder collaborate in the same workspace
    __tablename__ = "workspace_members"
    id = Column(String, primary_key=True, default=uid)
    workspace_id = Column(String, ForeignKey("workspaces.id"))
    user_id = Column(String, ForeignKey("users.id"))
    role = Column(String, default="editor")
    workspace = relationship("Workspace", back_populates="members")

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=uid)
    workspace_id = Column(String, ForeignKey("workspaces.id"))
    name = Column(String)
    doc_type = Column(String)
    text = Column(Text)
    version_number = Column(Integer, default=1)
    uploaded_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    workspace = relationship("Workspace", back_populates="documents")

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    id = Column(String, primary_key=True, default=uid)
    document_id = Column(String, ForeignKey("documents.id"))
    version_number = Column(Integer)
    text = Column(Text)
    diff_summary = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(String, primary_key=True, default=uid)
    workspace_id = Column(String, ForeignKey("workspaces.id"))
    composite_score = Column(Integer)
    category_scores = Column(JSON, default=dict)
    category_notes = Column(JSON, default=dict)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    discrepancies = relationship("Discrepancy", back_populates="analysis")
    follow_ups = relationship("FollowUpQuestion", back_populates="analysis")

class Discrepancy(Base):
    __tablename__ = "discrepancies"
    id = Column(String, primary_key=True, default=uid)
    analysis_id = Column(String, ForeignKey("analysis_results.id"))
    title = Column(String)
    category = Column(String)
    classification = Column(String)  # verified mismatch | unresolved inconsistency | missing information
    description = Column(Text)
    sources = Column(JSON, default=list)
    severity = Column(String, default="medium")
    analysis = relationship("AnalysisResult", back_populates="discrepancies")
    comments = relationship("Comment", back_populates="discrepancy")
    tasks = relationship("Task", back_populates="discrepancy")

class FollowUpQuestion(Base):
    __tablename__ = "follow_up_questions"
    id = Column(String, primary_key=True, default=uid)
    analysis_id = Column(String, ForeignKey("analysis_results.id"))
    question = Column(Text)
    analysis = relationship("AnalysisResult", back_populates="follow_ups")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(String, primary_key=True, default=uid)
    discrepancy_id = Column(String, ForeignKey("discrepancies.id"))
    user_id = Column(String, ForeignKey("users.id"))
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    discrepancy = relationship("Discrepancy", back_populates="comments")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=uid)
    discrepancy_id = Column(String, ForeignKey("discrepancies.id"))
    text = Column(Text)
    done = Column(Boolean, default=False)
    assigned_to = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    discrepancy = relationship("Discrepancy", back_populates="tasks")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, default=uid)
    workspace_id = Column(String, ForeignKey("workspaces.id"))
    user_id = Column(String, nullable=True)
    role = Column(String)  # user | assistant
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class DocumentChunk(Base):
    """Retrieval table used instead of a separate vector database. A
    Postgres tsvector column (search_vector) is populated at insert time
    by app.search_index, and queried with plainto_tsquery ranking."""
    __tablename__ = "document_chunks"
    id = Column(String, primary_key=True, default=uid)
    workspace_id = Column(String, index=True)
    document_id = Column(String, index=True)
    document_name = Column(String)
    doc_type = Column(String)
    chunk_index = Column(Integer)
    chunk_text = Column(Text)
    # search_vector is a Postgres TSVECTOR, created and populated via raw
    # SQL in search_index.py / init_db.sql rather than the ORM, since
    # SQLAlchemy's core column types do not model tsvector directly.

