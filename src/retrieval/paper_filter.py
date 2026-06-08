import re
from typing import List, Dict, Any, Optional

ARXIV_ID_PATTERN = re.compile(r"\b(\d{4}\.\d{5}v\d+)\b")

def extract_paper_id(query_text: str) -> Optional[str]:
    """
    Extract arXiv paper ID from query text.
    
    Matches patterns like: 2510.06186v2, 2506.13774v2, etc.
    
    Returns:
        The paper ID if found, None otherwise.
    """
    match = ARXIV_ID_PATTERN.search(query_text)
    if match:
        paper_id = match.group(1)
        print(f"[PAPER FILTER] Detected paper ID: {paper_id}")
        return paper_id
    return None

def filter_chunks_by_paper(
    chunks: List[Dict[str, Any]], 
    paper_id: str
) -> List[Dict[str, Any]]:
    """
    Filter chunks to only include those from the specified paper.
    
    Args:
        chunks: List of chunk dicts with 'source_doc' key.
        paper_id: The arXiv paper ID to filter by.
    
    Returns:
        Filtered list containing only chunks where source_doc == paper_id.
    """
    filtered = [c for c in chunks if c.get("source_doc") == paper_id]
    print(f"[PAPER FILTER] Filtered {len(filtered)} / {len(chunks)} chunks matching paper '{paper_id}'")
    return filtered

if __name__ == "__main__":
    # Test cases
    test_queries = [
        "What is the main contribution of paper 2510.06186v2?",
        "Tell me about RECODE-H benchmark",
        "What does 2511.03497v1 discuss?",
        "No paper ID here",
    ]
    for q in test_queries:
        result = extract_paper_id(q)
        print(f"Query: '{q}' -> Paper ID: {result}")