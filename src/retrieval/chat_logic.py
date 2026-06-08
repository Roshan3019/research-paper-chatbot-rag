from typing import Dict, Any, Optional
import sys

from transformers import pipeline

from src.retrieval.hybrid_retriever import retriever_hybrid_as_dicts
from src.retrieval.prompt_builder import build_plain_prompt
from src.config.settings import (
    VECTOR_STORE_CONFIG,
    LLM_CONFIG,
)

# Module-level cache for LLM client to avoid reloading
_llm_client_cache = {}


class HFChatClient:
    def __init__(
        self,
        model_name: str = LLM_CONFIG['model_name'],
        max_new_tokens: int = LLM_CONFIG["max_new_tokens"],
        temperature: float = LLM_CONFIG["temperature"],
    ) -> None:

        self.pipeline = pipeline(
            task="text-generation",
            model=model_name,
        )

        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.model_name = model_name

    def generate(self, prompt: str) -> str:

        response = self.pipeline(
            prompt,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            do_sample=False,
            return_full_text=False
        )

        return response[0]["generated_text"].strip()


def _get_or_create_llm_client(model_name: str) -> HFChatClient:
    """
    Get cached LLM client or create and cache a new one.
    Avoids reloading model on every query.
    """
    if model_name not in _llm_client_cache:
        print(f"[QA] Loading LLM model: {model_name}")
        _llm_client_cache[model_name] = HFChatClient(model_name=model_name)
        print(f"[QA] Model loaded and cached")
    return _llm_client_cache[model_name]


def answer_question_with_hf(
    query_text: str,
    top_k: int = VECTOR_STORE_CONFIG["default_top_k"],
    max_chunks: Optional[int] = None,
    max_chars_per_chunk: Optional[int] = None,
    model_name: str = LLM_CONFIG["model_name"],
    dense_k: Optional[int] = None,
    sparse_k: Optional[int] = None,
    paper_id: Optional[str] = None,
) -> Dict[str, Any]:

    if not query_text.strip():
        raise ValueError("Query text must not be empty.")

    print(f"\n[QA] Question: {query_text}")

    chunks = retriever_hybrid_as_dicts(
        query_text=query_text,
        top_k=top_k,
        dense_k=dense_k,
        sparse_k=sparse_k,
        paper_id=paper_id,
    )

    if max_chunks is None:
        max_chunks = top_k

    prompt = build_plain_prompt(
        query_text=query_text,
        chunks=chunks,
        max_chunks=max_chunks,
        max_chars_per_chunk=max_chars_per_chunk,
    )

    client = _get_or_create_llm_client(model_name)

    answer = client.generate(prompt)

    return {
        "answer": answer,
        "chunks_used": chunks[:max_chunks],
        "prompt": prompt,
        "model_name": model_name,
    }


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print(
            "python -m src.retrieval.chat_logic "
            "\"What is the main contribution of these papers?\""
        )
        sys.exit(1)

    question = sys.argv[1]

    result = answer_question_with_hf(
        query_text=question,
        top_k=VECTOR_STORE_CONFIG["default_top_k"],
        max_chunks=None,
        max_chars_per_chunk=None,
        model_name=LLM_CONFIG["model_name"],
    )

    print("\n" + "=" * 80)
    print("[QA] MODEL")
    print(result["model_name"])

    print("\n" + "=" * 80)
    print("[QA] ANSWER")
    print(result["answer"])

    print("\n" + "=" * 80)