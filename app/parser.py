"""PDF parser and semantic chunker preserving page numbers and section headings.

Extracts text page-by-page from CPCB and MoEFCC regulatory gazettes and SOPs,
maintaining exact document name, page citations, and section headings.
"""

from __future__ import annotations

import logging
import os
import re
import uuid
from typing import Any

from pypdf import PdfReader

logger = logging.getLogger(__name__)

# Regex patterns matching Indian statutory headings and sections
HEADING_PATTERNS = [
    re.compile(r"^(CHAPTER\s+[IVXLCDM\d]+[^\n]*)", re.IGNORECASE),
    re.compile(r"^(SCHEDULE\s+[IVXLCDM\d]+[^\n]*)", re.IGNORECASE),
    re.compile(r"^(FORM\s+[\dA-Z\-]+[^\n]*)", re.IGNORECASE),
    re.compile(r"^(RULE\s+\d+[^\n]*)", re.IGNORECASE),
    re.compile(r"^(PART\s+[A-Z\d]+[^\n]*)", re.IGNORECASE),
    re.compile(r"^(GUIDELINES?\s+FOR[^\n]*)", re.IGNORECASE),
    re.compile(r"^(STANDARD\s+OPERATING\s+PROCEDURE[^\n]*)", re.IGNORECASE),
    re.compile(r"^(NOTIFICATION[^\n]*)", re.IGNORECASE),
]


def extract_heading_from_text(text: str, fallback_heading: str = "") -> str:
    """Extract a salient heading from the text lines, or retain previous heading."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:10]:
        for pattern in HEADING_PATTERNS:
            match = pattern.match(line)
            if match:
                return match.group(1).strip()
    return fallback_heading


def parse_pdf(file_path: str) -> list[dict[str, Any]]:
    """Parse a single PDF file into page-level text items.

    Each item contains:
    - document_name: filename of the PDF
    - page_number: 1-indexed page number
    - text: raw text content of the page
    - heading: extracted section or rule heading
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    doc_name = os.path.basename(file_path)
    pages_data: list[dict[str, Any]] = []

    try:
        reader = PdfReader(file_path)
    except Exception as e:
        logger.error("Failed to read PDF %s: %s", file_path, e)
        return []

    current_heading = "General Regulations"

    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        try:
            page_text = page.extract_text() or ""
        except Exception as e:
            logger.warning("Failed extracting page %d of %s: %s", page_num, doc_name, e)
            page_text = ""

        # Normalize text whitespace while preserving paragraph breaks
        cleaned_text = re.sub(r"\r\n|\r", "\n", page_text)
        cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
        cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()

        # Update heading if new chapter/schedule/rule appears on this page
        detected_heading = extract_heading_from_text(cleaned_text, current_heading)
        if detected_heading:
            current_heading = detected_heading

        pages_data.append(
            {
                "document_name": doc_name,
                "page_number": page_num,
                "text": cleaned_text,
                "heading": current_heading,
            }
        )

    return pages_data


def estimate_tokens(text: str) -> int:
    """Approximate token count using word/whitespace heuristic (1 token ~ 0.75 words)."""
    words = text.split()
    return max(1, int(len(words) * 1.33))


def chunk_page_text(
    page_text: str,
    chunk_size_tokens: int = 400,
    overlap_tokens: int = 50,
) -> list[str]:
    """Break single page text into sliding-window chunks with overlap."""
    if not page_text.strip():
        return []

    words = page_text.split()
    chunk_size_words = max(50, int(chunk_size_tokens / 1.33))
    overlap_words = max(10, int(overlap_tokens / 1.33))

    if len(words) <= chunk_size_words:
        return [page_text]

    chunks = []
    start = 0
    while start < len(words):
        end = min(len(words), start + chunk_size_words)
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end >= len(words):
            break
        start += chunk_size_words - overlap_words

    return chunks


def parse_and_chunk_pdf(
    file_path: str,
    chunk_size_tokens: int = 400,
    overlap_tokens: int = 50,
) -> list[dict[str, Any]]:
    """Parse PDF and emit structured chunks compliant with document_chunks table schema."""
    pages = parse_pdf(file_path)
    chunks_data: list[dict[str, Any]] = []
    chunk_index = 0

    for page in pages:
        p_text = page["text"]
        if not p_text.strip():
            continue

        page_chunks = chunk_page_text(
            p_text,
            chunk_size_tokens=chunk_size_tokens,
            overlap_tokens=overlap_tokens,
        )

        for c_text in page_chunks:
            chunk_id = str(uuid.uuid4())
            chunks_data.append(
                {
                    "id": chunk_id,
                    "document_name": page["document_name"],
                    "section_heading": page["heading"],
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index,
                    "chunk_text": c_text,
                    "token_count": estimate_tokens(c_text),
                }
            )
            chunk_index += 1

    return chunks_data
