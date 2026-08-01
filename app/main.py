from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.routers import auth, documents, analysis, report, voice

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finvestor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(analysis.router)
app.include_router(report.router)
app.include_router(voice.router)


@app.get("/health")
def health():
    return {"status": "ok"}
