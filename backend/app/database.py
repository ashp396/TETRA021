from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def prepare_search_extensions():
    """Runs once at startup, after Base.metadata.create_all. Adds the
    tsvector column and its GIN index to document_chunks (SQLAlchemy's
    ORM does not model TSVECTOR directly, so this is done in raw SQL),
    and makes sure gen_random_uuid() is available for chunk ids."""
    with engine.connect() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS pgcrypto'))
        conn.execute(text(
            "ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS search_vector tsvector"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS document_chunks_search_idx "
            "ON document_chunks USING GIN (search_vector)"
        ))
        conn.commit()
