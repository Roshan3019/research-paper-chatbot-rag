# import pymupdf
import os
from typing import List, Tuple
import fitz #pymupdf

def pdf_loader(pdf_path: str) -> fitz.Document:
    #validate path exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")
    
    #validate file extensions
    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError(f"File is not a PDF: {pdf_path}")
    
    #attempt to open the pdfs
    try: 
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF '{pdf_path}': {e}")
    
    #log basic metadata
    print(f"\n[PDF LOADER] Successfully loaded: {os.path.basename(pdf_path)}")

    print(f"    PAGES   : {doc.page_count}")
    print(f"    Title   : {doc.metadata.get('title', 'N/A')}")
    print(f"    Author  : {doc.metadata.get('author', 'N/A')}")
    print(f"    Created : {doc.metadata.get('creationDate', 'N/A')}")
    print(f"    Producer: {doc.metadata.get('producer', 'N/A')}")

    return doc

def load_all_pdfs(folder_path: str) -> List[Tuple[str, fitz.Document]]:

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    pdf_files = [
        f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")
    ]
    if not pdf_files:
        print(f"[PDF Loader] NO pdf files found in : {folder_path}")
        return []
    print(f"\n [PDF LOADER] FOUND {len(pdf_files)} PDF(s) in '{folder_path}'")

    loaded_docs = []
    for filename in pdf_files:
        full_path = os.path.join(folder_path, filename)
        try:
            doc = pdf_loader(full_path)
            loaded_docs.append((filename, doc))
        except (FileNotFoundError, ValueError, RuntimeError) as e:
            print(f"[WARNING] Skipping '{filename}' : {e}")
        
    return loaded_docs


# quick manual test - run this file directly to verify it works
# if __name__ == "__main__":
#     import sys

#     #usage: python pdf_loader.py <path_to_pdf>

#     if len(sys.argv) < 2:
#         print("Usage: Python pdf_loader.py <path_to_pdf>")
#         sys.exit(1)
#     test_path = sys.argv[1]
#     document = pdf_loader(test_path)

#     print(f"\n[TEST] Document has {document.page_count} pages(s)")
#     print(f"[TEST] First Page object: {document[0]}")
#     document.close()
# for all pdf 
if __name__ == "__main__":
    from src.config.settings import INPUT_PDFS_DIR

    docs = load_all_pdfs(INPUT_PDFS_DIR)

    print(f"\nLoaded {len(docs)} PDF(s)")

    for _, doc in docs:
        doc.close()