#!/usr/bin/env python3
"""
Duplicate Detection and Cleanup Tool
Checks for and removes duplicate entries in Neo4j and Qdrant
"""
import sys
from typing import Dict, List
from integrated_graphrag import IntegratedGraphRAG

def check_duplicates():
    """Check for duplicate entries in the system"""
    try:
        print("🔍 Checking for duplicate entries...")
        graph = IntegratedGraphRAG()
        
        # Check Neo4j for duplicate chunks
        print("\n📊 Neo4j Analysis:")
        with graph.neo4j_graph.driver.session() as session:
            # Count total chunks
            result = session.run("MATCH (c:Chunk) RETURN count(c) as total")
            total_chunks = result.single()['total']
            
            # Count unique chunks by text hash
            result = session.run("""
                MATCH (c:Chunk) 
                WITH c.text as text, count(c) as count_per_text
                RETURN count_per_text, count(*) as frequency
                ORDER BY count_per_text DESC
            """)
            
            duplicates_found = False
            for record in result:
                if record['count_per_text'] > 1:
                    print(f"⚠️  Found {record['frequency']} texts with {record['count_per_text']} duplicates each")
                    duplicates_found = True
            
            if not duplicates_found:
                print("✅ No duplicate chunks found in Neo4j")
            
            print(f"📊 Total chunks: {total_chunks}")
        
        # Check Qdrant for duplicate vectors
        print("\n📊 Qdrant Analysis:")
        collection_info = graph.qdrant_vector.get_collection_info()
        if collection_info:
            print(f"📊 Total points: {collection_info.points_count}")
            
            # In a real scenario, we'd need to check vector similarity
            # For now, just report the count
            if collection_info.points_count > 600:  # Expected ~559
                print(f"⚠️  Suspiciously high point count: {collection_info.points_count}")
                print("💡 This might indicate duplicates")
            else:
                print("✅ Point count looks normal")
        
        return {'neo4j_chunks': total_chunks, 'qdrant_points': collection_info.points_count if collection_info else 0}
        
    except Exception as e:
        print(f"❌ Could not check duplicates: {e}")
        return None

def cleanup_duplicates():
    """Remove duplicate entries (USE WITH CAUTION!)"""
    print("🧹 Starting duplicate cleanup...")
    print("⚠️  WARNING: This will permanently delete duplicate data!")
    
    confirm = input("Are you sure you want to proceed? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Cleanup cancelled")
        return
    
    try:
        graph = IntegratedGraphRAG()
        
        print("🗑️  Removing duplicate chunks from Neo4j...")
        with graph.neo4j_graph.driver.session() as session:
            # Remove duplicate chunks (keep first occurrence)
            result = session.run("""
                MATCH (c:Chunk)
                WITH c.text as text, collect(c) as chunks
                WHERE size(chunks) > 1
                UNWIND chunks[1..] as duplicate
                DETACH DELETE duplicate
                RETURN count(*) as deleted
            """)
            deleted = result.single()['deleted']
            print(f"✅ Deleted {deleted} duplicate chunks from Neo4j")
        
        # For Qdrant, we'd need to implement vector similarity checking
        # This is more complex and requires careful analysis
        print("💡 Qdrant cleanup requires manual review of vector similarities")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        cleanup_duplicates()
    else:
        stats = check_duplicates()
        if stats:
            print(f"\n📊 Summary:")
            print(f"   Neo4j chunks: {stats['neo4j_chunks']}")
            print(f"   Qdrant points: {stats['qdrant_points']}")
            print(f"\n💡 To cleanup duplicates, run: python {sys.argv[0]} --cleanup")

if __name__ == "__main__":
    main()
