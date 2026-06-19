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