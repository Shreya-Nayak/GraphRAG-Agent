import os
from typing import List, Dict, Optional
from docx import Document
import tiktoken
from document_tracker import DocumentTracker

def get_doc_type(filename: str) -> str:
    # Simple heuristic based on filename
    lowered = filename.lower()
    if "prd" in lowered:
        return "PRD"
    if "hld" in lowered:
        return "HLD"
    if "lld" in lowered:
        return "LLD"
    if "api" in lowered:
        return "API_SPEC"
    if "architecture" in lowered:
        return "ARCHITECTURE"
    return "OTHER"

def extract_sections(doc: Document) -> List[Dict]:
    # Extracts paragraphs and tries to infer section headings
    sections = []
    current_section = {"title": None, "text": ""}
    for para in doc.paragraphs:
        if para.style.name.startswith("Heading"):
            if current_section["text"]:
                sections.append(current_section)
            current_section = {"title": para.text, "text": ""}
        else:
            current_section["text"] += para.text + "\n"
    if current_section["text"]:
        sections.append(current_section)
    return sections

def chunk_text(text: str, max_tokens: int = 800) -> List[str]:
    # Use tiktoken to count tokens (fallback: split by ~500 words)
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = enc.encode(text)
        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk = enc.decode(tokens[i:i+max_tokens])
            chunks.append(chunk)
        return chunks
    except Exception:
        # Fallback: split by words
        words = text.split()
        return [" ".join(words[i:i+500]) for i in range(0, len(words), 500)]

def process_docx_file(filepath: str) -> List[Dict]:
    doc = Document(filepath)
    file_name = os.path.basename(filepath)
    doc_type = get_doc_type(file_name)
    sections = extract_sections(doc)
    chunks = []
    for section in sections:
        section_title = section["title"]
        for chunk in chunk_text(section["text"]):
            if chunk.strip():
                chunks.append({
                    "text": chunk.strip(),
                    "file_name": file_name,
                    "section_title": section_title,
                    "doc_type": doc_type
                })
    return chunks

def ingest_documents(folder: str, force_reprocess: bool = False) -> List[Dict]:
    """
    Intelligently ingest documents - only process changed/new files
    
    Args:
        folder: Path to documents folder
        force_reprocess: If True, reprocess all documents regardless of cache
    
    Returns:
        List of document chunks from new/modified documents only
    """
    tracker = DocumentTracker()
    
    if force_reprocess:
        print("🔄 Force reprocessing all documents...")
        tracker.force_reprocess_all()
    
    # Get document change status
    changes = tracker.get_changed_documents(folder)
    
    # Files that need processing
    files_to_process = changes["new"] + changes["modified"]
    
    if not files_to_process:
        print("✅ No document changes detected - skipping ingestion")
        print(f"📊 Cache stats: {tracker.get_cache_stats()}")
        return []
    
    print(f"📄 Processing {len(files_to_process)} documents:")
    print(f"   📝 New: {len(changes['new'])}")
    print(f"   🔄 Modified: {len(changes['modified'])}")
    print(f"   ✅ Unchanged: {len(changes['unchanged'])}")
    
    all_chunks = []
    processed_files = []
    
    for filepath in files_to_process:
        try:
            chunks = process_docx_file(filepath)
            all_chunks.extend(chunks)
            processed_files.append(os.path.basename(filepath))
            print(f"✅ Processed {os.path.basename(filepath)}: {len(chunks)} chunks")
        except Exception as e:
            print(f"❌ Failed to process {os.path.basename(filepath)}: {e}")
    
    # Update cache for successfully processed files
    if processed_files:
        tracker.mark_documents_processed(folder, processed_files)
        print(f"💾 Successfully processed {len(processed_files)} documents")
    
    return all_chunks
