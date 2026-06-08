from typing import List, Dict, Any, Optional

import chromadb
from chromadb.utils import embedding_functions

from src.config.settings import(
    VECTOR_STORE_CONFIG,
    EMBEDDING_CONFIG
)
# from .embedding import EmbeddingModel

def get_chroma_client() -> chromadb.PersistentClient:
    client = chromadb.PersistentClient(path=str(VECTOR_STORE_CONFIG["persist_directory"]))
    return client

def get_embedding_function():
    """
    Creating a chroma embedding function based on config.
    For HF, we can either:
    - use chroma's sentenceTransformerEmbeddingFunction
    - or wrap our own EmbeddingModel(Advanced)
    """

    if EMBEDDING_CONFIG["backend"] == "huggingface":
        st_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=str(EMBEDDING_CONFIG["model_name"]),
            device=str(EMBEDDING_CONFIG["device"]),
            normalize_embeddings=False
        )
        return st_ef
    else:
        raise ValueError(f"Unsupported EMBEDDING BACKEND for chroma: {EMBEDDING_CONFIG['backend']}")


def get_or_create_collection():
    client = get_chroma_client()
    ef = get_embedding_function()

    collection = client.get_or_create_collection(
        name = VECTOR_STORE_CONFIG["collection_name"],
        embedding_function=ef,
    )
    return collection

def add_chunks_to_collection(
        chunks: List[Dict[str, Any]],
) -> None:
    """
    Add chunk docs to Chroma collections.

    each chunk dict is expected to have:
    - 'id' : integer or unique identifier
    - 'text' : Chunk content
    - 'source_doc' : document name
    - 'metadata' : optional dict of extra metadata
    """

    if not chunks:
        print("[VECTOR STORE] NO CHUNKS TO ADD.")
        return
    
    collection = get_or_create_collection()
    ids = [f"{c['source_doc']}_{c['id']}" for c in chunks]

    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "source_doc" : c["source_doc"],
            **(c.get("metadata") or {})
        }
        for c in chunks
    ]
    print(f"[VECTOR STORE] Adding {len(ids)} documents...")
    
    try:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        print(f"[VECTOR STORE] ✅ Successfully added {len(chunks)} chunks to collection '{VECTOR_STORE_CONFIG['collection_name']}'")
        
    except Exception as e:
        error_msg = f"[VECTOR STORE] ❌ ERROR: Failed to add {len(chunks)} chunks: {type(e).__name__}: {e}"
        print(error_msg, flush=True)
        raise RuntimeError(error_msg) from e


def query_collection(
        query_text: str,
        top_k: int = VECTOR_STORE_CONFIG["default_top_k"],
        paper_id: Optional[str] = None,
) -> Dict[str, Any]:
    collection = get_or_create_collection()
    
    where_filter = None
    if paper_id:
        where_filter = {"source_doc": paper_id}
        print(f"[VECTOR STORE] Applying where filter: {where_filter}")
    
    result = collection.query(
        query_texts= [query_text],
        n_results = top_k,
        where = where_filter,
    )
    return result