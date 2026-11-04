"""Database and vector storage manager for ScrapLedger.

Supports PostgreSQL with pgvector when DATABASE_URL is configured,
with an in-memory cosine store fallback for offline/CI execution.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from app.embeddings import cosine_similarity

logger = logging.getLogger(__name__)

# Global in-memory vector store for offline/local execution
_IN_MEMORY_CHUNKS: list[dict[str, Any]] = []

CREATE_TABLES_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS epr_obligations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    producer_name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    product_category VARCHAR(100) NOT NULL,
    financial_year VARCHAR(10) NOT NULL,
    target_quantity_kg NUMERIC(12, 2) NOT NULL,
    filed_quantity_kg NUMERIC(12, 2) DEFAULT 0.00,
    applicable_form VARCHAR(50) NOT NULL,
    filing_deadline DATE NOT NULL,
    rule_citation VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_name VARCHAR(255) NOT NULL,
    section_heading VARCHAR(255),
    page_number INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    embedding vector(768) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS llm_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint VARCHAR(50) NOT NULL,
    model_used VARCHAR(100) NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    cost_usd NUMERIC(10, 6) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
"""


def is_postgres_available() -> bool:
    """Check if DATABASE_URL is set and starts with postgres."""
    db_url = os.getenv("DATABASE_URL", "")
    return bool(db_url and db_url.startswith(("postgresql://", "postgres://")))


def init_db() -> bool:
    """Initialize PostgreSQL database schema if available."""
    if not is_postgres_available():
        logger.info("No DATABASE_URL configured; using in-memory vector store.")
        return False

    try:
        import psycopg2

        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLES_SQL)
        conn.commit()
        conn.close()
        logger.info("PostgreSQL pgvector tables successfully initialized.")
        return True
    except Exception as e:
        logger.warning("Failed connecting to PostgreSQL (%s); falling back to in-memory store.", e)
        return False


def insert_chunks(chunks: list[dict[str, Any]]) -> int:
    """Insert chunks with dense embeddings into storage (pgvector or in-memory)."""
    global _IN_MEMORY_CHUNKS

    if not chunks:
        return 0

    inserted_count = 0

    # Try PostgreSQL first if available
    if is_postgres_available():
        try:
            import psycopg2
            from psycopg2.extras import execute_values

            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            with conn.cursor() as cur:
                query = """
                INSERT INTO document_chunks (
                    id, document_name, section_heading, page_number,
                    chunk_index, chunk_text, token_count, embedding
                ) VALUES %s
                """
                tuples = [
                    (
                        c["id"],
                        c["document_name"],
                        c.get("section_heading", ""),
                        c["page_number"],
                        c["chunk_index"],
                        c["chunk_text"],
                        c["token_count"],
                        str(c["embedding"]),
                    )
                    for c in chunks
                ]
                execute_values(cur, query, tuples)
            conn.commit()
            conn.close()
            inserted_count = len(chunks)
        except Exception as e:
            logger.warning("Postgres insert failed (%s); storing in-memory.", e)

    # Always keep in-memory store synchronized
    _IN_MEMORY_CHUNKS.extend(chunks)
    if inserted_count == 0:
        inserted_count = len(chunks)

    return inserted_count


def search_chunks(
    query_vector: list[float],
    top_k: int = 3,
    min_similarity: float = -1.0,
) -> list[dict[str, Any]]:
    """Retrieve top-k similar chunks using cosine similarity."""
    if not query_vector:
        return []

    # Try PostgreSQL pgvector search
    if is_postgres_available():
        try:
            import psycopg2

            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            with conn.cursor() as cur:
                # Cosine distance operator is <=>
                cur.execute(
                    """
                    SELECT id, document_name, section_heading, page_number,
                           chunk_index, chunk_text, token_count,
                           1 - (embedding <=> %s::vector) AS similarity
                    FROM document_chunks
                    ORDER BY embedding <=> %s::vector ASC
                    LIMIT %s;
                    """,
                    (str(query_vector), str(query_vector), top_k),
                )
                rows = cur.fetchall()
            conn.close()
            results = []
            for r in rows:
                results.append(
                    {
                        "id": str(r[0]),
                        "document_name": r[1],
                        "section_heading": r[2],
                        "page_number": r[3],
                        "chunk_index": r[4],
                        "chunk_text": r[5],
                        "token_count": r[6],
                        "similarity": float(r[7]),
                    }
                )
            if results:
                return results
        except Exception as e:
            logger.warning("Postgres vector search failed (%s); using in-memory store.", e)

    # In-memory cosine search fallback
    scored: list[tuple[float, dict[str, Any]]] = []
    for c in _IN_MEMORY_CHUNKS:
        sim = cosine_similarity(query_vector, c["embedding"])
        if sim >= min_similarity:
            scored.append((sim, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for sim, c in scored[:top_k]:
        item = dict(c)
        item["similarity"] = sim
        results.append(item)
    return results


def get_chunk_count() -> int:
    """Get the current count of ingested chunks."""
    if is_postgres_available():
        try:
            import psycopg2

            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM document_chunks;")
                count = cur.fetchone()[0]
            conn.close()
            return count
        except Exception:
            pass
    return len(_IN_MEMORY_CHUNKS)


def clear_in_memory_chunks() -> None:
    """Clear all in-memory chunks (useful for test resets)."""
    global _IN_MEMORY_CHUNKS
    _IN_MEMORY_CHUNKS = []


def save_chunks_to_cache(file_path: str = "data/chunks_store.json") -> int:
    """Serialize the in-memory chunks store to disk for instant warm starts."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as fp:
        json.dump(_IN_MEMORY_CHUNKS, fp, indent=2)
    return len(_IN_MEMORY_CHUNKS)


def load_chunks_from_cache(file_path: str = "data/chunks_store.json") -> int:
    """Load precomputed chunks and embeddings from disk cache."""
    global _IN_MEMORY_CHUNKS
    if not os.path.exists(file_path):
        return 0
    try:
        with open(file_path, encoding="utf-8") as fp:
            data = json.load(fp)
            _IN_MEMORY_CHUNKS = data
            return len(_IN_MEMORY_CHUNKS)
    except Exception as e:
        logger.warning("Failed loading chunks cache from %s: %s", file_path, e)
        return 0
