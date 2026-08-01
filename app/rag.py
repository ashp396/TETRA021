"""
Retrieval Augmented Generation engine
"""

import os
import re
from typing import List, Dict, Optional

import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "storage/chroma_db"
os.makedirs(CHROMA_PATH, exist_ok=True)

_client = chromadb.PersistentClient(path=CHROMA_PATH)
_embedder = embedding_functions.DefaultEmbeddingFunction()


def _collection_name(run_id: int) -> str:
    return f"run_{run_id}"


def get_collection(run_id: int):
    return _client.get_or_create_collection(
        name=_collection_name(run_id), embedding_function=_embedder
    )


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    """Fixed size chunking with overlap. Simple on purpose: financial
    documents are short enough that sentence or table aware chunking is
    not needed for this to retrieve well."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    step = max(chunk_size - overlap, 1)
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += step
    return [c for c in chunks if c.strip()]


def index_document(run_id: int, doc_type: str, document_id: int, filename: str, text: str) -> int:
    """Chunks a parsed document and stores it in this run's collection.
    Returns the number of chunks stored, 0 if the document had no text."""
    chunks = chunk_text(text)
    if not chunks:
        return 0
    collection = get_collection(run_id)
    ids = [f"{doc_type}_{document_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {"doc_type": doc_type, "document_id": document_id, "filename": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]
    collection.add(ids=ids, documents=chunks, metadatas=metadatas)
    return len(chunks)


def retrieve(run_id: int, query: str, doc_types: Optional[List[str]] = None, k: int = 5) -> List[Dict]:
    collection = get_collection(run_id)
    if collection.count() == 0:
        return []
    where = {"doc_type": {"$in": doc_types}} if doc_types else None
    result = collection.query(query_texts=[query], n_results=min(k, collection.count()), where=where)
    hits = []
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    for doc, meta in zip(docs, metas):
        hits.append({"text": doc, "doc_type": meta.get("doc_type"), "filename": meta.get("filename")})
    return hits


def delete_run(run_id: int) -> None:
    try:
        _client.delete_collection(_collection_name(run_id))
    except Exception:
        pass
