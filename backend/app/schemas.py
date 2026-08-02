from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr

class SignupIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    startup_stage: str = "Seed"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    startup_stage: str
    class Config:
        from_attributes = True

class WorkspaceOut(BaseModel):
    id: str
    name: str
    created_at: datetime
    class Config:
        from_attributes = True

class DocumentOut(BaseModel):
    id: str
    name: str
    doc_type: str
    version_number: int
    created_at: datetime
    class Config:
        from_attributes = True

class DiscrepancyOut(BaseModel):
    id: str
    title: str
    category: str
    classification: str
    description: str
    sources: List[str]
    severity: str
    class Config:
        from_attributes = True

class AnalysisOut(BaseModel):
    id: str
    composite_score: int
    category_scores: Dict[str, Any]
    category_notes: Dict[str, Any]
    summary: str
    created_at: datetime
    discrepancies: List[DiscrepancyOut]
    follow_ups: List[str]

class CommentIn(BaseModel):
    text: str

class TaskIn(BaseModel):
    text: str
    assigned_to: Optional[str] = None

class ChatIn(BaseModel):
    message: str

class VersionCompareIn(BaseModel):
    document_id: str
    new_text: str
