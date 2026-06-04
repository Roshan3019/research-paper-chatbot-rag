# Research Paper Chat Bot - RAG System

A Retrieval-Augmented Generation (RAG) system for querying and analyzing academic research papers. This system allows you to ask questions about research papers and get accurate answers sourced directly from the paper content.

## 🎯 Project Overview

> ⚠️ This project is currently in active development. The core RAG pipeline is functional, while features such as advanced text cleaning, model evaluation, UI/UX, backend services, and public deployment are still under development.

The Research Paper Chat Bot enables researchers and students to:

- Upload PDF research papers
- Ask natural language questions about the papers
- Receive accurate, sourced answers from the paper content
- Understand key concepts and findings across multiple papers

**Key Features:**

- 📄 Batch PDF ingestion and processing
- 🔍 Semantic search with vector embeddings
- 🤖 Local LLM-based question answering
- 🖥️ CLI-based interaction
- 🎨 Web UI (Planned)
- 💾 Persistent vector store with Chroma DB
- 🚀 Lightweight and efficient models (optimized for CPU)

---

## 🏗️ Architecture

The system follows a standard RAG (Retrieval-Augmented Generation) pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                    INGESTION PHASE                          │
└─────────────────────────────────────────────────────────────┘
    PDF Files (input_pdfs/)
         ↓
    PDF Loader (PyMuPDF)
         ↓
    Text Extraction (extract_text/)
         ↓
    Text Cleaning & Preprocessing (Planned)
         ↓
    Semantic Chunking (chunks/)
         ↓
    Embedding Generation (HuggingFace)
         ↓
    Vector Store (Chroma DB)

┌─────────────────────────────────────────────────────────────┐
│                    RETRIEVAL PHASE                          │
└─────────────────────────────────────────────────────────────┘
    User Query
         ↓
    Query Embedding (HuggingFace)
         ↓
    Semantic Search (Chroma)
         ↓
    Top-K Retrieval (k=5 default)
         ↓
    Prompt Construction
         ↓
    Local LLM Inference
         ↓
    Answer with Source Attribution
```

## 📁 Folder Structure

```
research_paper_chat_bot/
├── README.md                           # This file
├── REPOSITORY_READINESS_REPORT.md     # Detailed analysis & issues
├── requirements.txt                    # Python dependencies
├── .gitignore                          # Git ignore rules
├── bootstrap_project.py                # Initial project scaffolding
│
├── data/                               # Data directory (not in git)
│   ├── input_pdfs/                    # Raw PDF files upload location
│   ├── extracted_text/                # Extracted text (by pdf_loader)
│   ├── chunks/                        # Document chunks for debugging
│   └── vector_store/                  # Chroma persistent database
│
├── src/                                # Source code
│   ├── __init__.py                    # Package initialization
│   ├── vector_store.py                # Vector store management
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                # Configuration (paths, models, params)
│   │
│   ├── ingestion/                     # Data ingestion pipeline
│   │   ├── __init__.py
│   │   ├── pdf_loader.py             # PDF file loader
│   │   ├── text_extractor.py         # Text extraction from PDFs
│   │   ├── chunker.py                # Semantic text chunking
│   │   └── build_vector_store.py     # Orchestrates ingestion
│   │
│   └── retrieval/                     # Query & answer generation
│       ├── __init__.py
│       ├── retriever.py              # Vector store query
│       ├── prompt_builder.py         # Prompt engineering
│       └── chat_logic.py             # LLM integration
```

---

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- Git
- macOS, Linux, or Windows (WSL2 recommended for Windows)
- ~4GB RAM (more if running multiple concurrent queries)

### Setup Steps

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd research_paper_chat_bot
   ```

2. **Create a Python virtual environment:**

   ```bash
   # Using venv
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows

   # OR using conda
   conda create -n rag-bot python=3.9
   conda activate rag-bot
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create required directories:**
   ```bash
   mkdir -p data/{input_pdfs,extracted_text,chunks,vector_store}
   ```

---

## ⚙️ Setup & Configuration

### Configuration File

All settings are managed in `src/config/settings.py`:

```python
# Model Configuration
EMBEDDING_CONFIG = {
    "backend": "huggingface",
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",  # Lightweight
    "normalize_embeddings": True,
    "device": "cpu",
}

LLM_CONFIG = {
    "backend": "huggingface",
    "model_name": "Qwen/Qwen2.5-0.5B-Instruct",  # Lightweight model
    "temperature": 0.2,  # Lower = more focused
    "max_new_tokens": 512,
}

CHUNKER_CONFIG = {
    "target_chars": 1000,        # ~1000 chars per chunk
    "overlap_sentences": 1,      # Sentence overlap between chunks
    "sentence_endings": [".","!","?"],
}

VECTOR_STORE_CONFIG = {
    "type": "chroma",
    "persist_directory": str(VECTOR_STORE_DIR),
    "collection_name": "research_papers",
    "default_top_k": 5,  # Return 5 most relevant chunks
}
```

### Alternative LLM Models

Pre-configured lightweight models:

- `Qwen/Qwen2.5-0.5B-Instruct` (500MB) - Default, recommended for CPU
- `Qwen/Qwen2.5-1.5B-Instruct` (1.5GB) - Better quality, slower
- `microsoft/Phi-3-mini-4k-instruct` (2.3GB) - Good balance
- `meta-llama/Llama-2-7b-chat-hf` (13GB) - High quality, requires VRAM

---

## 📖 Usage Examples

### 1. Ingesting Papers (Data Pipeline)

First, place PDF files in `data/input_pdfs/`, then run:

```bash
# Run the full ingestion pipeline
python -m src.ingestion.build_vector_store

# Output:
# [PDF LOADER] FOUND 20 PDF(s) in 'data/input_pdfs'
# [INGESTION] PROCESSING PDF: paper1.pdf
# [TEXT EXTRACTOR] Saved extracted text to: data/extracted_text/paper1_extracted.txt
# [INGESTION] CREATED 47 chunks(s) for 'paper1.pdf'
# ...
# [INGESTION] TOTAL CHUNKS CREATED: 520
# [VECTOR STORE] Added 520 chunks(s) to collection 'research_papers'
```

**What happens:**

1. Loads all PDFs from `data/input_pdfs/`
2. Extracts text to `data/extracted_text/`
3. Chunks text with overlap
4. Generates embeddings
5. Stores in Chroma vector DB

### 2. Asking Questions (Retrieval + QA)

```bash
# CLI mode - ask a question
python -m src.retrieval.chat_logic "What is the attention mechanism?"

# Output:
# [RETRIEVER] Querying for: 'What is the attention mechanism?' (top_k=5)
# [RETRIEVER] Retrieved 5 chunk(s).
# [QA] Question: What is the attention mechanism?
#
# ================================================================================
# [QA] ANSWER
# The attention mechanism is a neural network technique that allows models to
# focus on different parts of the input when processing each output. It works by
# computing attention weights for each input element, allowing the model to
# dynamically emphasize relevant information...
# [Source: transformer_paper.pdf]
# ================================================================================
```

### 3. Retrieving Source Chunks

Test retrieval without LLM:

```bash
python -m src.retrieval.retriever "What are transformers?"

# Output:
# [RETRIEVER] Querying for: 'What are transformers?'
# [RETRIEVER] Retrieved 5 chunk(s).
#
# ============================================================
# Chunk 1 | ID: transformer_paper_0
# Source: transformer_paper
# Score: 0.1234 (lower = more similar)
# Metadata: {'pages': '1-2'}
# Text Preview:
# "Transformers are neural networks based on attention mechanisms
#  instead of recurrence or convolution. They were introduced in the
#  'Attention is All You Need' paper..."
```

### 5. Python API Usage

```python
from src.retrieval.chat_logic import answer_question_with_hf
from src.config.settings import VECTOR_STORE_CONFIG

# Ask a question
result = answer_question_with_hf(
    query_text="Explain the transformer architecture",
    top_k=5,  # Use top 5 chunks
    max_chunks=3,  # Include only 3 in prompt
)

print(f"Answer: {result['answer']}")
print(f"Sources: {[c['source_doc'] for c in result['chunks_used']]}")
print(f"Model: {result['model_name']}")
```

---

## ⚙️ Configuration Explanation

### Key Configuration Parameters

#### Embedding Model

- **Model:** `all-MiniLM-L6-v2` (22MB)
  - Fast (good for CPU)
  - 384-dimensional embeddings
  - Good balance of quality and speed
- **Device:** `cpu` (can change to `cuda` if GPU available)
- **Normalize:** Helps with cosine similarity

#### LLM Model

- **Model:** `Qwen2.5-0.5B-Instruct` (250MB)
  - Smallest available
  - Fast inference on CPU
  - Suitable for research questions
- **Temperature:** `0.2` (Lower = more focused, deterministic)
  - 0.0 = Deterministic (same answer every time)
  - 1.0 = Creative, varied responses
- **Max Tokens:** `512` (Limits answer length)

#### Chunking Strategy

- **Target Size:** 1000 characters (~150-200 words)
- **Overlap:** 1 sentence between chunks
- **Benefit:** Maintains context across chunk boundaries

#### Vector Store

- **Type:** Chroma (persistent, efficient)
- **Collection:** `research_papers` (name of collection)
- **Top-K:** 5 (retrieve 5 most relevant chunks per query)

---

## 🔍 Understanding the RAG Pipeline

### 1. Ingestion Phase

**Input:** PDF research papers

**Process:**

1. **PDF Loader** - Opens PDF, validates format
2. **Text Extractor** - Converts pages to plain text with page markers
3. **Text Cleaner** - Normalizes whitespace, removes artifacts
4. **Chunker** - Splits text into semantic chunks with overlap
5. **Embedder** - Converts chunk text to 384-dimensional vectors
6. **Vector Store** - Stores vectors with metadata for retrieval

**Output:** Searchable vector database

### 2. Retrieval Phase

**Input:** User question (natural language)

**Process:**

1. **Query Embedding** - Convert question to same vector space as chunks
2. **Semantic Search** - Find most similar chunks using cosine similarity
3. **Ranking** - Sort by similarity score (lower = more similar)
4. **Filtering** - Select top-K chunks (default K=5)

**Output:** Most relevant document chunks

### 3. Generation Phase

**Input:** Question + Retrieved chunks

**Process:**

1. **Prompt Engineering** - Format question and chunks into structured prompt
2. **LLM Inference** - Feed prompt to local language model
3. **Answer Generation** - Model generates answer based on context
4. **Source Attribution** - Include source document references

**Output:** Final answer with sources

---

## 🚧 Project Status

**Current Version:** v0.1.0 (Development Stage)

> **Note:** This repository is primarily a learning and engineering project focused on understanding and building Retrieval-Augmented Generation (RAG) systems from scratch. The current implementation prioritizes modularity, experimentation, and learning rather than production readiness.

This project is currently in the early development phase and serves as a foundational implementation of a Research Paper Chat Bot using Retrieval-Augmented Generation (RAG).

The core RAG pipeline has been implemented and is currently under active testing and refinement.

### ✅ Implemented Features

- PDF Loading and Validation
- Text Extraction from Research Papers
- Sentence-Based Text Chunking
- Hugging Face Embedding Generation
- Chroma Vector Database Integration
- Semantic Similarity Search
- Top-K Document Retrieval
- Prompt Construction for RAG
- Local Hugging Face LLM Integration
- End-to-End Question Answering Workflow
- Configurable Settings Management
- Persistent Vector Store

### 🎯 Current Goal

The primary objective of this project is to build a robust and well-structured RAG system from scratch while gaining a deep understanding of:

- Document ingestion pipelines
- Text preprocessing workflows
- Embedding generation
- Vector databases
- Retrieval systems
- Prompt engineering
- Local LLM inference
- End-to-end RAG architecture

The current implementation successfully demonstrates the complete RAG workflow and serves as a strong foundation for future enhancements.

---

## 🔮 Planned Implementations

The following components are planned for future development and are not fully implemented yet.

### 1. Text Cleaning & Preprocessing

- Advanced document cleaning
- PDF artifact removal
- Header and footer detection
- Better text normalization
- Improved document quality before chunking

### 2. Model Evaluation Framework

- Retrieval quality evaluation
- RAG benchmarking metrics
- Embedding model comparison
- LLM answer quality assessment
- Experiment tracking and reporting

### 3. Production System Design

- Improved project architecture
- Logging and monitoring
- Comprehensive error handling
- Automated testing suite
- CI/CD integration
- Configuration management improvements

### 4. UI / UX Interface

- Interactive user interface
- Better document upload experience
- Source citation visualization
- Chat history management
- Improved user experience and navigation

### 5. Full-Stack Application & Deployment

- Backend API development
- Frontend application development
- Authentication and user management
- Cloud deployment
- Publicly accessible chatbot platform
- Production hosting and scaling

---

## 📈 Future Enhancements

Potential future improvements include:

- Hybrid Retrieval (Keyword + Semantic Search)
- Multi-PDF Comparative Question Answering
- Research Paper Metadata Extraction
- Citation Tracking
- Table and Figure Understanding
- OCR Support for Scanned PDFs
- Multi-Language Research Paper Support
- Advanced RAG Evaluation Dashboard
- Real-Time Paper Ingestion Pipelines
- REST API Services
- Docker Containerization
- Production Monitoring and Analytics

---

## 🚀 Long-Term Vision

The long-term goal is to transform this project from a learning-focused RAG implementation into a complete research assistant platform capable of:

- Processing large collections of academic papers
- Delivering reliable source-grounded answers
- Providing an intuitive user experience
- Supporting multiple research workflows
- Operating as a scalable production-grade application

As development continues, the project will evolve beyond the core RAG pipeline to include a full frontend, backend services, deployment infrastructure, evaluation systems, and advanced user-facing features.
