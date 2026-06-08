from __future__ import annotations
from typing import List, Dict, Any, Optional
import sys
import re

from .paper_filter import extract_paper_id
from src.config.settings import VECTOR_STORE_CONFIG

try:
    from rank_bm25 import BM25Okapi
except ImportError as e:
    raise ImportError(
        "rank_bm25 is required for bm25_retriever"
    ) from e


#tokenization
TOKEN_SPLIT_REGEX = re.compile(r"\W+", re.UNICODE)

def _normalize(text: str) -> str:
    return text.lower().strip()

def _tokenization(text: str) -> List[str]:
    text_norm = _normalize(text)

    if not text_norm:
        return []
    
    return [t for t in TOKEN_SPLIT_REGEX.split(text_norm) if t]

# Index storage

class BM25Index:
    #"in memory BM25 index over chunks"

    def __init__(self) -> None:
        self._bm25: Optional[BM25Okapi] = None
        self._chunk_ids: List[str] = []
        self._chunk_texts: List[str] = []
        self._chunk_source_docs: List[str] = []
        self._chunk_metadatas: List[Dict[str, Any]] = []


    def is_built(self) -> bool:
        return self._bm25 is not None
    
    def build_from_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        if not chunks:
            raise ValueError("[BM25Index] No chunks provided for BM25 index")
        

        tokenized_corpus = []
        self._chunk_ids = []
        self._chunk_texts = []
        self._chunk_source_docs = []
        self._chunk_metadatas = []

        for c in chunks:
            cid = c.get("chunk_id")
            text = c.get("text") or ""
            source_doc = c.get("source_doc", "unknown")
            metadata = c.get("metadata") or {}


            tokens = _tokenization(text)

            if not tokens:
                continue
            tokenized_corpus.append(tokens)
            self._chunk_ids.append(cid)
            self._chunk_texts.append(text)
            self._chunk_source_docs.append(source_doc)
            self._chunk_metadatas.append(metadata)
        if not tokenized_corpus:
            raise ValueError(
                "[BM25 INDEX] AFTER FILTERNING, NO NON-EMTPY CHUNKS TO INDEX"
            )
        
        self._bm25 = BM25Okapi(tokenized_corpus)
        print(f"[BM25INDEX] BUILT BM25 INDEX OVER {len(self._chunk_ids)} chunks.")

    def get_top_n(
            self,
            query:str,
            n:int
    ) -> List[Dict[str, Any]]:
        if self._bm25 is None:
            raise RuntimeError(
                "[BM25INDEX] BM25 index has not been built yet."
            )
        
        tokens = _tokenization(query)
        if not tokens:
            return []
        
        scores = self._bm25.get_scores(tokens)

        scored_indices = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
            )

        results: List[Dict[str, Any]] = []

        for idx, score in scored_indices[:n]:
            cid = self._chunk_ids[idx]
            text = self._chunk_texts[idx]
            source_doc = self._chunk_source_docs[idx]
            metadata = self._chunk_metadatas[idx]
            results.append(
                {
                    "chunk_id": cid,
                    "text": text,
                    "source_doc": source_doc,
                    "metadata": metadata,
                    "score": float(score),
                }
            )
            
        return results
    
_bm25_index: Optional[BM25Index] = None
_cached_chunks: Optional[List[Dict[str, Any]]] = None

def _get_bm25_index() -> BM25Index:
    global _bm25_index, _cached_chunks
    if _bm25_index is None:
        _bm25_index = BM25Index()
    if not _bm25_index.is_built():
        if _cached_chunks is None:
            _cached_chunks = load_all_chunks()
        _bm25_index.build_from_chunks(_cached_chunks)
    return _bm25_index


def load_all_chunks() -> List[Dict[str, Any]]:
    from src.vector_store import get_or_create_collection

    collection = get_or_create_collection()
    data = collection.get()
    ids = data["ids"]
    docs = data["documents"]
    metas = data["metadatas"]

    chunks = []

    for cid, doc, meta in zip(ids, docs, metas):
        chunks.append(
            {
                "chunk_id": cid,
                "text": doc,
                "source_doc": meta.get("source_doc", "unknown"),
                "metadata": meta,
            }
        )

    return chunks


def ensure_bm25_index_built() -> None:
    _get_bm25_index()



def retriever_bm25_as_dicts(
    query_text: str,
    top_k: int = VECTOR_STORE_CONFIG["default_top_k"],
    paper_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    if not query_text.strip():
        raise ValueError("Query text must not be empty")
    
    # Auto-detect paper ID if not provided
    if paper_id is None:
        paper_id = extract_paper_id(query_text)
    
    if paper_id:
        print(f"[PAPER FILTER] Filtered retrieval: enabled for paper '{paper_id}'")

    index = _get_bm25_index()
    results = index.get_top_n(
        query=query_text,
        n=top_k
    )
    
    # Apply paper filter post-retrieval (BM25 needs to search all chunks)
    if paper_id:
        results = [r for r in results if r.get("source_doc") == paper_id]
        print(f"[PAPER FILTER] Filtered to {len(results)} chunk(s) matching paper '{paper_id}'")

    print(f"[BM25] retrieved {len(results)} chunk(s) with BM25")
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bm25_retriever.py '<your question>'")
        sys.exit(1)

    q = sys.argv[1]
    try:
        res = retriever_bm25_as_dicts(query_text=q, top_k=VECTOR_STORE_CONFIG["default_top_k"])
    except NotImplementedError as e:
        print("[BM25] ERROR:", e)
        sys.exit(1)

    print("\n[BM25] Results:")
    for i, r in enumerate(res, start=1):
        print(f"\n#{i} | ID={r.get('chunk_id')} | source={r.get('source_doc')}")
        print(f"BM25 score  : {r.get('score')}")
        print(f"Metadata    : {r.get('metadata')}")
        print(f"Text preview: { (r.get('text') or '')[:200] }...")
