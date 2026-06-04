from typing import List, Dict, Any
import sys
from src.vector_store import query_collection
from src.config.settings import VECTOR_STORE_CONFIG

class RetrieverChunk:
    """
    A clean, Structured representation of a single retrieved chunk.

    Attributes:
    chunk_id            : Chroma doc ID
    text                : Chunk's raw text content
    source_doc          : name of the paper
    metadata
    score               : similarity score
    """

    def __init__(
            self,
            chunk_id:str,
            text:str,
            source_doc:str,
            metadata:Dict[str, Any],
            score: float,
    ) -> None:
        self.chunk_id = chunk_id
        self.text = text
        self.source_doc = source_doc
        self.metadata = metadata
        self.score = score

    def __repr__(self) ->str:
        return(
            f"RetrievedChunk("
            f"id={self.chunk_id!r}, "
            f"source={self.source_doc!r}, "
            f"score={self.score:.4f}, "
            f"text_preview={self.text[:80]!r}...)"
        )


def retriever(
        query_text: str,
        top_k: int=VECTOR_STORE_CONFIG["default_top_k"]
) -> List[RetrieverChunk]:
    if not query_text.strip():
        raise ValueError("Query text must not be empty.")
    
    print(f"\n[RETRIEVER]   Querying for : {query_text!r} (top_k = {top_k}) ")

    try: 
        raw_result = query_collection(
            query_text=query_text,
            top_k=top_k
        )
    except Exception as e:
        raise RuntimeError(f"[RETRIEVER]    Chroma Query Failed: {e}")
    


    return _parse_chroma_result(raw_result)

def _parse_chroma_result(raw_result : Dict[str, Any]) -> List[RetrieverChunk]:
    chunks: List[RetrieverChunk] = []

    try:
        # Extract with validation
        ids_list = raw_result.get("ids", [[]])
        docs_list = raw_result.get("documents", [[]])
        metas_list = raw_result.get("metadatas", [[]])
        dists_list = raw_result.get("distances", [[]])
        
        # Validate structure
        if not all(isinstance(x, list) for x in [ids_list, docs_list, metas_list, dists_list]):
            raise TypeError("Chroma response lists are not in expected format")
        
        if not ids_list:  # If empty
            print("[RETRIEVER] No results from query")
            return []
        
        # Now unpack safely
        ids = ids_list[0] if ids_list else []
        documents = docs_list[0] if docs_list else []
        metadatas = metas_list[0] if metas_list else []
        distances = dists_list[0] if dists_list else []
        
        # Validate all have same length
        if not (len(ids) == len(documents) == len(metadatas) == len(distances)):
            raise ValueError(f"Mismatched result lengths: {len(ids)}, {len(documents)}, {len(metadatas)}, {len(distances)}")
        
    except (IndexError, TypeError, ValueError) as e:
        raise RuntimeError(f"[RETRIEVER] Failed to parse Chroma response: {e}. Raw result: {raw_result}")

    for chunk_id, text, meta, dist in zip(ids, documents, metadatas, distances):
        source_doc = meta.get(
            "source_doc", "unknown"
        ) if meta else "unknown"

        chunk = RetrieverChunk(
            chunk_id=chunk_id,
            text=text or "",
            source_doc=source_doc,
            metadata=meta or {},
            score=dist,
        )

        chunks.append(chunk)

    
    print(f"[RETRIEVER]     Retrieved {len(chunks)} chunk(s).")

    return chunks
def print_retrieved_chunks(chunks: List[RetrieverChunk]) -> None:
    """
    Print retrieved chunks in a human-readable format.
    Useful for testing retrieval before integrating the LLM.
    """
    if not chunks:
        print("[Retriever] No chunks retrieved.")
        return

    for i, chunk in enumerate(chunks, start=1):
        print(f"\n{'='*60}")
        print(f"Chunk {i} | ID: {chunk.chunk_id}")
        print(f"Source  : {chunk.source_doc}")
        print(f"Score   : {chunk.score:.4f} (lower = more similar)")
        print(f"Metadata: {chunk.metadata}")
        print(f"Text Preview:\n{chunk.text[:300]}...")
    print(f"\n{'='*60}")



def retrieve_as_dicts(
    query_text: str,
    top_k: int = VECTOR_STORE_CONFIG["default_top_k"],
) -> List[Dict[str, Any]]:
    """
    Same as retrieve(), but returns plain dicts instead of RetrievedChunk objects.
    Easier to pass to prompt-construction functions.

    Returns:
        List[Dict[str, Any]]: Each dict has keys:
            chunk_id, text, source_doc, metadata, score
    """
    chunks = retriever(query_text=query_text, top_k=top_k)
    return [
        {
            "chunk_id": c.chunk_id,
            "text": c.text,
            "source_doc": c.source_doc,
            "metadata": c.metadata,
            "score": c.score,
        }
        for c in chunks
    ]


# -------------------------------------------------------------------
# Quick manual test
# python src/retrieval/retriever.py "What is the attention mechanism?"
# -------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python retriever.py '<your question>'")
        sys.exit(1)

    query = sys.argv[1]
    results = retriever(query_text=query, top_k=VECTOR_STORE_CONFIG["default_top_k"])
    print_retrieved_chunks(results)