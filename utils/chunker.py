"""
chunker.py — Split extracted text into overlapping chunks.

Why chunking?  Embedding models have token limits, and smaller chunks
produce more focused embeddings -> better retrieval accuracy.

Why overlap?  Prevents important sentences at chunk boundaries from
being split across two chunks and losing context.
"""

import logging
from config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """Split a long text string into overlapping chunks.

    Each chunk is returned as a dict with its index and content,
    making it easy to reference in citations.

    Args:
        text (str): The full extracted text from the PDF.
        chunk_size (int): Maximum number of characters per chunk.
        overlap (int): Number of characters to overlap between consecutive chunks.

    Returns:
        list[dict]: A list of dicts, each with keys:
            - "index" (int): 0-based chunk number.
            - "content" (str): The chunk text.

    Raises:
        ValueError: If chunk_size or overlap have invalid values.

    Example:
        >>> chunks = chunk_text("Hello world " * 500, chunk_size=100, overlap=20)
        >>> print(f"Created {len(chunks)} chunks")
    """
    # Validate parameters
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")
    if overlap < 0:
        raise ValueError(f"overlap must be non-negative, got {overlap}")
    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be smaller than chunk_size ({chunk_size})"
        )

    # Handle edge case: empty or whitespace-only text
    if not text or not text.strip():
        logger.warning("Received empty text -- returning no chunks.")
        return []

    chunks: list[dict] = []
    start: int = 0
    index: int = 0

    # Slide a window of chunk_size across the text with overlap step-back
    while start < len(text):
        end: int = start + chunk_size
        chunk_content: str = text[start:end].strip()

        # Only add non-empty chunks (avoids trailing whitespace chunks)
        if chunk_content:
            chunks.append({"index": index, "content": chunk_content})
            index += 1

        # Move the window forward by (chunk_size - overlap)
        start += chunk_size - overlap

    logger.info("Split text into %d chunks (size=%d, overlap=%d).", len(chunks), chunk_size, overlap)
    return chunks
