"""
Neo4j Aura DB graph operations for knowledge graph storage
"""
from neo4j import GraphDatabase
from typing import List, Dict, Optional
import logging
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

logger = logging.getLogger(__name__)

class Neo4jGraphRAG:
    def __init__(self):
        """Initialize Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
                database=NEO4J_DATABASE
            )
            # Test connection
            self.driver.verify_connectivity()
            print("✅ Connected to Neo4j Aura DB successfully")
            
            # Create constraints and indexes
            self._create_constraints()
            self._create_vector_index()
            
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def _create_constraints(self):
        """Create necessary constraints"""
        with self.driver.session() as session:
            # Create unique constraint for chunk IDs
            session.run("""
                CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS 
                FOR (c:Chunk) REQUIRE c.chunk_id IS UNIQUE
            """)
            
            # Create constraint for documents
            session.run("""
                CREATE CONSTRAINT document_name_unique IF NOT EXISTS 
                FOR (d:Document) REQUIRE d.name IS UNIQUE
            """)
            print("✅ Neo4j constraints created")

    def _create_vector_index(self):
        """Create vector index for similarity search"""
        with self.driver.session() as session:
            try:
                # Create vector index for embeddings
                session.run("""
                    CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
                    FOR (c:Chunk) ON (c.embedding)
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: 768,
                        `vector.similarity_function`: 'cosine'
                    }}
                """)
                print("✅ Neo4j vector index created")
            except Exception as e:
                logger.warning(f"Vector index creation warning: {e}")

    def create_chunk_nodes(self, chunks: List[Dict]):
        """Create chunk nodes in Neo4j"""
        with self.driver.session() as session:
            for chunk in chunks:
                session.run("""
                    MERGE (c:Chunk {chunk_id: $chunk_id})
                    SET c.text = $text,
                        c.file_name = $file_name,
                        c.section_title = $section_title,
                        c.doc_type = $doc_type,
                        c.embedding = $embedding
                    
                    MERGE (d:Document {name: $file_name})
                    SET d.doc_type = $doc_type
                    
                    MERGE (c)-[:BELONGS_TO]->(d)
                """, 
                    chunk_id=chunk.get('chunk_id', hash(chunk['text'])),
                    text=chunk['text'],
                    file_name=chunk['file_name'],
                    section_title=chunk.get('section_title', ''),
                    doc_type=chunk.get('doc_type', 'UNKNOWN'),
                    embedding=chunk['embedding']
                )
        print(f"✅ Created {len(chunks)} chunk nodes in Neo4j")

    def link_chunks(self, chunks: List[Dict]):
        """Create relationships between chunks"""
        with self.driver.session() as session:
            # Create sequential relationships within documents
            for i in range(len(chunks) - 1):
                if chunks[i]['file_name'] == chunks[i + 1]['file_name']:
                    session.run("""
                        MATCH (c1:Chunk {chunk_id: $chunk_id1})
                        MATCH (c2:Chunk {chunk_id: $chunk_id2})
                        MERGE (c1)-[:NEXT_SECTION]->(c2)
                    """,
                        chunk_id1=chunks[i].get('chunk_id', hash(chunks[i]['text'])),
                        chunk_id2=chunks[i + 1].get('chunk_id', hash(chunks[i + 1]['text']))
                    )
            
            # Create semantic relationships based on similarity
            self._create_semantic_relationships()
        print("✅ Created relationships between chunks in Neo4j")

    def _create_semantic_relationships(self):
        """Create semantic relationships between similar chunks"""
        with self.driver.session() as session:
            # Find semantically similar chunks and create relationships
            session.run("""
                MATCH (c1:Chunk), (c2:Chunk)
                WHERE c1 <> c2 AND c1.file_name <> c2.file_name
                WITH c1, c2, 
                     gds.similarity.cosine(c1.embedding, c2.embedding) AS similarity
                WHERE similarity > 0.8
                MERGE (c1)-[:SEMANTICALLY_SIMILAR {similarity: similarity}]->(c2)
            """)

    def get_relevant_chunks(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Find most similar chunks using vector search"""
        with self.driver.session() as session:
            result = session.run("""
                CALL db.index.vector.queryNodes('chunk_embeddings', $top_k, $query_embedding)
                YIELD node, score
                RETURN node.chunk_id as chunk_id, 
                       node.text as text,
                       node.file_name as file_name,
                       node.section_title as section_title,
                       node.doc_type as doc_type,
                       score
                ORDER BY score DESC
            """, top_k=top_k, query_embedding=query_embedding)
            
            chunks = []
            for record in result:
                chunks.append({
                    'chunk_id': record['chunk_id'],
                    'text': record['text'],
                    'file_name': record['file_name'],
                    'section_title': record['section_title'],
                    'doc_type': record['doc_type'],
                    'similarity_score': record['score']
                })
            
            print(f"📄 Found {len(chunks)} relevant chunks from Neo4j")
            return chunks

    def expand_context(self, chunk_ids: List[int], hops: int = 2) -> List[Dict]:
        """Expand context by following relationships"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (start:Chunk)
                WHERE start.chunk_id IN $chunk_ids
                MATCH path = (start)-[*1..$hops]-(related:Chunk)
                RETURN DISTINCT related.chunk_id as chunk_id,
                       related.text as text,
                       related.file_name as file_name,
                       related.section_title as section_title,
                       related.doc_type as doc_type
            """, chunk_ids=chunk_ids, hops=hops)
            
            chunks = []
            for record in result:
                chunks.append({
                    'chunk_id': record['chunk_id'],
                    'text': record['text'],
                    'file_name': record['file_name'],
                    'section_title': record['section_title'],
                    'doc_type': record['doc_type']
                })
            
            print(f"📖 Expanded to {len(chunks)} chunks total from Neo4j")
            return chunks

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            print("✅ Neo4j connection closed")
