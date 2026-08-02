from sqlalchemy import text
from sqlalchemy.orm import Session

def chunk_text(raw_text: str, chunk_size: int = 900, overlap: int = 150):
    chunks = []
    start = 0
    while start < len(raw_text):
        end = start + chunk_size
        chunks.append(raw_text[start:end])
        start = end - overlap
        if start < 0:
            break
    return [c for c in chunks if c.strip()]

def index_document(db: Session, workspace_id: str, document_id: str,
                    document_name: str, doc_type: str, raw_text: str):
    """Replace any existing chunks for this document with freshly chunked
    text, each with a precomputed search vector."""
    db.execute(
        text("DELETE FROM document_chunks WHERE document_id = :doc_id"),
        {"doc_id": document_id},
    )
    for i, chunk in enumerate(chunk_text(raw_text)):
        db.execute(
            text("""
                INSERT INTO document_chunks
                    (id, workspace_id, document_id, document_name, doc_type,
                     chunk_index, chunk_text, search_vector)
                VALUES
                    (gen_random_uuid()::text, :workspace_id, :document_id,
                     :document_name, :doc_type, :chunk_index, :chunk_text,
                     to_tsvector('english', :chunk_text))
            """),
            {
                "workspace_id": workspace_id, "document_id": document_id,
                "document_name": document_name, "doc_type": doc_type,
                "chunk_index": i, "chunk_text": chunk,
            },
        )
    db.commit()

def delete_document(db: Session, document_id: str):
    db.execute(text("DELETE FROM document_chunks WHERE document_id = :doc_id"), {"doc_id": document_id})
    db.commit()

def retrieve(db: Session, workspace_id: str, query: str, top_k: int = 8):
    rows = db.execute(
        text("""
            SELECT document_name, doc_type, chunk_text,
                   ts_rank(search_vector, plainto_tsquery('english', :query)) AS rank
            FROM document_chunks
            WHERE workspace_id = :workspace_id
              AND search_vector @@ plainto_tsquery('english', :query)
            ORDER BY rank DESC
            LIMIT :top_k
        """),
        {"workspace_id": workspace_id, "query": query, "top_k": top_k},
    ).fetchall()
    if not rows:
        # fall back to the most recent chunks so a query with no exact
        # keyword match still returns something instead of nothing
        rows = db.execute(
            text("""
                SELECT document_name, doc_type, chunk_text, 0 AS rank
                FROM document_chunks
                WHERE workspace_id = :workspace_id
                ORDER BY chunk_index
                LIMIT :top_k
            """),
            {"workspace_id": workspace_id, "top_k": top_k},
        ).fetchall()
    return [{"document_name": r.document_name, "doc_type": r.doc_type, "text": r.chunk_text} for r in rows]

def retrieve_all_grouped(db: Session, workspace_id: str, queries: list[str], top_k_each: int = 6):
    seen = set()
    merged = []
    for q in queries:
        for hit in retrieve(db, workspace_id, q, top_k_each):
            key = (hit["document_name"], hit["text"][:60])
            if key not in seen:
                seen.add(key)
                merged.append(hit)
    return merged
