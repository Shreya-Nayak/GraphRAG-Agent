"""
Integrated GraphRAG system using Neo4j for knowledge graph and Qdrant for vector storage
Supports both Neo4j Desktop/Aura and Qdrant Docker/Cloud modes
"""
from typing import List, Dict, Optional
from neo4j_graph import Neo4jGraphRAG
from qdrant_vector import QdrantVectorStore
from config import QDRANT_MODE, NEO4J_MODE
import logging

logger = logging.getLogger(__name__)

class IntegratedGraphRAG:
    def __init__(self):
        """Initialize both Neo4j and Qdrant connections with proper error handling"""
        self.neo4j_graph = None
        self.qdrant_vector = None
        
        # Try to initialize Neo4j
        try:
            self.neo4j_graph = Neo4jGraphRAG()
            if NEO4J_MODE == "aura":
                print("✅ Neo4j Aura DB connected")
            else:
                print("✅ Neo4j Desktop connected")
        except Exception as e:
            if NEO4J_MODE == "aura":
                print(f"⚠️  Neo4j Aura connection failed: {e}")
                print("📝 Check your Aura credentials in .env file")
            else:
                print(f"⚠️  Neo4j Desktop connection failed: {e}")
                print("📝 Make sure Neo4j Desktop is running")
            print("📝 Neo4j features will be disabled, using in-memory fallback")
        
        # Try to initialize Qdrant
        try:
            self.qdrant_vector = QdrantVectorStore()
            if QDRANT_MODE == "cloud":
                print("✅ Qdrant Cloud connected")
            else:
                print("✅ Qdrant Docker connected")
        except Exception as e:
            if QDRANT_MODE == "cloud":
                print(f"❌ Qdrant Cloud connection failed: {e}")
                print("📝 Check your QDRANT_URL and QDRANT_API_KEY in .env file")
            else:
                print(f"❌ Qdrant Docker connection failed: {e}")
                print("📝 Make sure Qdrant is running: docker-compose up -d qdrant")
            raise Exception("Qdrant is required for the system to work")
        
        print("✅ Integrated GraphRAG system initialized")

    def create_chunk_nodes(self, chunks: List[Dict]):
        """Create chunk nodes in both Neo4j and Qdrant"""
        # Add chunk IDs if not present
        for i, chunk in enumerate(chunks):
            if 'chunk_id' not in chunk:
                chunk['chunk_id'] = i
        
        # Store in Neo4j if available
        if self.neo4j_graph:
            print("🔄 Creating chunk nodes in Neo4j...")
            try:
                self.neo4j_graph.create_chunk_nodes(chunks)
            except Exception as e:
                print(f"⚠️  Neo4j storage failed: {e}")
        
        # Store embeddings in Qdrant (required)
        print("🔄 Storing embeddings in Qdrant...")
        self.qdrant_vector.store_embeddings(chunks)
        
        print("✅ Chunks created successfully")

    def link_chunks(self, chunks: List[Dict]):
        """Create relationships between chunks in Neo4j"""
        if self.neo4j_graph:
            print("🔄 Creating relationships in Neo4j...")
            try:
                self.neo4j_graph.link_chunks(chunks)
                print("✅ Chunk relationships created in Neo4j")
            except Exception as e:
                print(f"⚠️  Neo4j relationship creation failed: {e}")
        else:
            print("⚠️  Neo4j not available, skipping relationship creation")

    def get_relevant_chunks(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Hybrid search: Use Qdrant for vector similarity, optionally expand with Neo4j
        """
        print("🔍 Starting search...")
        
        # Step 1: Vector similarity search in Qdrant
        print("📊 Performing vector search in Qdrant...")
        qdrant_chunks = self.qdrant_vector.search_similar(
            query_embedding=query_embedding, 
            top_k=top_k,
            score_threshold=0.6
        )
        
        if not qdrant_chunks:
            print("⚠️ No similar chunks found in Qdrant")
            return []
        
        # Step 2: Expand context using Neo4j if available
        if self.neo4j_graph:
            try:
                chunk_ids = [chunk['chunk_id'] for chunk in qdrant_chunks]
                print("📖 Expanding context using Neo4j relationships...")
                expanded_chunks = self.neo4j_graph.expand_context(chunk_ids, hops=2)
                
                # Combine and deduplicate results
                all_chunks = {}
                for chunk in qdrant_chunks:
                    all_chunks[chunk['chunk_id']] = chunk
                for chunk in expanded_chunks:
                    chunk_id = chunk['chunk_id']
                    if chunk_id not in all_chunks:
                        all_chunks[chunk_id] = chunk
                
                result_chunks = list(all_chunks.values())
                result_chunks.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
                
                print(f"✅ Hybrid search completed: {len(qdrant_chunks)} from Qdrant + {len(expanded_chunks)} expanded = {len(result_chunks)} total")
                return result_chunks
                
            except Exception as e:
                print(f"⚠️  Neo4j expansion failed: {e}, using Qdrant results only")
        
        # Fallback: Return Qdrant results only
        print(f"✅ Vector search completed: {len(qdrant_chunks)} chunks found")
        return qdrant_chunks

    def expand_context(self, chunk_ids: List[int], hops: int = 2) -> List[Dict]:
        """Expand context using Neo4j graph relationships"""
        return self.neo4j_graph.expand_context(chunk_ids, hops)

    def get_chunks_by_file(self, file_name: str) -> List[Dict]:
        """Get all chunks from a specific file using Qdrant"""
        return self.qdrant_vector.get_chunks_by_file(file_name)

    def get_chunk_by_id(self, chunk_id: int) -> Optional[Dict]:
        """Get a specific chunk by ID using Qdrant"""
        return self.qdrant_vector.get_chunk_by_id(chunk_id)

    def search_semantic_relationships(self, chunk_id: int) -> List[Dict]:
        """Find semantically related chunks using Neo4j"""
        with self.neo4j_graph.driver.session() as session:
            result = session.run("""
                MATCH (c:Chunk {chunk_id: $chunk_id})-[r:SEMANTICALLY_SIMILAR]-(related:Chunk)
                RETURN related.chunk_id as chunk_id,
                       related.text as text,
                       related.file_name as file_name,
                       related.section_title as section_title,
                       related.doc_type as doc_type,
                       r.similarity as similarity
                ORDER BY r.similarity DESC
                LIMIT 10
            """, chunk_id=chunk_id)
            
            chunks = []
            for record in result:
                chunks.append({
                    'chunk_id': record['chunk_id'],
                    'text': record['text'],
                    'file_name': record['file_name'],
                    'section_title': record['section_title'],
                    'doc_type': record['doc_type'],
                    'similarity_score': record['similarity']
                })
            
            return chunks

    def get_system_stats(self) -> Dict:
        """Get statistics about both systems"""
        stats = {
            'neo4j_connected': True,
            'qdrant_connected': True,
            'qdrant_collection_info': None
        }
        
        try:
            # Get Qdrant stats
            collection_info = self.qdrant_vector.get_collection_info()
            if collection_info:
                stats['qdrant_collection_info'] = {
                    'vectors_count': collection_info.vectors_count,
                    'indexed_vectors_count': collection_info.indexed_vectors_count,
                    'points_count': collection_info.points_count
                }
        except Exception as e:
            stats['qdrant_connected'] = False
            logger.error(f"Qdrant stats error: {e}")
        
        try:
            # Test Neo4j connection
            with self.neo4j_graph.driver.session() as session:
                result = session.run("MATCH (c:Chunk) RETURN count(c) as chunk_count")
                record = result.single()
                stats['neo4j_chunk_count'] = record['chunk_count'] if record else 0
        except Exception as e:
            stats['neo4j_connected'] = False
            logger.error(f"Neo4j stats error: {e}")
        
        return stats

    def close(self):
        """Close both connections"""
        print("🔄 Closing connections...")
        if self.neo4j_graph:
            self.neo4j_graph.close()
        if self.qdrant_vector:
            self.qdrant_vector.close()
        print("✅ All connections closed")

    def has_existing_data(self) -> Dict[str, bool]:
        """Check if the system already has data to avoid duplicates"""
        status = {
            'neo4j_has_data': False,
            'qdrant_has_data': False,
            'total_chunks': 0,
            'total_points': 0
        }
        
        try:
            # Check Neo4j for existing chunks
            with self.neo4j_graph.driver.session() as session:
                result = session.run("MATCH (c:Chunk) RETURN count(c) as chunk_count")
                record = result.single()
                chunk_count = record['chunk_count'] if record else 0
                status['neo4j_has_data'] = chunk_count > 0
                status['total_chunks'] = chunk_count
        except Exception as e:
            logger.warning(f"Could not check Neo4j data: {e}")
        
        try:
            # Check Qdrant for existing points
            collection_info = self.qdrant_vector.get_collection_info()
            if collection_info:
                points_count = collection_info.points_count or 0
                status['qdrant_has_data'] = points_count > 0
                status['total_points'] = points_count
        except Exception as e:
            logger.warning(f"Could not check Qdrant data: {e}")
        
        return status

    def ingest_chunks(self, chunks: List[Dict]):
        """Intelligently ingest chunks, avoiding duplicates"""
        if not chunks:
            logger.info("No chunks to ingest")
            return
        
        logger.info(f"Ingesting {len(chunks)} chunks into knowledge graph")
        
        # Check for existing data
        existing_data = self.has_existing_data()
        
        if existing_data['neo4j_has_data'] or existing_data['qdrant_has_data']:
            logger.info(f"Existing data found - Neo4j: {existing_data['total_chunks']} chunks, "
                       f"Qdrant: {existing_data['total_points']} points")
            logger.info("Performing incremental update...")
        else:
            logger.info("No existing data found - performing initial ingestion")
        
        try:
            # Generate embeddings for chunks that don't have them
            chunks_to_embed = [chunk for chunk in chunks if 'embedding' not in chunk]
            if chunks_to_embed:
                logger.info(f"Generating embeddings for {len(chunks_to_embed)} chunks")
                for i, chunk in enumerate(chunks_to_embed):
                    try:
                        from embedding import get_gemini_embedding, dummy_embedding
                        import asyncio
                        chunk["embedding"] = asyncio.run(get_gemini_embedding(chunk["text"]))
                    except Exception as e:
                        logger.warning(f"Embedding failed for chunk {i+1}, using fallback: {e}")
                        chunk["embedding"] = dummy_embedding(chunk["text"])
            
            # Store in Neo4j (handles duplicates internally)
            self.create_chunk_nodes(chunks)
            self.link_chunks(chunks)
            
            logger.info(f"✅ Successfully ingested {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to ingest chunks: {e}")
            raise
