from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data"
INPUT_PDFS_DIR = DATA_DIR / "input_pdfs"
EXTRACTED_TEXT_DIR = DATA_DIR / "extracted_text"
CHUNKS_DIR = DATA_DIR / "chunks"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"

SRC_DIR = PROJECT_ROOT / "src"
CONFIG_DIR = SRC_DIR / "config"
INGESTION_DIR = SRC_DIR / "ingestion"
RETRIEVAL_DIR = SRC_DIR / "retrieval"

PDF_LOADER_CONFIG = {
    "supported_extensions": [".pdf"],
    "validate_path": True,
    "validate_extension": True,
}

TEXT_EXTRACTOR_CONFIG = {
    "include_page_markers": True,
    "page_marker_format": "=== Page {page_num} / {total_pages} ({doc_name}) ===",
    "text_mode": "text",
    "sort_text": True,
}

CHUNKER_CONFIG = {
    "target_chars": 1000,
    "overlap_sentences": 1,
    "sentence_endings": [".","!","?"],
}

LOGGING_CONFIG = {
    "log_level": "INFO",
    "log_format": "[{module}] {message}",
}

EMBEDDING_CONFIG = {
    "backend": "huggingface",
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "normalize_embeddings": True,
    "device": "cpu",
}

LLM_CONFIG = {
    "backend": "huggingface",

    # Lightweight local model
    # "model_name": "microsoft/Phi-3-mini-4k-instruct",
    # "model_name": "Qwen/Qwen2.5-1.5B-Instruct",
    "model_name": "Qwen/Qwen2.5-0.5B-Instruct",
    "temperature": 0.2,
    "max_new_tokens": 512,
}

VECTOR_STORE_CONFIG = {
    "type": "chroma",

    "persist_directory": str(VECTOR_STORE_DIR),

    "collection_name": "research_papers",

    "default_top_k": 5,
}