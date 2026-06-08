from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
import sys
import os

from src.retrieval.retriever import RetrieverChunk, retrieve_as_dicts
from src.config.settings import VECTOR_STORE_CONFIG
from .paper_filter import extract_paper_id

#later implementation
try:
    from .bm25_retriever import retriever_bm25_as_dicts

except ImportError:
    retriever_bm25_as_dicts = None


HYBRID_DENSE_K : int = 10
HYBRID_SPARSE_K : int = 10

RRF_K :int = 60


#internal helpers

def _build_rank_map(
        results: List[Dict[str, Any]]
) -> Dict[str, int]:
    rank_map: Dict[str, int] = {}

    for idx, res in enumerate(results, start=1):
        cid = res.get("chunk_id")
        if cid is not None and cid not in rank_map:
            rank_map[cid] = idx
    return rank_map


def _rrf_score(
        dense_rank: Optional[int],
        sparse_rank: Optional[int],
        k : int = RRF_K,
) -> float:
    score = 0.0
    if dense_rank is not None:
        score += 1.0 / (k+dense_rank)
    
    if sparse_rank is not None:
        score += 1.0 / (k + sparse_rank)
    return score

def _merge_results_rrf(
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str , Any]],
        top_k : int,  
) -> List[Dict[str, Any]]:
    dense_rank = _build_rank_map(dense_results)
    sparse_rank = _build_rank_map(sparse_results)


    #collect all unique chunk_ids
    all_ids = set(dense_rank.keys()) | set(sparse_rank.keys())


    #mapping from id -> base dic
    id_to_result : Dict[str, Dict[str,Any]] = {}

    for res in dense_results:
        cid = res.get("chunk_id")
        if cid is not None:
            id_to_result[cid] = res

    for res in sparse_results:
        cid = res.get("chunk_id")
        if cid is not None and cid not in id_to_result:
            id_to_result[cid] = res

    
    #compute RRF scores
    scored: List[Tuple[str, float]] = []
    for cid in all_ids:
        dr = dense_rank.get(cid)
        sr = sparse_rank.get(cid)
        score = _rrf_score(dr, sr, k=RRF_K)
        scored.append((cid, score))

    
    scored.sort(key=lambda x: x[1], reverse=True)


    hybrid_results : List[Dict[str, Any]] = []
    for cid, score in scored[:top_k]:
        base = id_to_result[cid]
        result = dict(base)
        result["hybrid_score"] = score
        hybrid_results.append(result)

    return hybrid_results


#PUBLIC API
def retriever_hybrid_as_dicts(
        query_text: str,
        top_k: int = VECTOR_STORE_CONFIG["default_top_k"],
        dense_k: Optional[int] = None,
        sparse_k: Optional[int] = None,
        paper_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    #Hybrid Retrieval: BM25(Sparse) + Chroma(dense) + RRF fusion
    
    # Auto-detect paper ID if not provided
    if paper_id is None:
        paper_id = extract_paper_id(query_text)
    
    if paper_id:
        print(f"[PAPER FILTER] Filtered retrieval: enabled for paper '{paper_id}'")

    if not query_text.strip():
        raise ValueError("Query Text must not be empty.")
    
    if dense_k is None:
        dense_k = HYBRID_DENSE_K
    
    if sparse_k is None:
        sparse_k = HYBRID_SPARSE_K
    
    print(f"\n[HYBRID RETRIEVER]    QUERYING HYBRID FOR: {query_text}")
    print(f"[HYBRID RETRIEVER]      dense_k = {dense_k}, sparse_k = {sparse_k}, top_k = {top_k}")

    dense_results = retrieve_as_dicts(query_text=query_text, top_k=dense_k, paper_id=paper_id)
    
    if retriever_bm25_as_dicts is None:
        raise RuntimeError(
            "BM25 retriever not available"
            "Please implement BM25 retriever or adjust impmorts"
        )
    sparse_results = retriever_bm25_as_dicts(query_text=query_text, top_k=sparse_k, paper_id=paper_id)

    print(
        f"[HYBRID RETRIEVER]    DENSE RESULTS : {len(dense_results)}, "
        f"Sparse Results: {len(sparse_results)}"
    )


    hybrid_results = _merge_results_rrf(
        dense_results=dense_results,
        sparse_results=sparse_results,
        top_k=top_k
    )

    print(f"[HYRBID RETRIEVER]  HYRBID RESULTS: {len(hybrid_results)}")
    return hybrid_results

def retrieve_hybrid(
    query_text: str,
    top_k: int = VECTOR_STORE_CONFIG["default_top_k"],
    dense_k: Optional[int] = None,
    sparse_k: Optional[int] = None,
) -> List[RetrieverChunk]:
    
    hybrid_dicts = retriever_hybrid_as_dicts(
        query_text=query_text,
        top_k=top_k,
        dense_k=dense_k,
        sparse_k=sparse_k,
    )

    chunks: List[RetrieverChunk] = []
    for res in hybrid_dicts:
        chunk = RetrieverChunk(
            chunk_id=res.get("chunk_id", ""),
            text=res.get("text", ""),
            source_doc=res.get("source_doc", "unknown"),
            metadata=res.get("metadata") or {},
            score=res.get("score", 0.0),
        )

        chunks.append(chunk)

    return chunks


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("USAGE: python hybrid_retriever.py '<YOUR QUESTIONS>'")

    q = sys.argv[1]
    try:
        results = retriever_hybrid_as_dicts(
            query_text=q, 
            top_k=VECTOR_STORE_CONFIG['default_top_k']
        )
    except RuntimeError as e:
        print("[HYBRID RETRIEVER] ERROR: ", e)
        sys.exit(1)

    print("\n [HYBRID RETRIEVER] RESULTS: ")
    for i, r in enumerate(results, start=1):
        print(f"\n#{i} | ID={r.get('chunk_id')} | source={r.get('source_doc')}")
        print(f"Hybrid score : {r.get('hybrid_score'):.6f}")
        print(f"Dense score? : {r.get('score')}")
        print(f"Metadata     : {r.get('metadata')}")
        print(f"Text preview : { (r.get('text') or '')[:200] }...")