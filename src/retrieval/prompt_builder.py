from typing import List, Dict, Any, Optional
from src.config.settings import VECTOR_STORE_CONFIG

def build_content_block(
        chunks: List[Dict[str, Any]],
        max_chunks: int = VECTOR_STORE_CONFIG["default_top_k"],
        max_chars_per_chunk: Optional[int] = None,
) -> str:
    
    if not chunks:
        return "No content available.\n"
    
    selected = chunks[:max_chunks]

    context_sections: List[str] = []
    for idx, c in enumerate(selected, start=1):
        text = c['text'] or ""
        if max_chars_per_chunk is not None and len(text) > max_chars_per_chunk:
            text = text[:max_chars_per_chunk] + "..."
        

        source_doc = c.get("source_doc", "unknown")
        score = c.get("score", None)
        metadata = c.get("metadata", {}) or {}

        header_lines = [
            f"[Context {idx}]",
            f"Source Document   :{source_doc}",
            f"Chunk ID          :{c.get('chunk_id', 'unknown')}",
        ]

        if score is not None:
            header_lines.append(f"Similarity Score: {score:.4f} (lower = closer)")

        if metadata:
            header_lines.append(f"Metadata:\n {metadata}")
        header = "\n".join(header_lines)

        section = f"{header}\n\n{text}\n"
        context_sections.append(section)
    return "\n---\n".join(context_sections) + "\n"

def build_plain_prompt(
        query_text:str,
        chunks:List[Dict[str, Any]],
        max_chunks: int = VECTOR_STORE_CONFIG['default_top_k'],
        max_chars_per_chunk: Optional[int] = None,
) -> str:
    
    instruction = (
        "You are a helpful research assistant. "
        "Your task is to answer questions based only on the provided context "
        "from academic research papers. \n\n"
        "Guidelines:\n"
         "- If the answer is clearly stated in the context, explain it concisely.\n"
        "- When possible, refer to the source document name and any available "
        "page / section hints.\n"
        "- If the answer CANNOT be found in the context, say: "
        "\"I cannot find this information in the provided papers.\"\n"
        "- Do NOT invent facts or rely on external knowledge.\n"
    )

    context_block = build_content_block(
        chunks=chunks,
        max_chunks=max_chunks,
        max_chars_per_chunk=max_chars_per_chunk,
    )

    questions_block = f"User Questions: \n{query_text}\n"

    prompt=(
        "INSTRUCTIONS: \n"
        f"{instruction}\n"
        "CONTEXT:\n"
        f"{context_block}\n"
        f"{questions_block}"
    )

    return prompt
def build_chat_prompt(
        query_text: str,
        chunks: List[Dict[str, Any]],
        max_chunks: int = VECTOR_STORE_CONFIG['default_top_k'],
        max_chars_per_chunk: Optional[int] = None,
) -> List[Dict[str, str]]:
    system_message = (
        "You are a helpful research assistant specialized in academic papers.\n"
        "You must answer questions using ONLY the provided context.\n"
        "If the answer is not in the context, explicitly say so.\n"
        "Prefer concise, precise explanations and mention the source document "
        "when possible."
    )

    context_block = build_content_block(
        chunks = chunks,
        max_chunks=max_chunks,
        max_chars_per_chunk=max_chars_per_chunk,
    )

    user_content = (
        "Here is the context from the papers:\n\n"
        f"{context_block}\n"
        "Now answer this question based ONLY on the context above:\n"
        f"{query_text}\n"
    )
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_content},
    ]
    return messages
    

if __name__ =="__main__":
    fake_chunks = [
        {
            "chunk_id": "paperA_0",
            "text": "This paper introduces a novel attention-based architecture for sequence modeling.",
            "source_doc": "paperA",
            "metadata": {"pages": "1-2"},
            "score": 0.12,
        },
        {
            "chunk_id": "paperA_1",
            "text": "The loss function used is cross-entropy over the token vocabulary.",
            "source_doc": "paperA",
            "metadata": {"pages": "3"},
            "score": 0.25,
        },
    ]
    q = "What architecture does the paper introduce, and what loss function does it use?"
    prompt = build_plain_prompt(q, fake_chunks, max_chunks=2)
    print(prompt)