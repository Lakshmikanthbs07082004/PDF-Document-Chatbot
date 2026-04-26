"""
document_loader.py — Extract raw text from uploaded PDF files.

Uses PyPDF2 to read each page and concatenate text.
Why PyPDF2?  Pure-Python, no system dependencies (unlike pdfminer or poppler),
lightweight, and sufficient for text-based PDFs.
"""

import logging
from io import BytesIO
from typing import Optional

from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

logger = logging.getLogger(__name__)


def load_pdf(file_bytes: bytes) -> tuple[str, int]:
    """Extract all text from a PDF provided as raw bytes.

    Reads each page sequentially and concatenates the text with page markers
    so that downstream components can trace which page content came from.

    Args:
        file_bytes (bytes): The raw byte content of the uploaded PDF file.

    Returns:
        tuple[str, int]: A tuple of (extracted_text, total_page_count).
            extracted_text may be empty if the PDF contains only images.

    Raises:
        ValueError: If the PDF is corrupted, encrypted, or otherwise unreadable.

    Example:
        >>> with open("sample.pdf", "rb") as f:
        ...     text, pages = load_pdf(f.read())
        >>> print(f"Extracted {len(text)} chars from {pages} pages")
    """
    try:
        # Wrap bytes in a BytesIO stream so PdfReader can seek through it
        reader = PdfReader(BytesIO(file_bytes))
    except PdfReadError as exc:
        # Corrupted or malformed PDF — surface a clear error message
        logger.error("Failed to parse PDF: %s", exc)
        raise ValueError(
            "The uploaded file appears to be a corrupted or invalid PDF."
        ) from exc
    except Exception as exc:
        # Catch-all for unexpected errors (e.g., empty file, wrong magic bytes)
        logger.error("Unexpected error reading PDF: %s", exc)
        raise ValueError(
            "Could not read the uploaded file. Please ensure it is a valid PDF."
        ) from exc

    total_pages: int = len(reader.pages)
    logger.info("PDF has %d page(s).", total_pages)

    # Accumulate text page-by-page with clear page delimiters
    parts: list[str] = []
    for page_num, page in enumerate(reader.pages, start=1):
        try:
            page_text: Optional[str] = page.extract_text()
        except Exception as exc:
            # Some pages may fail (e.g., scanned images) — skip gracefully
            logger.warning("Could not extract text from page %d: %s", page_num, exc)
            page_text = None

        if page_text and page_text.strip():
            # Prefix each page's text so citations can reference page numbers
            parts.append(f"[Page {page_num}]\n{page_text.strip()}")

    full_text: str = "\n\n".join(parts)

    if not full_text.strip():
        logger.warning("PDF contained no extractable text (possibly scanned/image-only).")

    return full_text, total_pages
