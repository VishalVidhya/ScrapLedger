"""Ingestion CLI for parsing, chunking, and embedding CPCB regulatory PDFs.

Parses all 500+ pages from data/raw/, generates 768-dimensional dense embeddings,
and stores them into Postgres + pgvector (with local cache in data/chunks_store.json).
"""

from __future__ import annotations

import argparse
import logging
import os
import time

from app.db import init_db, insert_chunks, save_chunks_to_cache
from app.embeddings import get_embedding
from app.parser import parse_and_chunk_pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest")


def ingest_all_pdfs(
    raw_dir: str = "data/raw",
    cache_path: str = "data/chunks_store.json",
    chunk_size_tokens: int = 400,
    overlap_tokens: int = 50,
) -> dict[str, int]:
    """Parse, chunk, embed, and store all PDFs from raw_dir."""
    start_time = time.time()
    init_db()

    pdf_files = [f for f in sorted(os.listdir(raw_dir)) if f.lower().endswith(".pdf")]
    logger.info("Found %d PDF documents in %s", len(pdf_files), raw_dir)

    all_chunks = []
    total_pages = 0

    for idx, fname in enumerate(pdf_files, 1):
        fpath = os.path.join(raw_dir, fname)
        logger.info("[%d/%d] Parsing and chunking: %s", idx, len(pdf_files), fname)
        try:
            doc_chunks = parse_and_chunk_pdf(
                fpath,
                chunk_size_tokens=chunk_size_tokens,
                overlap_tokens=overlap_tokens,
            )
            # Find max page number in doc_chunks
            max_page = max((c["page_number"] for c in doc_chunks), default=0)
            total_pages += max_page

            # Generate embeddings for each chunk
            for c in doc_chunks:
                c["embedding"] = get_embedding(c["chunk_text"])

            all_chunks.extend(doc_chunks)
            logger.info("  -> Generated %d chunks across %d pages", len(doc_chunks), max_page)
        except Exception as e:
            logger.error("Error processing %s: %s", fname, e)

    logger.info("Inserting %d total chunks into vector store...", len(all_chunks))
    inserted = insert_chunks(all_chunks)

    # Save to disk cache for instant warm start
    saved = save_chunks_to_cache(cache_path)
    elapsed = time.time() - start_time

    logger.info(
        "Ingestion completed: %d documents, %d pages, %d chunks in %.2f seconds.",
        len(pdf_files),
        total_pages,
        len(all_chunks),
        elapsed,
    )

    return {
        "documents": len(pdf_files),
        "pages": total_pages,
        "chunks": len(all_chunks),
        "inserted": inserted,
        "saved_to_cache": saved,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest PDFs into Postgres + pgvector")
    parser.add_argument("--raw-dir", default="data/raw", help="Path to raw PDFs directory")
    parser.add_argument("--cache", default="data/chunks_store.json", help="Path to chunks cache")
    args = parser.parse_args()

    ingest_all_pdfs(raw_dir=args.raw_dir, cache_path=args.cache)


if __name__ == "__main__":
    main()

