from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import statistics
from pathlib import Path

from src.config.settings import EVALUATION_CONFIG
from .evaluator import evaluate_retrieval, compare_retrieval_methods


@dataclass
class BenchmarkResult:
    query: str
    method: str
    precision: float
    recall: float
    mrr: float
    ndcg: float


def run_benchmark(
    queries_with_ground_truth: List[Dict[str, Any]],
    top_k: int = None,
    paper_id: Optional[str] = None,
) -> List[BenchmarkResult]:
    if top_k is None:
        top_k = EVALUATION_CONFIG.get("top_k", 5)

    results: List[BenchmarkResult] = []

    for item in queries_with_ground_truth:
        query = item["query"]
        relevant_ids = item.get("relevant_chunk_ids", [])

        comparison = compare_retrieval_methods(
            query_text=query,
            relevant_chunk_ids=relevant_ids,
            top_k=top_k,
            paper_id=paper_id,
        )

        for method_name, comp in comparison.items():
            results.append(BenchmarkResult(
                query=query,
                method=comp.method,
                precision=comp.metrics.precision_at_k,
                recall=comp.metrics.recall_at_k,
                mrr=comp.metrics.mrr,
                ndcg=comp.metrics.ndcg_at_k,
            ))

    return results


def print_benchmark_summary(results: List[BenchmarkResult]) -> None:
    methods = set(r.method for r in results)

    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)

    for method in sorted(methods):
        method_results = [r for r in results if r.method == method]

        avg_precision = statistics.mean(r.precision for r in method_results)
        avg_recall = statistics.mean(r.recall for r in method_results)
        avg_mrr = statistics.mean(r.mrr for r in method_results)
        avg_ndcg = statistics.mean(r.ndcg for r in method_results)

        print(f"\n{method.upper()}:")
        print(f"  Queries:     {len(method_results)}")
        print(f"  Avg P@{5}:   {avg_precision:.4f}")
        print(f"  Avg Recall:  {avg_recall:.4f}")
        print(f"  Avg MRR:     {avg_mrr:.4f}")
        print(f"  Avg nDCG:    {avg_ndcg:.4f}")


def save_benchmark_results(results: List[BenchmarkResult], output_path: str) -> None:
    data = [
        {
            "query": r.query,
            "method": r.method,
            "precision": r.precision,
            "recall": r.recall,
            "mrr": r.mrr,
            "ndcg": r.ndcg,
        }
        for r in results
    ]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"[BENCHMARK] Results saved to {output_path}")


if __name__ == "__main__":
    import sys

    sample_queries = [
        {
            "query": "attention mechanism",
            "relevant_chunk_ids": [],
        },
        {
            "query": "RECODE-H benchmark",
            "relevant_chunk_ids": [],
        },
    ]

    results = run_benchmark(sample_queries, top_k=5)
    print_benchmark_summary(results)

    if len(sys.argv) > 1:
        save_benchmark_results(results, sys.argv[1])