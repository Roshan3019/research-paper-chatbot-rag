from typing import List, Dict, Any

from .pdf_loader import load_all_pdfs
from .text_extractor import extract_and_save_document_text
from .chunker import chunk_document_text
from src.config import settings
from src.vector_store import add_chunks_to_collection

def build_chunks_for_all_pdfs() -> List[Dict[str, Any]]:
    all_chunks: List[Dict[str, Any]] = []

    pdf_entries = load_all_pdfs(str(settings.INPUT_PDFS_DIR))
    if not pdf_entries:
        print("[INGESTION] No PDFS to process.")
        return all_chunks
    
    for filename, doc in pdf_entries:
        pdf_path = settings.INPUT_PDFS_DIR / filename
        base_name = pdf_path.stem

        try:
            print(f"\n[INGESTION]   PROCESSING PDF: {filename}")

            txt_path = extract_and_save_document_text(
                doc, 
                original_pdf_path=str(pdf_path),
                output_dir=str(settings.EXTRACTED_TEXT_DIR),
                include_page_markers=True,
            )

            with open(txt_path, "r", encoding="utf-8") as f:
                full_text = f.read()

            chunks = chunk_document_text(
                text=full_text,
                source_doc=base_name,
                target_chars=settings.CHUNKER_CONFIG["target_chars"],
                overlap_sentences=settings.CHUNKER_CONFIG["overlap_sentences"],
            )

            print(f"[INGESTION] CREATED {len(chunks)} chunks(s) for '{filename}'")

            all_chunks.extend(chunks)

        finally:
            doc.close()

    print(f"\n[INGESTION] TOTAL CHUNKS CREATED : {len(all_chunks)}")
    
    # Persist chunks to vector store
    if all_chunks:
        print(f"[INGESTION] Persisting {len(all_chunks)} chunks to vector store...")
        try:
            add_chunks_to_collection(all_chunks)
            print("[INGESTION] ✅ Successfully stored chunks to vector store")
        except Exception as e:
            print(f"[INGESTION] ❌ ERROR: Failed to store chunks: {e}")
            raise
    
    return all_chunks


if __name__ == "__main__":
    chunks  = build_chunks_for_all_pdfs()

    for c in chunks[:3]:
        print(f"\n[PREVIEW] chunk {c['id']} from {c['source_doc']} : ")
        print(c["text"][:200], "...")

