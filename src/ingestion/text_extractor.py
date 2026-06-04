import os
from typing import List, Tuple, Iterator
import fitz

def extract_page_text(page: fitz.Page) -> str:
    return page.get_text("text", sort=True)

def iter_document_pages(
        doc: fitz.Document,
) -> Iterator[Tuple[int, str]]:
    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        page_text = extract_page_text(page)
        yield page_index, page_text

def extract_and_save_document_text(
        doc: fitz.Document,
        original_pdf_path: str,
        output_dir:str,
        include_page_markers: bool=True,
) -> str:
    
    os.makedirs(output_dir, exist_ok=True)

    pdf_filename = os.path.basename(original_pdf_path)
    base_name, _ = os.path.splitext(pdf_filename)
    output_path = os.path.join(
        output_dir,
        f"{base_name}_extracted.txt"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        for page_index, page_text in iter_document_pages(doc):
            if include_page_markers:
                marker = (
                    f"\n\n=== Page "
                    f"{page_index + 1} / {doc.page_count} "
                    f"({base_name}) ===\n\n"
                )
                f.write(marker)
            f.write(page_text)
    print(
        f"[TEXT EXTRACTOR] Saved extracted text to: "
        f"{output_path}"
    )
    return output_path
    
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python text_extractor.py <path_to_pdf> <output_dir>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]

    # Lazy import to avoid circulars if you later reorganize
    from pdf_loader import pdf_loader  

    doc = pdf_loader(pdf_path)
    try:
        txt_path = extract_and_save_document_text(
            doc,
            original_pdf_path=pdf_path,
            output_dir=output_dir,
            include_page_markers=True,
        )
        print(f"[Test] Extraction finished. Output file: {txt_path}")
    finally:
        doc.close()



#===========VERSION-0=============
# def extract_page_text(page: fitz.Page)->str:
#     text = page.get_text("text", sort=True)
#     return text

# def extract_document_text(
#         doc: fitz.Document,     #Open PyMuPDF document
#         doc_name: str | None=None,  #optional logic name
#         include_page_markers: bool=True,   
# ) -> Tuple[str, List[Tuple[int, str]]]:
#     if doc_name is None:
#         doc_name = "document"
    
#     page_texts: List[Tuple[int, str]] = []
#     parts: List[str] = []

#     for page_index in range(doc.page_count):
#         page = doc.load_page(page_index)
#         page_text = extract_page_text(page)
#         #store page-wise text in memory
#         page_texts.append((page_index, page_text))


#         #append to combined text with optional markers
#         if include_page_markers:
#             marker = f"\n\n=== Page {page_index + 1} / {doc.page_count} ({doc_name}) ===\n\n"

#             parts.append(marker)

#         parts.append(page_text)

#     combined_text = "".join(parts)
#     return combined_text, page_texts

# def save_extracted_text(
#         combined_text:str,
#         output_dir: str,
#         output_filename: str,
# ) -> str:
#     os.makedirs(output_dir, exist_ok=True)

#     if not output_filename.lower().endswith(".txt"):
#         output_filename = output_filename + ".txt"
    
#     output_path = os.path.join(output_dir, output_filename)

#     with open(output_path, "w", encoding="utf-8") as f:
#         f.write(combined_text)
    
#     print(f"[TEXT EXTRACTOR] Saved extracted text to: {output_path}")

#     return output_path

#extract text from all pages
    # combined_text, _ = extract_document_text(
    #     doc, 
    #     doc_name=doc_name,
    #     include_page_markers=include_page_markers
    # )
    # #save to text file

    # output_filename = f"{base_name}_extracted"
    # output_path = save_extracted_text(combined_text, output_dir, output_filename)

    # return output_path