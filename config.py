"""
config.py — Central configuration for the PDF Document Chatbot.

All constants, API keys, and tuneable parameters are defined here.
No other file should hardcode values — import from config instead.
"""

import os
import logging
from dotenv import load_dotenv

# ── Logging setup ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Load .env file so os.getenv can read user secrets ──────────
load_dotenv()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API Keys
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Model Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Gemini model used for chat / answer generation
GENERATION_MODEL: str = "gemini-2.5-flash-lite"

# Local sentence-transformers model for text embeddings (no API calls)
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Document Processing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Maximum file size allowed for upload (in bytes) — 20 MB
MAX_FILE_SIZE_BYTES: int = 20 * 1024 * 1024

# Allowed file extensions (only PDF for this project)
ALLOWED_EXTENSIONS: list[str] = [".pdf"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Chunking Parameters
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Number of characters per chunk — balances context vs. embedding quality
CHUNK_SIZE: int = 1000

# Overlap between consecutive chunks — prevents losing context at boundaries
CHUNK_OVERLAP: int = 200

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Retrieval Parameters
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# How many top chunks to retrieve for the LLM prompt
TOP_K: int = 5

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Input Validation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Maximum query length (in characters) to prevent abuse
MAX_QUERY_LENGTH: int = 2000

# Minimum query length — reject trivially short queries
MIN_QUERY_LENGTH: int = 3

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Prompt Template
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTEM_PROMPT: str = (
    "You are a helpful assistant that answers questions based ONLY on the "
    "provided document context. If the answer is not in the context, say "
    "'I could not find the answer in the uploaded document.'\n\n"
    "Format your answers in a clear, structured way:\n"
    "- Use **bold** for key terms and important points.\n"
    "- Use bullet points or numbered lists when listing multiple items.\n"
    "- Use short paragraphs for explanations.\n"
    "- Add headings (##) if the answer covers multiple topics.\n"
    "- Do NOT mention chunk numbers or internal source references in your answer."
)


def check_keys() -> bool:
    """Verify that all required API keys are configured.

    Returns:
        bool: True if all keys are set, False otherwise.

    Example:
        >>> import config
        >>> config.check_keys()
        True
    """
    # Check each required key and log a clear message if missing
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your-gemini-api-key-here":
        logger.error("GEMINI_API_KEY is missing or still set to the placeholder value.")
        return False

    logger.info("All API keys are configured correctly.")
    return True
