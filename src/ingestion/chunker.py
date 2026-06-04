import re
from typing import List, Dict, Any

def split_text_into_sentences(text:str) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []
    
    #simple split on sentence-ending punctuation
    #keep the delimiter attached to the sentences

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
    #add any trailing text without punctuation as a sentence

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
        sentence = sentence.strip() #first iter ex : "Hello." "I love ML!" "YEAH?"
        if not sentence:
            continue


        # +1 for space/newline separator
        sentence_length = len(sentence) +1  #6 + 1 = 7          sen_len = 10+1 = 11  SEN_LEN = 5+1 = 6

        if current_length + sentence_length > target_chars and current_sentences:   #7 > 20  (7+ 11 = 18 > 20) (18 + 6 = 24 > 20)
            #close current chunk
            chunk_text = " ".join(current_sentences).strip() #"HELLO. I LOVE ML!"
            chunks.append(chunk_text)   #chunks = "hello. I love Ml"

            #prepare next chunk with overlap
            if overlap_sentences > 0:       #1 > 0
                #keep last N sentences as overlap
                overlap=current_sentences[-overlap_sentences:] #overlap = "I Love ML!"
                current_sentences = overlap.copy()  #current_sentence = ["I love Ml1"]
                current_length = sum(len(s) + 1 for s in current_sentences) #cur_len = 10+1 = 11
            else:
                current_sentences = []
                current_length = 0
            
        #add sentence to current chunk
        current_sentences.append(sentence)          #current_sentences = ["Hello.", "I love ML!"]
                                                    # after if statement, current_sentence = ["I love Ml1", "YEAH!"]
        current_length+= sentence_length              # cur_len = 0 + 7 = 7 + 11 = 18

    #add any remaining sentences as final chunk
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


#manual text

if __name__ =="__main__":
    sample_text = (
        # "This is a sample paragraph. It is meant to demonstrate sentence-based chunking. "
        # "Chunking is important in RAG systems. It helps control context size and retrieval quality. "
        # "You can adjust target_chars and overlap_sentences to tune behavior."
        "Hello. I love ML! YEAH?"
    )

    result = chunk_document_text(
        text=sample_text,
        source_doc="sample_doc",
        target_chars=20,
        overlap_sentences=1,
    )


    for c in result:
        print(f"\n Chunk {c['id']} ({len(c['text'])} chars):\n{c['text']}")
