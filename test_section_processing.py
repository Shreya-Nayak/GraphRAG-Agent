#!/usr/bin/env python3
"""
Test Section-Level Document Processing
Demonstrates granular change detection and processing
"""
import sys
import os
from enhanced_ingestion import ingest_documents_sectioned
from section_tracker import SectionTracker

def test_section_processing():
    """Test the section-level document processing"""
    print("🧪 Testing Section-Level Document Processing")
    print("=" * 60)
    
    doc_folder = "documents"
    
    if not os.path.exists(doc_folder):
        print(f"❌ Document folder '{doc_folder}' not found!")
        return
    
    # Test 1: Initial processing (all sections should be "new")
    print("\\n📋 Test 1: Initial Section Processing")
    print("-" * 40)
    
    tracker = SectionTracker()
    tracker.force_reprocess_all()  # Clear cache for clean test
    
    result = ingest_documents_sectioned(doc_folder)
    
    print(f"\\n📊 Results:")
    print(f"   📝 New chunks: {len(result['new_chunks'])}")
    print(f"   🔄 Modified chunks: {len(result['modified_chunks'])}")
    print(f"   📈 Stats: {result['stats']}")
    
    # Test 2: Re-run without changes (should be no processing)
    print("\\n📋 Test 2: No Changes Detection")
    print("-" * 40)
    
    result = ingest_documents_sectioned(doc_folder)
    
    print(f"\\n📊 Results:")
    print(f"   📝 New chunks: {len(result['new_chunks'])}")
    print(f"   🔄 Modified chunks: {len(result['modified_chunks'])}")
    print(f"   📈 Stats: {result['stats']}")
    
    # Test 3: Show cache statistics
    print("\\n📋 Test 3: Cache Statistics")
    print("-" * 40)
    
    cache_stats = tracker.get_cache_stats()
    print(f"\\n📊 Cache Statistics:")
    print(f"   📁 Total files: {cache_stats['total_files']}")
    print(f"   📄 Total sections: {cache_stats['total_sections']}")
    print(f"   🕒 Last updated: {cache_stats['last_updated']}")
    
    if cache_stats['files']:
        print(f"\\n📋 File Details:")
        for file_info in cache_stats['files'][:3]:  # Show first 3 files
            print(f"   📝 {file_info['filename']}: {file_info['sections']} sections")
    
    print("\\n✅ Section processing test completed!")

def simulate_document_change():
    """Simulate what happens when a document changes"""
    print("\\n🔄 Simulating Document Change...")
    print("=" * 60)
    
    print("In a real scenario:")
    print("1. User edits 1 paragraph in 'ChatApp PRD.docx'")
    print("2. System detects only that section changed")  
    print("3. Only the modified section gets reprocessed")
    print("4. All other sections remain unchanged in knowledge graph")
    print("5. Minimal API calls and fast processing!")

if __name__ == "__main__":
    test_section_processing()
    simulate_document_change()
