"""
Enhanced File Ingestion with Section-Level Processing
Only processes changed sections instead of entire files
"""
import os
from typing import List, Dict, Optional
from docx import Document
import tiktoken
from section_tracker import SectionTracker

def get_doc_type(filename: str) -> str:
    """Determine document type from filename"""
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

def chunk_section_text(text: str, max_tokens: int = 800) -> List[str]:
    """Chunk section text into manageable pieces"""
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

def process_section_to_chunks(section: Dict, filename: str, doc_type: str) -> List[Dict]:
    """Convert a section into document chunks"""
    chunks = []
    section_title = section.get("title", "Untitled Section")
    section_content = section.get("content", "")
    
    if not section_content.strip():
        return chunks
    
    # Chunk the section content
    text_chunks = chunk_section_text(section_content)
    
    for chunk_idx, chunk_text in enumerate(text_chunks):
        if chunk_text.strip():
            chunks.append({
                "text": chunk_text.strip(),
                "file_name": filename,
                "section_title": section_title,
                "section_id": section.get("section_id", 0),
                "chunk_id": f"{filename}_{section.get('section_id', 0)}_{chunk_idx}",
                "doc_type": doc_type,
                "section_hash": section.get("hash", "")
            })
    
    return chunks

def ingest_documents_sectioned(folder: str, force_reprocess: bool = False) -> Dict[str, List[Dict]]:
    """
    Intelligently ingest documents with section-level change detection
    
    Args:
        folder: Path to documents folder
        force_reprocess: If True, reprocess all sections regardless of cache
    
    Returns:
        Dict with 'new_chunks': new chunks, 'modified_chunks': updated chunks, 'stats': processing stats
    """
    tracker = SectionTracker()
    
    if force_reprocess:
        print("🔄 Force reprocessing all sections...")
        tracker.force_reprocess_all()
    
    # Get section-level changes
    all_changes = tracker.get_changed_sections(folder)
    
    new_chunks = []
    modified_chunks = []
    stats = {
        "files_processed": 0,
        "sections_new": 0,
        "sections_modified": 0,
        "sections_unchanged": 0,
        "total_chunks": 0
    }
    
    if not any(changes["new"] or changes["modified"] for changes in all_changes.values()):
        print("✅ No section changes detected - skipping ingestion")
        print(f"📊 Cache stats: {tracker.get_cache_stats()}")
        return {
            "new_chunks": [],
            "modified_chunks": [],
            "stats": stats
        }
    
    print(f"📄 Processing sections from {len(all_changes)} documents:")
    
    processed_files = {}
    
    for filename, changes in all_changes.items():
        if not changes["new"] and not changes["modified"]:
            continue
            
        doc_type = get_doc_type(filename)
        stats["files_processed"] += 1
        
        print(f"\\n📝 {filename}:")
        print(f"   📝 New sections: {len(changes['new'])}")
        print(f"   🔄 Modified sections: {len(changes['modified'])}")
        print(f"   ✅ Unchanged sections: {len(changes['unchanged'])}")
        
        # Process new sections
        for section in changes["new"]:
            try:
                section_chunks = process_section_to_chunks(section, filename, doc_type)
                new_chunks.extend(section_chunks)
                stats["sections_new"] += 1
                stats["total_chunks"] += len(section_chunks)
                print(f"   ✅ New section '{section['title'][:40]}...': {len(section_chunks)} chunks")
            except Exception as e:
                print(f"   ❌ Failed to process new section: {e}")
        
        # Process modified sections  
        for section in changes["modified"]:
            try:
                section_chunks = process_section_to_chunks(section, filename, doc_type)
                modified_chunks.extend(section_chunks)
                stats["sections_modified"] += 1
                stats["total_chunks"] += len(section_chunks)
                print(f"   🔄 Modified section '{section['title'][:40]}...': {len(section_chunks)} chunks")
            except Exception as e:
                print(f"   ❌ Failed to process modified section: {e}")
        
        # Track all sections for cache update (including unchanged)
        all_sections = changes["new"] + changes["modified"] + changes["unchanged"]
        processed_files[filename] = all_sections
        stats["sections_unchanged"] += len(changes["unchanged"])
    
    # Update cache with all processed sections
    if processed_files:
        tracker.mark_sections_processed(folder, processed_files)
        print(f"\\n💾 Cache updated: {stats['files_processed']} files")
        print(f"📊 Section summary:")
        print(f"   📝 New: {stats['sections_new']} sections")
        print(f"   🔄 Modified: {stats['sections_modified']} sections") 
        print(f"   ✅ Unchanged: {stats['sections_unchanged']} sections")
        print(f"   🧩 Total chunks: {stats['total_chunks']}")
    
    return {
        "new_chunks": new_chunks,
        "modified_chunks": modified_chunks,
        "stats": stats
    }

# Backwards compatibility wrapper
def ingest_documents(folder: str, force_reprocess: bool = False) -> List[Dict]:
    """Wrapper for backwards compatibility - returns all chunks"""
    result = ingest_documents_sectioned(folder, force_reprocess)
    return result["new_chunks"] + result["modified_chunks"]
