# Evaluation Phase - RAG System

## Overview

The evaluation phase measures retrieval quality using standard IR metrics.

## Testing Steps

### 1. Basic Metrics Test
```bash
python3 -c "
from src.evaluation import evaluate_retrieval

# With mock data
retrieved = [{'chunk_id': 'a'}, {'chunk_id': 'b'}, {'chunk_id': 'c'}]
relevant = ['a', 'c']
metrics = evaluate_retrieval(retrieved, relevant, k=3)
print(f'P@3: {metrics.precision_at_k:.2f}, R@3: {metrics.recall_at_k:.2f}')
"
```

### 2. Retrieval Method Comparison
```bash
python3 -c "
from src.evaluation import compare_retrieval_methods, print_metrics_comparison

comparison = compare_retrieval_methods(
    query_text='attention mechanism',
    relevant_chunk_ids=[],  # Empty = no ground truth
    top_k=5
)
print_metrics_comparison(comparison)
"
```

### 3. Full Benchmark
Create `data/eval_queries.json`:
```json
{
  "queries": [
    {"query": "attention mechanism", "relevant_chunk_ids": ["paperA_0"]},
    {"query": "benchmark", "relevant_chunk_ids": ["paperB_5"]}
  ]
}
```

Run benchmark:
```bash
python3 -c "
import json
from src.evaluation import run_benchmark, print_benchmark_summary, save_benchmark_results

with open('data/eval_queries.json') as f:
    data = json.load(f)

results = run_benchmark(data['queries'], top_k=5)
print_benchmark_summary(results)
save_benchmark_results(results, 'data/eval_results.json')
"
```

## Impact on Project

1. **Quantitative Measurement**: Precision@K, Recall@K, MRR, nDCG assess retrieval effectiveness
2. **Method Comparison**: Compare Dense (Chroma) vs Sparse (BM25) vs Hybrid (RRF)
3. **Parameter Optimization**: Tune RRF_K, dense_k, sparse_k based on metrics
4. **Regression Detection**: Monitor quality degradation over time