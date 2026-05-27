"""
Configuration Module - AI Learning Management System

Quản lý tất cả các cấu hình central cho project.
Sử dụng environment variables để lưu API keys và settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables từ .env file
load_dotenv()


# ============================================================
# Path Configurations
# ============================================================

# Root directory của project
PROJECT_ROOT = Path(__file__).parent

# Thư mục chứa dữ liệu (PDF files, FAISS index, v.v.)
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Thư mục chứa PDF files
PDF_DIR = DATA_DIR / "pdfs"
PDF_DIR.mkdir(exist_ok=True)

# Thư mục chứa FAISS vector store
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
VECTOR_STORE_DIR.mkdir(exist_ok=True)

# Thư mục chứa cached embeddings
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)


# ============================================================
# API Keys & Secrets
# ============================================================

# Gemini API Key - Lấy từ environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Check xem API key đã được set chưa
if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY chưa được set! "
        "Vui lòng tạo file .env với nội dung: GEMINI_API_KEY=your_api_key_here"
    )


# ============================================================
# Gemini Model Configuration
# ============================================================

# Model name cho chat
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")

# Temperature cho generation (0.0 = deterministic, 1.0 = creative)
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))

# Maximum tokens trong response
GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", "2048"))

# Top P sampling
GEMINI_TOP_P = float(os.getenv("GEMINI_TOP_P", "0.95"))

# Top K sampling
GEMINI_TOP_K = int(os.getenv("GEMINI_TOP_K", "40"))


# ============================================================
# Embedding Configuration
# ============================================================

# Model name cho embeddings (sentence-transformers)
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Embedding dimension (của model all-MiniLM-L6-v2 là 384)
EMBEDDING_DIMENSION = 384

# Batch size cho embedding generation
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))


# ============================================================
# PDF Processing Configuration
# ============================================================

# Kích thước chunk (số ký tự)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))

# Overlap giữa các chunks (số ký tự)
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Số ký tự tối thiểu để considered là valid chunk
MIN_CHUNK_LENGTH = int(os.getenv("MIN_CHUNK_LENGTH", "100"))

# Encoding cho text extraction
PDF_ENCODING = os.getenv("PDF_ENCODING", "utf-8")


# ============================================================
# FAISS Vector Store Configuration
# ============================================================

# Index type: "Flat" (exact search) hoặc "IVF" (approximate search)
FAISS_INDEX_TYPE = os.getenv("FAISS_INDEX_TYPE", "Flat")

# Số neighbors tối đa để retrieve
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))

# Search params cho IVF index (nprobe)
FAISS_NPROBE = int(os.getenv("FAISS_NPROBE", "10"))


# ============================================================
# RAG Configuration
# ============================================================

# Số document contexts tối đa để đưa vào prompt
MAX_CONTEXT_DOCUMENTS = int(os.getenv("MAX_CONTEXT_DOCUMENTS", "5"))

# Similarity threshold (0.0 - 1.0)
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.0"))


# ============================================================
# System Configuration
# ============================================================

# Logging level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Cache embeddings (tiết kiệm API calls)
USE_CACHE = os.getenv("USE_CACHE", "true").lower() == "true"


# ============================================================
# Utility Functions
# ============================================================

def get_config_summary() -> dict:
    """Trả về tóm tắt configuration (không bao gồm secrets)."""
    return {
        "gemini_model": GEMINI_MODEL_NAME,
        "embedding_model": EMBEDDING_MODEL_NAME,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "faiss_index_type": FAISS_INDEX_TYPE,
        "default_top_k": DEFAULT_TOP_K,
        "data_directory": str(DATA_DIR),
    }


def validate_config() -> bool:
    """Kiểm tra configuration có hợp lệ không."""
    errors = []

    if not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY is required")

    if CHUNK_SIZE <= 0:
        errors.append("CHUNK_SIZE must be positive")

    if CHUNK_OVERLAP >= CHUNK_SIZE:
        errors.append("CHUNK_OVERLAP must be less than CHUNK_SIZE")

    if not (0.0 <= GEMINI_TEMPERATURE <= 2.0):
        errors.append("GEMINI_TEMPERATURE must be between 0.0 and 2.0")

    if errors:
        for error in errors:
            print(f"[CONFIG ERROR] {error}")
        return False

    return True
