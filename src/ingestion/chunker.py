import re
from typing import List, Dict, Any

def split_text_into_sentences(text:str) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []
    
    parts = re.split(r"([.!?])", text)

    sentences: List[str] = []
    current = ""

    for part in parts:
        if not part:
            continue
        current+=part
        if part in ".!?":
            sentences.append(current.strip())
            current = ""
    
    if current.strip():
        sentences.append(current.strip())

    return sentences

def build_chunks_from_sentences(
        sentences: List[str],
        target_chars : int,
        overlap_sentences: int = 12,
) -> List[str]:
    chunks: List[str] = []
    current_sentences: List[str] = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        sentence_length = len(sentence) + 1

        if current_length + sentence_length > target_chars and current_sentences:
            chunk_text = " ".join(current_sentences).strip()
            chunks.append(chunk_text)

            if overlap_sentences > 0:
                overlap=current_sentences[-overlap_sentences:]
                current_sentences = overlap.copy()
                current_length = sum(len(s) + 1 for s in current_sentences)
            else:
                current_sentences = []
                current_length = 0
        
        current_sentences.append(sentence)
        current_length+= sentence_length

    if current_sentences:
        chunk_text = " ".join(current_sentences).strip()
        chunks.append(chunk_text)

    return chunks

def chunk_document_text(
        text:str,
        source_doc:str,
        target_chars:int = 1000,
        overlap_sentences: int=1,
) -> List[Dict[str, Any]]:
    sentences = split_text_into_sentences(text)
    if not sentences:
        return []
    
    chunk_texts = build_chunks_from_sentences(
        sentences=sentences,
        target_chars=target_chars,
        overlap_sentences=overlap_sentences
    )

    chunks: List[Dict[str, Any]] = []
    for idx, chunk_text in enumerate(chunk_texts):
        chunk = {
            "id" : idx,
            "text" : chunk_text,
            "source_doc": source_doc,
            "metadata" : {},
        }
        chunks.append(chunk)
    return chunks

if __name__ =="__main__":
    sample_text = "Hello. I love ML! YEAH?"

    result = chunk_document_text(
        text=sample_text,
        source_doc="sample_doc",
        target_chars=20,
        overlap_sentences=1,
    )

    for c in result:
        print(f"\n Chunk {c['id']} ({len(c['text'])} chars):\n{c['text']}")
