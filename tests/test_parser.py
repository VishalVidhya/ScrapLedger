import os

from app.parser import (
    chunk_page_text,
    estimate_tokens,
    extract_heading_from_text,
    parse_and_chunk_pdf,
    parse_pdf,
)


def test_extract_heading():
    sample_text = (
        "CHAPTER III\nRESPONSIBILITIES OF PRODUCERS\nEvery producer shall register on the portal."
    )
    heading = extract_heading_from_text(sample_text)
    assert "CHAPTER III" in heading

    form_text = "FORM 1\nApplication for registration by Producer"
    form_heading = extract_heading_from_text(form_text)
    assert "FORM 1" in form_heading

    plain_text = "Just some standard paragraph text without headings."
    fallback = extract_heading_from_text(plain_text, fallback_heading="Default Heading")
    assert fallback == "Default Heading"


def test_chunk_page_text_sliding_window():
    words = [f"word{i}" for i in range(200)]
    text = " ".join(words)

    chunks = chunk_page_text(text, chunk_size_tokens=60, overlap_tokens=15)
    assert len(chunks) > 1

    # Ensure overlapping words exist between adjacent chunks
    chunk_0_words = chunks[0].split()
    chunk_1_words = chunks[1].split()
    overlap = set(chunk_0_words).intersection(set(chunk_1_words))
    assert len(overlap) > 0


def test_estimate_tokens():
    text = "Extended Producer Responsibility under CPCB"
    tokens = estimate_tokens(text)
    assert tokens >= 5


def test_parse_sample_pdf():
    sample_pdf = os.path.join("data", "sample", "Battery-WasteManagementRules-2022.pdf")
    if not os.path.exists(sample_pdf):
        sample_pdf = os.path.join("data", "raw", "Battery-WasteManagementRules-2022.pdf")

    assert os.path.exists(sample_pdf), "Sample PDF should exist"
    pages = parse_pdf(sample_pdf)

    assert len(pages) == 51
    assert pages[0]["page_number"] == 1
    assert pages[50]["page_number"] == 51
    assert pages[0]["document_name"] == "Battery-WasteManagementRules-2022.pdf"

    # Verify structured chunks
    chunks = parse_and_chunk_pdf(sample_pdf, chunk_size_tokens=300, overlap_tokens=40)
    assert len(chunks) >= len(pages)

    for chunk in chunks:
        assert "document_name" in chunk
        assert "page_number" in chunk
        assert chunk["page_number"] >= 1
        assert "section_heading" in chunk
        assert "chunk_text" in chunk
        assert chunk["token_count"] > 0

