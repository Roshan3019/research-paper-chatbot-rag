#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from src.retrieval.hybrid_retriever import retriever_hybrid_as_dicts
from src.retrieval.chat_logic import answer_question_with_hf
from src.evaluation.evaluator import compare_retrieval_methods, print_metrics_comparison


def main():
    parser = argparse.ArgumentParser(description="RAG System Query & Evaluate")
    parser.add_argument("query", help="Query text")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    parser.add_argument("--evaluate", action="store_true", help="Run evaluation")
    parser.add_argument("--ground-truth", nargs="+", help="Relevant chunk IDs for evaluation")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM generation")
    
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"QUERY: {args.query}")
    print(f"{'='*60}")

    results = retriever_hybrid_as_dicts(
        query_text=args.query,
        top_k=args.top_k
    )

    print(f"\nRETRIEVED CHUNKS ({len(results)}):")
    for i, r in enumerate(results, 1):
        score = r.get("hybrid_score", 0) or r.get("score", 0)
        print(f"  {i}. {r['chunk_id'][:40]}... [score: {score:.4f}]")
        preview = (r.get("text", "") or "")[:100]
        print(f"     {preview}...")

    if args.evaluate:
        relevant = args.ground_truth or []
        comparison = compare_retrieval_methods(
            query_text=args.query,
            relevant_chunk_ids=relevant,
            top_k=args.top_k
        )
        print_metrics_comparison(comparison)
    
    if not args.no_llm:
        print(f"\n{'='*60}")
        print("GENERATING ANSWER...")
        print(f"{'='*60}")
        
        result = answer_question_with_hf(
            query_text=args.query,
            top_k=args.top_k
        )
        
        print(f"\nANSWER:\n{result['answer']}")


if __name__ == "__main__":
    main()