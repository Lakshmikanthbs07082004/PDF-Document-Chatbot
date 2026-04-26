"""
utils — Utility package for the PDF Document Chatbot.

Submodules:
    document_loader : Extract text from PDF files.
    chunker         : Split text into overlapping chunks.
    embedder        : Generate vector embeddings locally.
    retriever       : Rank chunks by cosine similarity.
    validator       : Validate user inputs and uploaded files.
"""

from utils.document_loader import load_pdf
from utils.chunker import chunk_text
from utils.embedder import embed_text, embed_chunks
from utils.retriever import retrieve_top_chunks
from utils.validator import validate_file, validate_query

__all__ = [
    "load_pdf",
    "chunk_text",
    "embed_text",
    "embed_chunks",
    "retrieve_top_chunks",
    "validate_file",
    "validate_query",
]
