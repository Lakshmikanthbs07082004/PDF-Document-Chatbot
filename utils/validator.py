"""
validator.py — Input validation for uploaded files and user queries.

Why a separate validator?  Keeps validation logic out of the UI layer,
making it testable and reusable. Every edge case (empty input, wrong
file type, oversized file, etc.) is caught here with clear error messages.
"""

import os
import logging
from typing import Optional

import config

logger = logging.getLogger(__name__)


def validate_file(filename: str, file_size: int) -> tuple[bool, Optional[str]]:
    """Validate an uploaded file by name and size.

    Checks:
      1. File extension is in ALLOWED_EXTENSIONS.
      2. File size does not exceed MAX_FILE_SIZE_BYTES.

    Args:
        filename (str): Original name of the uploaded file (e.g., "report.pdf").
        file_size (int): Size of the file in bytes.

    Returns:
        tuple[bool, Optional[str]]:
            (True, None) if valid; (False, error_message) if invalid.

    Example:
        >>> ok, err = validate_file("thesis.pdf", 5_000_000)
        >>> assert ok is True
    """
    # Check file extension
    ext: str = os.path.splitext(filename)[1].lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        msg = f"Unsupported file type '{ext}'. Please upload a PDF file."
        logger.warning("File validation failed: %s", msg)
        return False, msg

    # Check file size
    max_mb: float = config.MAX_FILE_SIZE_BYTES / (1024 * 1024)
    if file_size > config.MAX_FILE_SIZE_BYTES:
        msg = f"File too large ({file_size / (1024*1024):.1f} MB). Maximum allowed is {max_mb:.0f} MB."
        logger.warning("File validation failed: %s", msg)
        return False, msg

    # Check for empty file
    if file_size == 0:
        msg = "The uploaded file is empty (0 bytes)."
        logger.warning("File validation failed: %s", msg)
        return False, msg

    logger.info("File '%s' passed validation (%d bytes).", filename, file_size)
    return True, None


def validate_query(query: str) -> tuple[bool, Optional[str]]:
    """Validate the user's query string.

    Checks:
      1. Query is not empty or whitespace-only.
      2. Query length is within [MIN_QUERY_LENGTH, MAX_QUERY_LENGTH].

    Args:
        query (str): The raw query text from the user.

    Returns:
        tuple[bool, Optional[str]]:
            (True, None) if valid; (False, error_message) if invalid.

    Example:
        >>> ok, err = validate_query("What is deep learning?")
        >>> assert ok is True
        >>> ok, err = validate_query("")
        >>> assert ok is False
    """
    # Strip whitespace for the checks
    stripped: str = query.strip()

    # Empty or whitespace-only
    if not stripped:
        msg = "Please enter a question. The query cannot be empty."
        logger.warning("Query validation failed: empty query.")
        return False, msg

    # Too short
    if len(stripped) < config.MIN_QUERY_LENGTH:
        msg = f"Query is too short (minimum {config.MIN_QUERY_LENGTH} characters)."
        logger.warning("Query validation failed: too short (%d chars).", len(stripped))
        return False, msg

    # Too long
    if len(stripped) > config.MAX_QUERY_LENGTH:
        msg = f"Query is too long ({len(stripped)} chars). Maximum is {config.MAX_QUERY_LENGTH} characters."
        logger.warning("Query validation failed: too long (%d chars).", len(stripped))
        return False, msg

    logger.info("Query passed validation (%d chars).", len(stripped))
    return True, None
