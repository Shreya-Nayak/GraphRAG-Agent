"""
Enhanced Document Tracker with Section-Level Change Detection
Tracks changes at paragraph/section level for granular updates
"""
import os
import json
import hashlib
from typing import Dict, List, Set, Tuple
from datetime import datetime
from docx import Document

class SectionTracker:
    """Tracks document changes at section/paragraph level"""
    
    def __init__(self, cache_file: str = "section_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cached section metadata"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Warning: Could not load section cache: {e}")
        return {"documents": {}, "last_updated": None}
    
    def _save_cache(self):
        """Save section metadata to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save section cache: {e}")
    
    def _extract_sections_with_hashes(self, filepath: str) -> List[Dict]:
        """Extract sections from docx with individual hashes"""
        try:
            doc = Document(filepath)
            sections = []
            section_id = 0
            current_section = {"title": None, "content": "", "paragraphs": []}
            
            for para_idx, para in enumerate(doc.paragraphs):
                para_text = para.text.strip()
                if not para_text:
                    continue
                    
                # Check if this is a heading (new section)
                if para.style.name.startswith("Heading"):
                    # Save previous section if it has content
                    if current_section["content"].strip():
                        current_section["section_id"] = section_id
                        current_section["hash"] = hashlib.md5(
                            current_section["content"].encode('utf-8')
                        ).hexdigest()
                        sections.append(current_section)
                        section_id += 1
                    
                    # Start new section
                    current_section = {
                        "title": para_text,
                        "content": para_text + "\\n",
                        "paragraphs": [{"index": para_idx, "text": para_text}]
                    }
                else:
                    # Add to current section
                    current_section["content"] += para_text + "\\n"
                    current_section["paragraphs"].append({
                        "index": para_idx, 
                        "text": para_text
                    })
            
            # Don't forget the last section
            if current_section["content"].strip():
                current_section["section_id"] = section_id
                current_section["hash"] = hashlib.md5(
                    current_section["content"].encode('utf-8')
                ).hexdigest()
                sections.append(current_section)
            
            return sections
            
        except Exception as e:
            print(f"❌ Error extracting sections from {filepath}: {e}")
            return []
    
    def get_changed_sections(self, doc_folder: str) -> Dict[str, Dict]:
        """
        Returns sections that have changed since last processing
        Returns: {filename: {new: [...], modified: [...], unchanged: [...]}}
        """
        all_changes = {}
        
        if not os.path.exists(doc_folder):
            print(f"⚠️  Document folder not found: {doc_folder}")
            return all_changes
        
        # Process each .docx file
        for filename in os.listdir(doc_folder):
            if not filename.endswith(".docx"):
                continue
                
            filepath = os.path.join(doc_folder, filename)
            file_changes = {"new": [], "modified": [], "unchanged": []}
            
            # Extract current sections
            current_sections = self._extract_sections_with_hashes(filepath)
            cached_sections = self.cache["documents"].get(filename, {}).get("sections", [])
            
            # Create lookup for cached sections
            cached_lookup = {s["section_id"]: s for s in cached_sections}
            
            print(f"📄 Analyzing {filename}: {len(current_sections)} sections")
            
            # Check each current section
            for section in current_sections:
                section_id = section["section_id"]
                cached_section = cached_lookup.get(section_id)
                
                if not cached_section:
                    # New section
                    file_changes["new"].append(section)
                    print(f"   📝 New section {section_id}: {section['title'][:50]}...")
                elif section["hash"] != cached_section["hash"]:
                    # Modified section
                    file_changes["modified"].append(section)
                    print(f"   🔄 Modified section {section_id}: {section['title'][:50]}...")
                else:
                    # Unchanged section
                    file_changes["unchanged"].append(section)
                    print(f"   ✅ Unchanged section {section_id}: {section['title'][:50]}...")
            
            # Check for deleted sections
            current_ids = {s["section_id"] for s in current_sections}
            cached_ids = {s["section_id"] for s in cached_sections}
            deleted_ids = cached_ids - current_ids
            
            if deleted_ids:
                print(f"   🗑️  Deleted sections: {deleted_ids}")
            
            all_changes[filename] = file_changes
        
        return all_changes
    
    def mark_sections_processed(self, doc_folder: str, processed_files: Dict[str, List] = None):
        """Mark sections as processed and update cache"""
        if processed_files is None:
            # Mark all files as fully processed
            processed_files = {}
            for filename in os.listdir(doc_folder):
                if filename.endswith(".docx"):
                    filepath = os.path.join(doc_folder, filename)
                    sections = self._extract_sections_with_hashes(filepath)
                    processed_files[filename] = sections
        
        # Update cache
        for filename, sections in processed_files.items():
            self.cache["documents"][filename] = {
                "sections": sections,
                "last_processed": datetime.now().isoformat(),
                "total_sections": len(sections)
            }
        
        self.cache["last_updated"] = datetime.now().isoformat()
        self._save_cache()
        
        total_sections = sum(len(sections) for sections in processed_files.values())
        print(f"💾 Updated section cache: {len(processed_files)} files, {total_sections} sections")
    
    def force_reprocess_all(self):
        """Clear cache to force reprocessing of all sections"""
        self.cache = {"documents": {}, "last_updated": None}
        self._save_cache()
        print("🔄 Cleared section cache - all documents will be reprocessed")
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about cached sections"""
        total_sections = 0
        files_info = []
        
        for filename, data in self.cache["documents"].items():
            section_count = data.get("total_sections", 0)
            total_sections += section_count
            files_info.append({
                "filename": filename,
                "sections": section_count,
                "last_processed": data.get("last_processed")
            })
        
        return {
            "total_files": len(self.cache["documents"]),
            "total_sections": total_sections,
            "last_updated": self.cache.get("last_updated"),
            "files": files_info
        }
