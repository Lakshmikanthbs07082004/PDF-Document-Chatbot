"""
embedder.py — Generate vector embeddings using a local sentence-transformers model.

Why local embeddings?  They run entirely on your machine with zero API calls,
no rate limits, and no daily quotas. The 'all-MiniLM-L6-v2' model produces
384-dim vectors and is fast even on CPU (~90 MB download on first run).

Alternative: Google Gemini embeddings, OpenAI text-embedding-ada-002,
Cohere embed-v3. Local was chosen to avoid free-tier API quota limits.
"""

import logging
from typing import Optional

from sentence_transformers import SentenceTransformer

import config

logger = logging.getLogger(__name__)

# Module-level model (loaded lazily on first call)
_model: Optional[SentenceTransformer] = None


def _get_model() -> SentenceTransformer:
    """Return a cached SentenceTransformer model, loading it on first call.

    The model is downloaded once (~90 MB) and cached locally by
    huggingface_hub for all subsequent runs.

    Returns:
        SentenceTransformer: The loaded embedding model.

    Example:
        >>> model = _get_model()
    """
    global _model
    if _model is None:
        logger.info("Loading local embedding model '%s'…", config.EMBEDDING_MODEL)
        _model = SentenceTransformer(config.EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully.")
    return _model


def embed_text(text: str) -> list[float]:
    """Generate an embedding vector for a single text string.

    Args:
        text (str): The text to embed.

    Returns:
        list[float]: A 384-dimensional embedding vector.

    Raises:
        RuntimeError: If embedding generation fails.

    Example:
        >>> vec = embed_text("What is machine learning?")
        >>> print(len(vec))  # 384
    """
    try:
        model = _get_model()
        # encode() returns a numpy array; convert to plain list for JSON compatibility
        embedding = model.encode(text, show_progress_bar=False).tolist()
        return embedding
    except Exception as exc:
        logger.error("Embedding generation failed: %s", exc)
        raise RuntimeError(f"Failed to generate embedding: {exc}") from exc


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Add an 'embedding' field to each chunk dict.

    Processes chunks one at a time (simple, debuggable; batching can be
    added later for performance).

    Args:
        chunks (list[dict]): List of chunk dicts with at least a "content" key.

    Returns:
        list[dict]: The same list with an "embedding" key added to each dict.

    Raises:
        RuntimeError: If any embedding call fails.

    Example:
        >>> chunks = [{"index": 0, "content": "Hello"}]
        >>> embedded = embed_chunks(chunks)
        >>> print(len(embedded[0]["embedding"]))  # 384
    """
    logger.info("Embedding %d chunks...", len(chunks))
    for i, chunk in enumerate(chunks):
        # Embed each chunk's content and attach the vector
        chunk["embedding"] = embed_text(chunk["content"])
        if (i + 1) % 10 == 0:
            logger.info("Embedded %d / %d chunks.", i + 1, len(chunks))
    logger.info("All %d chunks embedded successfully.", len(chunks))
    return chunks
