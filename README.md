# Research Paper Chat Bot - RAG System

A Retrieval-Augmented Generation (RAG) system for querying and analyzing academic research papers. This system allows you to ask questions about research papers and get accurate answers sourced directly from the paper content.

## 🎯 Project Overview

> ⚠️ This project is currently in active development. The core RAG pipeline is functional, while features such as advanced text cleaning, UI/UX, backend services, and public deployment are still under development.

The Research Paper Chat Bot enables researchers and students to:

- Upload PDF research papers
- Ask natural language questions about the papers
- Receive accurate, sourced answers from the paper content
- Understand key concepts and findings across multiple papers

**Key Features:**

- 📄 Batch PDF ingestion and processing
- 🔀 Hybrid Retrieval (Dense + Sparse Search)
- 🔎 BM25 Keyword-Based Retrieval
- 📊 Reciprocal Rank Fusion (RRF) Ranking
- 📈 Retrieval evaluation and benchmarking
- 🤖 Local LLM-based question answering
- 🖥️ CLI-based interaction
- 🎨 Web UI (Planned)
- 💾 Persistent vector store with Chroma DB
- 🚀 Lightweight and efficient models (optimized for CPU)

---

## 🏗️ Architecture

Graphify analysis of the current repository shows the system as a modular RAG pipeline with **105 extracted nodes**, **216 edges**, **10 detected communities**, and **no import cycles**. The most connected bridge in the architecture is `retriever_hybrid_as_dicts()` in `src/retrieval/hybrid_retriever.py`, because it connects dense retrieval, sparse BM25 retrieval, paper filtering, RRF fusion, QA, and evaluation.

The system follows this pipeline:

```
PDF / text corpus
  ↓
Ingestion
  ├── src/ingestion/pdf_loader.py
  ├── src/ingestion/text_extractor.py
  └── src/ingestion/chunker.py
  ↓
Persistent vector store
  ├── src/vector_store.py
  └── Chroma DB
  ↓
Retrieval
  ├── Dense retrieval: src/retrieval/retriever.py
  ├── Sparse retrieval: src/retrieval/bm25_retriever.py
  ├── Paper filtering: src/retrieval/paper_filter.py
  └── Hybrid retrieval + RRF: src/retrieval/hybrid_retriever.py
  ↓
RAG prompt construction
  └── src/retrieval/prompt_builder.py
  ↓
Local Hugging Face generation
  └── src/retrieval/chat_logic.py
  ↓
Answer with retrieved source chunks
```

### Architecture communities

The current graphify-detected communities map to these responsibilities:

1. **Hybrid retrieval and paper filtering**
   - `retriever_hybrid_as_dicts()`
   - `retrieve_hybrid()`
   - `_merge_results_rrf()`
   - `_build_rank_map()`
   - `_rrf_score()`
   - `filter_chunks_by_paper()`
   - `extract_paper_id()`

2. **Evaluation and benchmarking**
   - `evaluate_retrieval()`
   - `compare_retrieval_methods()`
   - `print_metrics_comparison()`
   - `run_benchmark()`
   - `save_benchmark_results()`
   - `print_benchmark_summary()`
   - `BenchmarkResult`

3. **Ingestion and chunking**
   - `pdf_loader()`
   - `load_all_pdfs()`
   - `extract_page_text()`
   - `extract_and_save_document_text()`
   - `build_chunks_from_sentences()`
   - `chunk_document_text()`
   - `build_chunks_for_all_pdfs()`
   - `split_text_into_sentences()`

4. **QA and LLM orchestration**
   - `main()`
   - `answer_question_with_hf()`
   - `_get_or_create_llm_client()`
   - `HFChatClient`

5. **BM25 sparse retrieval**
   - `BM25Index`
   - `_get_bm25_index()`
   - `ensure_bm25_index_built()`
   - `load_all_chunks()`
   - `_tokenization()`
   - `retriever_bm25_as_dicts()`

6. **Chroma vector store**
   - `PersistentClient`
   - `get_chroma_client()`
   - `get_or_create_collection()`
   - `get_embedding_function()`
   - `add_chunks_to_collection()`
   - `query_collection()`

7. **Prompt construction**
   - `build_chat_prompt()`
   - `build_plain_prompt()`
   - `build_content_block()`

### Main runtime entry point

`rag_query.py` is the current CLI entry point. It orchestrates the end-to-end flow:

```text
rag_query.py
  ├── retriever_hybrid_as_dicts()
  ├── answer_question_with_hf()
  └── compare_retrieval_methods()
```

It supports:

- normal hybrid retrieval
- hybrid retrieval plus LLM answer generation
- retrieval evaluation with ground-truth chunk IDs
- `--no-llm` mode for retrieval-only debugging

## 📁 Folder Structure

```
research_paper_chat_bot/
├── README.md
├── REPOSITORY_READINESS_REPORT.md
├── requirements.txt
├── .gitignore
├── bootstrap_project.py
├── rag_query.py                         # CLI entry point for query + QA + optional evaluation
│
├── data/
│   ├── input_pdfs/                      # Raw PDF files
│   ├── extracted_text/                  # Extracted text outputs
│   ├── chunks/                          # Debug chunk outputs
│   └── vector_store/                    # Persistent Chroma DB
│
├── src/
│   ├── __init__.py
│   ├── vector_store.py                  # Chroma client, embeddings, collection, add/query helpers
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                  # Paths, models, chunking, vector store settings
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── pdf_loader.py                # PDF discovery and loading
│   │   ├── text_extractor.py            # PDF text extraction and saved text outputs
│   │   ├── chunker.py                   # Sentence-based chunking
│   │   └── build_vector_store.py        # Ingestion orchestration: PDFs → text → chunks → Chroma
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── retriever.py                 # Dense Chroma retrieval and RetrieverChunk wrapper
│   │   ├── bm25_retriever.py            # Sparse BM25 retrieval over stored chunks
│   │   ├── hybrid_retriever.py          # Dense + BM25 + RRF fusion
│   │   ├── paper_filter.py              # arXiv-style paper ID extraction/filtering
│   │   ├── prompt_builder.py            # RAG prompt construction
│   │   └── chat_logic.py                # Local Hugging Face QA orchestration
│   │
│   └── evaluation/
│       ├── __init__.py
│       ├── evaluator.py                 # Retrieval metrics and dense/sparse/hybrid comparison
│       └── benchmark.py                 # Benchmark execution and result persistence
│
└── graphify-out/
    ├── graph.html                       # Generated architecture graph visualization
    ├── GRAPH_REPORT.md                  # Generated architecture report
    └── graph.json                       # Raw graph data
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

Place PDF files in `data/input_pdfs/`, then run:

```bash
python -m src.ingestion.build_vector_store
```

**What happens:**

1. Loads all PDFs from `data/input_pdfs/`
2. Extracts text to `data/extracted_text/`
3. Chunks text using `src/ingestion/chunker.py`
4. Creates or opens the Chroma collection
5. Adds chunk documents with source metadata to the vector store

### 2. Asking Questions (Hybrid Retrieval + QA)

Use the main CLI entry point:

```bash
python rag_query.py "What is the attention mechanism?" --top-k 5
```

This runs hybrid retrieval through:

```text
rag_query.py
  → retriever_hybrid_as_dicts()
  → answer_question_with_hf()
```

The answer is generated by the local Hugging Face chat client configured in `src/config/settings.py`.

### 3. Retrieval-Only Debugging

Skip LLM generation and inspect retrieved chunks:

```bash
python rag_query.py "What are transformers?" --top-k 5 --no-llm
```

This prints the hybrid retrieval results and scores without generating an answer.

### 4. Evaluating Retrieval

Run retrieval evaluation with ground-truth chunk IDs:

```bash
python rag_query.py "What is the attention mechanism?" \
  --top-k 5 \
  --evaluate \
  --ground-truth paperA_0 paperB_2 paperC_1
```

This compares dense, sparse, and hybrid retrieval using metrics from `src/evaluation/evaluator.py`:

- Precision@K
- Recall@K
- MRR
- nDCG@K

### 5. Python API Usage

```python
from src.retrieval.chat_logic import answer_question_with_hf

result = answer_question_with_hf(
    query_text="Explain the transformer architecture",
    top_k=5,
    max_chunks=3,
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

## 🚧 Project Status

**Current Version:** v0.2.0 (Development Stage)

> **Note:** This repository is primarily a learning and engineering project focused on understanding and building Retrieval-Augmented Generation (RAG) systems from scratch. The current implementation prioritizes modularity, experimentation, and learning rather than production readiness.

This project is currently in the early development phase and serves as a foundational implementation of a Research Paper Chat Bot using Retrieval-Augmented Generation (RAG).

The core RAG pipeline has been implemented and is currently under active testing and refinement.

### ✅ Implemented Features

- PDF Loading and Validation
- Text Extraction from Research Papers
- Sentence-Based Text Chunking
- Hugging Face Embedding Generation
- Chroma Vector Database Integration
- BM25 Sparse Retrieval
- Hybrid Retrieval (Dense + Sparse)
- Reciprocal Rank Fusion (RRF)
- Hybrid Search Ranking Pipeline
- Retrieval Evaluation and Benchmarking
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

### 2. Evaluation Framework Improvements

The basic retrieval evaluation framework exists through `src/evaluation/evaluator.py` and `src/evaluation/benchmark.py`, including Precision@K, Recall@K, MRR, nDCG@K, and dense/sparse/hybrid comparison.

Future improvements:

- Larger benchmark datasets
- Ground-truth creation tooling
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

## Version History

### v0.2.0

* Added BM25 Sparse Retrieval
* Added Hybrid Retrieval (Dense + Sparse Search)
* Added Reciprocal Rank Fusion (RRF)
* Improved retrieval quality for keyword-heavy queries
* Enhanced ranking pipeline for research paper search

### v0.1.0

* Initial RAG pipeline
* PDF ingestion
* Text extraction
* Chunking
* Embedding generation
* Chroma vector database
* Dense semantic retrieval
* Local LLM integration
