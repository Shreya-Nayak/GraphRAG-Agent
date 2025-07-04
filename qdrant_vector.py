"""
Qdrant vector database operations for embedding storage
Supports both Docker (local) and Cloud (remote) modes
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional
import logging
import uuid
from config import (
    QDRANT_MODE, QDRANT_URL, QDRANT_API_KEY, 
    QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION_NAME
)

logger = logging.getLogger(__name__)

class QdrantVectorStore:
    def __init__(self):
        """Initialize Qdrant client - supports both Docker and Cloud modes"""
        try:
            if QDRANT_MODE == "cloud":
                # Qdrant Cloud mode
                if not QDRANT_URL:
                    raise ValueError("QDRANT_URL is required for cloud mode")
                if not QDRANT_API_KEY:
                    raise ValueError("QDRANT_API_KEY is required for cloud mode")
                
                self.client = QdrantClient(
                    url=QDRANT_URL,
                    api_key=QDRANT_API_KEY,
                )
                print(f"✅ Connected to Qdrant Cloud: {QDRANT_URL}")
                
            else:
                # Docker mode (local)
                self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
                print(f"✅ Connected to Qdrant Docker: {QDRANT_HOST}:{QDRANT_PORT}")
            
            self.collection_name = QDRANT_COLLECTION_NAME
            
            # Test connection and get collections
            collections = self.client.get_collections()
            print(f"✅ Qdrant connection successful ({QDRANT_MODE} mode)")
            
            # Create collection if it doesn't exist
            self._create_collection()
            
        except Exception as e:
            if QDRANT_MODE == "cloud":
                logger.error(f"Failed to connect to Qdrant Cloud: {e}")
                logger.error("Check your QDRANT_URL and QDRANT_API_KEY in .env file")
            else:
                logger.error(f"Failed to connect to Qdrant Docker: {e}")
                logger.error("Make sure Qdrant is running: docker-compose up -d qdrant")
            raise

    def _create_collection(self):
        """Create collection for document chunks"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=768,  # Gemini embedding dimension
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Created Qdrant collection: {self.collection_name}")
            else:
                print(f"✅ Qdrant collection already exists: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise

    def store_embeddings(self, chunks: List[Dict]):
        """Store chunk embeddings in Qdrant"""
        points = []
        
        for i, chunk in enumerate(chunks):
            point_id = chunk.get('chunk_id', i)
            
            # Create point for Qdrant
            point = PointStruct(
                id=point_id,
                vector=chunk['embedding'],
                payload={
                    'text': chunk['text'],
                    'file_name': chunk['file_name'],
                    'section_title': chunk.get('section_title', ''),
                    'doc_type': chunk.get('doc_type', 'UNKNOWN'),
                    'chunk_id': point_id
                }
            )
            points.append(point)
        
        # Batch upsert points
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        
        print(f"✅ Stored {len(chunks)} embeddings in Qdrant")

    def search_similar(self, query_embedding: List[float], top_k: int = 5, score_threshold: float = 0.7) -> List[Dict]:
        """Search for similar chunks using vector similarity"""
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )
            
            chunks = []
            for hit in search_result:
                chunk = {
                    'chunk_id': hit.payload['chunk_id'],
                    'text': hit.payload['text'],
                    'file_name': hit.payload['file_name'],
                    'section_title': hit.payload['section_title'],
                    'doc_type': hit.payload['doc_type'],
                    'similarity_score': hit.score
                }
                chunks.append(chunk)
            
            print(f"📄 Found {len(chunks)} similar chunks from Qdrant")
            return chunks
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_chunk_by_id(self, chunk_id: int) -> Optional[Dict]:
        """Retrieve a specific chunk by ID"""
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[chunk_id],
                with_payload=True,
                with_vectors=True
            )
            
            if result:
                point = result[0]
                return {
                    'chunk_id': point.payload['chunk_id'],
                    'text': point.payload['text'],
                    'file_name': point.payload['file_name'],
                    'section_title': point.payload['section_title'],
                    'doc_type': point.payload['doc_type'],
                    'embedding': point.vector
                }
            return None
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return None

    def get_chunks_by_file(self, file_name: str) -> List[Dict]:
        """Get all chunks from a specific file"""
        try:
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="file_name",
                            match=models.MatchValue(value=file_name)
                        )
                    ]
                ),
                with_payload=True,
                with_vectors=False
            )
            
            chunks = []
            for point in search_result[0]:  # search_result is (points, next_page_offset)
                chunk = {
                    'chunk_id': point.payload['chunk_id'],
                    'text': point.payload['text'],
                    'file_name': point.payload['file_name'],
                    'section_title': point.payload['section_title'],
                    'doc_type': point.payload['doc_type']
                }
                chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            logger.error(f"File retrieval failed: {e}")
            return []

    def delete_collection(self):
        """Delete the entire collection"""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            print(f"✅ Deleted Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Collection deletion failed: {e}")

    def get_collection_info(self):
        """Get information about the collection"""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            print(f"📊 Collection info: {info}")
            return info
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return None

    def close(self):
        """Close Qdrant connection"""
        if hasattr(self, 'client'):
            # Qdrant client doesn't need explicit closing
            print("✅ Qdrant connection closed")
