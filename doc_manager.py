#!/usr/bin/env python3
"""
CLI Tool for GraphRAG Document Management
Allows force reprocessing and cache management
"""
import sys
import argparse
from document_tracker import DocumentTracker

def main():
    parser = argparse.ArgumentParser(description="GraphRAG Document Management CLI")
    parser.add_argument("--clear-cache", action="store_true", 
                       help="Clear document cache (forces reprocessing)")
    parser.add_argument("--check-status", action="store_true",
                       help="Check document status and cache")
    parser.add_argument("--folder", default="documents",
                       help="Documents folder path (default: documents)")
    
    args = parser.parse_args()
    
    tracker = DocumentTracker()
    
    if args.clear_cache:
        print("🗑️  Clearing document cache...")
        tracker.force_reprocess_all()
        print("✅ Cache cleared - all documents will be reprocessed on next run")
    
    if args.check_status:
        print("📊 Document Status Report")
        print("=" * 50)
        
        # Get cache stats
        stats = tracker.get_cache_stats()
        print(f"📁 Cached Documents: {stats['total_documents']}")
        print(f"🕒 Last Updated: {stats['last_updated']}")
        
        if stats['cached_files']:
            print(f"📄 Files in cache:")
            for file in stats['cached_files']:
                print(f"   • {file}")
        
        # Check for changes
        print("\n🔍 Checking for changes...")
        changes = tracker.get_changed_documents(args.folder)
        
        if changes['new']:
            print(f"📝 New files ({len(changes['new'])}):")
            for file in changes['new']:
                print(f"   • {file}")
        
        if changes['modified']:
            print(f"🔄 Modified files ({len(changes['modified'])}):")
            for file in changes['modified']:
                print(f"   • {file}")
        
        if changes['unchanged']:
            print(f"✅ Unchanged files ({len(changes['unchanged'])}):")
            for file in changes['unchanged']:
                print(f"   • {file}")
    
    if not args.clear_cache and not args.check_status:
        parser.print_help()

if __name__ == "__main__":
    main()
