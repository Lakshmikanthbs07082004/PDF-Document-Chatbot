"""
retriever.py — Rank document chunks by semantic similarity to a query.

Uses cosine similarity between the query embedding and each chunk embedding.
Why cosine similarity?  It is the standard metric for comparing direction of
high-dimensional vectors; magnitude-invariant, fast, and well-understood.

Alternative: FAISS for large-scale search, but numpy is sufficient for
single-document use cases and has zero extra dependencies.
"""

import logging
import numpy as np

from utils.embedder import embed_text
import config

logger = logging.getLogger(__name__)


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors.

    Args:
        vec_a (list[float]): First vector.
        vec_b (list[float]): Second vector.

    Returns:
        float: Cosine similarity in range [-1, 1].

    Example:
        >>> _cosine_similarity([1, 0], [1, 0])
        1.0
    """
    a = np.array(vec_a, dtype=np.float64)
    b = np.array(vec_b, dtype=np.float64)

    # Dot product divided by product of magnitudes
    dot_product: float = float(np.dot(a, b))
    norm_a: float = float(np.linalg.norm(a))
    norm_b: float = float(np.linalg.norm(b))

    # Guard against zero-norm vectors (e.g., empty text embedding)
    if norm_a == 0.0 or norm_b == 0.0:
        logger.warning("Zero-norm vector detected -- returning similarity 0.0")
        return 0.0

    return dot_product / (norm_a * norm_b)


def retrieve_top_chunks(
    query: str,
    chunks: list[dict],
    top_k: int = config.TOP_K,
) -> list[dict]:
    """Retrieve the top-k most relevant chunks for a given query.

    Steps:
      1. Embed the user query.
      2. Compute cosine similarity with every chunk.
      3. Sort descending and return the top-k.

    Args:
        query (str): The user's natural-language question.
        chunks (list[dict]): List of chunk dicts, each with "content" and "embedding".
        top_k (int): Number of top chunks to return.

    Returns:
        list[dict]: Top-k chunks, each with an added "score" key (float).

    Raises:
        RuntimeError: If the query embedding fails.
        ValueError: If chunks are empty.

    Example:
        >>> results = retrieve_top_chunks("What is AI?", embedded_chunks)
        >>> print(results[0]["score"])
    """
    if not chunks:
        raise ValueError("No chunks available for retrieval. Please upload a PDF first.")

    # Step 1: embed the user query
    logger.info("Embedding query for retrieval...")
    query_embedding: list[float] = embed_text(query)

    # Step 2: score every chunk
    scored: list[dict] = []
    for chunk in chunks:
        score: float = _cosine_similarity(query_embedding, chunk["embedding"])
        scored.append({**chunk, "score": score})

    # Step 3: sort by score descending and take top-k
    scored.sort(key=lambda c: c["score"], reverse=True)
    top_results: list[dict] = scored[:top_k]

    logger.info(
        "Retrieved top %d chunks (best score=%.4f).",
        len(top_results),
        top_results[0]["score"] if top_results else 0.0,
    )
    return top_results
