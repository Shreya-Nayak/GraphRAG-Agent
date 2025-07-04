from memory_graph import InMemoryGraphRAG

# Simple test
print("Testing InMemoryGraphRAG initialization...")
try:
    rag = InMemoryGraphRAG()
    print("SUCCESS: InMemoryGraphRAG initialized")
    
    # Test with dummy data
    test_chunks = [
        {
            "text": "Test chunk 1",
            "file_name": "test.docx",
            "doc_type": "test",
            "embedding": [0.1, 0.2, 0.3]
        }
    ]
    
    rag.create_chunk_nodes(test_chunks)
    rag.link_chunks(test_chunks)
    print("SUCCESS: Test chunks processed")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
