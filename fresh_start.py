#!/usr/bin/env python3
"""
Fresh Start Script - Clean databases and restart
Clears all data and rebuilds knowledge graph from scratch
"""
import os
import sys

def clear_all_data():
    """Clear all cached data and force fresh processing"""
    print("🧹 Starting fresh data cleanup...")
    
    # Clear document cache
    cache_files = ["document_cache.json", "section_cache.json"]
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print(f"✅ Removed {cache_file}")
    
    print("💡 Next steps:")
    print("1. Start Neo4j Desktop (if using local)")
    print("2. Start Qdrant Docker: docker-compose up -d qdrant")
    print("3. Clear Neo4j database (optional):")
    print("   MATCH (n) DETACH DELETE n")
    print("4. Run: python main.py --force-reprocess")
    
    # Optionally clear Neo4j if connected
    try:
        from integrated_graphrag import IntegratedGraphRAG
        graph = IntegratedGraphRAG()
        
        print("\n🗑️  Clearing Neo4j database...")
        with graph.neo4j_graph.driver.session() as session:
            result = session.run("MATCH (n) DETACH DELETE n RETURN count(n) as deleted")
            deleted = result.single()['deleted']
            print(f"✅ Deleted {deleted} nodes from Neo4j")
        
        print("🗑️  Clearing Qdrant collection...")
        try:
            graph.qdrant_vector.client.delete_collection("document_chunks")
            print("✅ Cleared Qdrant collection")
        except:
            print("💡 Qdrant collection will be recreated automatically")
            
        graph.close()
        
    except Exception as e:
        print(f"💡 Database cleanup skipped: {e}")
        print("💡 Manually clear databases if they're running")

if __name__ == "__main__":
    clear_all_data()
    print("\n🎉 Fresh start ready! Run the application to rebuild clean data.")
