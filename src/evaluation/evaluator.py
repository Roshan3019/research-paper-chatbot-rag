from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import statistics


@dataclass
class RetrievalMetrics:
    precision_at_k: float
    recall_at_k: float
    mrr: float
    ndcg_at_k: float


def _calculate_precision_at_k(
    retrieved_ids: List[str],
    relevant_ids: List[str],
    k: int
) -> float:
    if k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    relevant_set = set(relevant_ids)
    hits = sum(1 for rid in top_k if rid in relevant_set)
    return hits / len(top_k)


def _calculate_recall_at_k(
    retrieved_ids: List[str],
    relevant_ids: List[str],
    k: int
) -> float:
    if k <= 0 or not relevant_ids:
        return 0.0
    top_k = retrieved_ids[:k]
    relevant_set = set(relevant_ids)
    hits = sum(1 for rid in top_k if rid in relevant_set)
    return hits / len(relevant_ids)


def _calculate_mrr(
    retrieved_ids: List[str],
    relevant_ids: List[str]
) -> float:
    relevant_set = set(relevant_ids)
    for rank, rid in enumerate(retrieved_ids, start=1):
        if rid in relevant_set:
            return 1.0 / rank
    return 0.0


def _calculate_ndcg_at_k(
    retrieved_ids: List[str],
    relevant_ids: List[str],
    k: int
) -> float:
    if k <= 0:
        return 0.0

    top_k = retrieved_ids[:k]
    relevant_set = set(relevant_ids)

    ideal_hits = min(len(relevant_set), k)
    idcg = sum(1.0 / (i + 1) if (i < ideal_hits) else 0
               for i in range(k))

    dcg = sum(1.0 / (i + 1) if rid in relevant_set else 0
              for i, rid in enumerate(top_k))

    if idcg == 0:
        return 0.0
    return dcg / idcg


def evaluate_retrieval(
    retrieved_chunks: List[Dict[str, Any]],
    relevant_chunk_ids: List[str],
    k: int = 5
) -> RetrievalMetrics:
    retrieved_ids = [c.get("chunk_id") for c in retrieved_chunks if c.get("chunk_id")]

    return RetrievalMetrics(
        precision_at_k=_calculate_precision_at_k(retrieved_ids, relevant_chunk_ids, k),
        recall_at_k=_calculate_recall_at_k(retrieved_ids, relevant_chunk_ids, k),
        mrr=_calculate_mrr(retrieved_ids, relevant_chunk_ids),
        ndcg_at_k=_calculate_ndcg_at_k(retrieved_ids, relevant_chunk_ids, k),
    )


def evaluate_retrieval_list(
    retrieved_chunks: List[Dict[str, Any]],
    relevant_chunk_ids: List[str],
    k_values: List[int] = None
) -> Dict[str, RetrievalMetrics]:
    if k_values is None:
        k_values = [1, 3, 5, 10]

    return {f"@{k}": evaluate_retrieval(retrieved_chunks, relevant_chunk_ids, k)
            for k in k_values}


@dataclass
class RetrievalComparison:
    method: str
    metrics: RetrievalMetrics


def compare_retrieval_methods(
    query_text: str,
    relevant_chunk_ids: List[str],
    top_k: int = 5,
    paper_id: Optional[str] = None
) -> Dict[str, RetrievalComparison]:
    from src.retrieval.retriever import retrieve_as_dicts
    from src.retrieval.bm25_retriever import retriever_bm25_as_dicts
    from src.retrieval.hybrid_retriever import retriever_hybrid_as_dicts

    results = {}

    dense = retrieve_as_dicts(query_text=query_text, top_k=top_k * 2, paper_id=paper_id)
    results["dense"] = RetrievalComparison(
        method="dense",
        metrics=evaluate_retrieval(dense[:top_k], relevant_chunk_ids, top_k)
    )

    try:
        sparse = retriever_bm25_as_dicts(query_text=query_text, top_k=top_k * 2, paper_id=paper_id)
        results["sparse"] = RetrievalComparison(
            method="sparse",
            metrics=evaluate_retrieval(sparse[:top_k], relevant_chunk_ids, top_k)
        )
    except RuntimeError:
        pass

    try:
        hybrid = retriever_hybrid_as_dicts(query_text=query_text, top_k=top_k, paper_id=paper_id)
        results["hybrid"] = RetrievalComparison(
            method="hybrid",
            metrics=evaluate_retrieval(hybrid, relevant_chunk_ids, top_k)
        )
    except RuntimeError:
        pass

    return results


def print_metrics_comparison(comparison: Dict[str, RetrievalComparison]) -> None:
    print("\n" + "=" * 60)
    print("RETRIEVAL METHODS COMPARISON")
    print("=" * 60)

    for method_name, comp in comparison.items():
        m = comp.metrics
        print(f"\n{comp.method.upper()}:")
        print(f"  Precision@{5}: {m.precision_at_k:.4f}")
        print(f"  Recall@{5}:    {m.recall_at_k:.4f}")
        print(f"  MRR:         {m.mrr:.4f}")
        print(f"  nDCG@{5}:    {m.ndcg_at_k:.4f}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python evaluator.py '<query>' [relevant_chunk_id1] [relevant_chunk_id2] ...")
        print("Example: python evaluator.py 'attention mechanism' paperA_0 paperB_5")
        sys.exit(1)

    query = sys.argv[1]
    relevant_ids = sys.argv[2:] if len(sys.argv) > 2 else []

    if not relevant_ids:
        print("[EVALUATOR] No relevant IDs provided - using empty list (precision/recall will be 0)")
        relevant_ids = []

    comparison = compare_retrieval_methods(query, relevant_ids, top_k=5)
    print_metrics_comparison(comparison)