from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine, prepare_search_extensions
from app.routers import auth, documents, analysis, collab, chat, voice, versions, report, workspaces

app = FastAPI(title="Finvestor API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    prepare_search_extensions()

app.include_router(auth.router)
app.include_router(workspaces.router)
app.include_router(documents.router)
app.include_router(analysis.router)
app.include_router(collab.router)
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(versions.router)
app.include_router(report.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}
