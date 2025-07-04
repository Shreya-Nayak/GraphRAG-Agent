"""
Document Change Tracking System
Prevents unnecessary re-processing of unchanged documents
"""
import os
import json
import hashlib
from typing import Dict, List, Set
from datetime import datetime

class DocumentTracker:
    """Tracks document changes to avoid unnecessary re-processing"""
    
    def __init__(self, cache_file: str = "document_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cached document metadata"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Warning: Could not load document cache: {e}")
        return {"documents": {}, "last_updated": None}
    
    def _save_cache(self):
        """Save document metadata to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save document cache: {e}")
    
    def _get_file_hash(self, filepath: str) -> str:
        """Calculate file hash for change detection"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _get_file_metadata(self, filepath: str) -> Dict:
        """Get file metadata (size, modified time, hash)"""
        try:
            stat = os.stat(filepath)
            return {
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "hash": self._get_file_hash(filepath),
                "last_processed": datetime.now().isoformat()
            }
        except Exception:
            return {}
    
    def get_changed_documents(self, doc_folder: str) -> Dict[str, str]:
        """
        Returns documents that have changed since last processing
        Returns: {status: List[filepath]} where status is 'new', 'modified', or 'unchanged'
        """
        changed_docs = {"new": [], "modified": [], "unchanged": []}
        
        if not os.path.exists(doc_folder):
            print(f"⚠️  Document folder not found: {doc_folder}")
            return changed_docs
        
        current_files = set()
        
        # Check all .docx files in the folder
        for filename in os.listdir(doc_folder):
            if filename.endswith(".docx"):
                filepath = os.path.join(doc_folder, filename)
                current_files.add(filename)
                
                current_metadata = self._get_file_metadata(filepath)
                cached_metadata = self.cache["documents"].get(filename, {})
                
                # Check if file is new or modified
                if not cached_metadata:
                    changed_docs["new"].append(filepath)
                    print(f"📄 New document: {filename}")
                elif (current_metadata.get("hash") != cached_metadata.get("hash") or
                      current_metadata.get("size") != cached_metadata.get("size") or
                      current_metadata.get("modified") != cached_metadata.get("modified")):
                    changed_docs["modified"].append(filepath)
                    print(f"🔄 Modified document: {filename}")
                else:
                    changed_docs["unchanged"].append(filepath)
                    print(f"✅ Unchanged document: {filename}")
        
        # Check for deleted files
        deleted_files = set(self.cache["documents"].keys()) - current_files
        if deleted_files:
            print(f"🗑️  Deleted documents: {', '.join(deleted_files)}")
            for filename in deleted_files:
                del self.cache["documents"][filename]
        
        return changed_docs
    
    def mark_documents_processed(self, doc_folder: str, processed_files: List[str] = None):
        """Mark documents as processed and update cache"""
        if processed_files is None:
            # Mark all .docx files in folder as processed
            processed_files = [f for f in os.listdir(doc_folder) if f.endswith(".docx")]
        
        for filename in processed_files:
            if filename.endswith(".docx"):
                filepath = os.path.join(doc_folder, filename)
                if os.path.exists(filepath):
                    self.cache["documents"][filename] = self._get_file_metadata(filepath)
        
        self.cache["last_updated"] = datetime.now().isoformat()
        self._save_cache()
        print(f"💾 Updated document cache for {len(processed_files)} files")
    
    def force_reprocess_all(self):
        """Clear cache to force reprocessing of all documents"""
        self.cache = {"documents": {}, "last_updated": None}
        self._save_cache()
        print("🔄 Cleared document cache - all documents will be reprocessed")
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about cached documents"""
        return {
            "total_documents": len(self.cache["documents"]),
            "last_updated": self.cache.get("last_updated"),
            "cached_files": list(self.cache["documents"].keys())
        }
