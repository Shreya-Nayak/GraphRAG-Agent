import numpy as np
from typing import List, Dict, Optional
from sklearn.metrics.pairwise import cosine_similarity

class InMemoryGraphRAG:
    def __init__(self):
        self.chunks = []
        self.embeddings = []
        self.chunk_index = {}
    
    def create_chunk_nodes(self, chunks: List[Dict]):
        """Store chunks in memory with their embeddings"""
        for idx, chunk in enumerate(chunks):
            chunk['chunk_id'] = idx
            self.chunks.append(chunk)
            self.embeddings.append(chunk['embedding'])
            self.chunk_index[idx] = chunk
        print(f"✅ Stored {len(chunks)} chunks in memory")
    
    def link_chunks(self, chunks: List[Dict]):
        """Create relationships between chunks (in-memory)"""
        # Add relationships for chunks from the same file
        for i in range(len(chunks) - 1):
            if chunks[i]["file_name"] == chunks[i+1]["file_name"]:
                # Store relationship info in chunk metadata
                if 'relationships' not in chunks[i]:
                    chunks[i]['relationships'] = []
                chunks[i]['relationships'].append({'type': 'NEXT_SECTION', 'target': i+1})
        print(f"✅ Created relationships between chunks")
    
    def get_relevant_chunks(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Find most similar chunks using cosine similarity"""
        if not self.embeddings:
            return []
        
        # Convert to numpy arrays
        query_emb = np.array(query_embedding).reshape(1, -1)
        chunk_embs = np.array(self.embeddings)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_emb, chunk_embs)[0]
        
        # Get top-k most similar chunks
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        result_chunks = []
        for idx in top_indices:
            chunk = self.chunks[idx].copy()
            chunk['similarity_score'] = float(similarities[idx])
            result_chunks.append(chunk)
        
        print(f"📄 Found {len(result_chunks)} relevant chunks with similarities: {[f'{s:.3f}' for s in similarities[top_indices]]}")
        return result_chunks
    
    def expand_context(self, chunk_ids: List[int], hops: int = 2) -> List[Dict]:
        """Expand context by following relationships"""
        expanded_chunks = []
        visited = set()
        
        def expand_recursive(current_ids, remaining_hops):
            if remaining_hops <= 0:
                return
            
            for chunk_id in current_ids:
                if chunk_id in visited or chunk_id not in self.chunk_index:
                    continue
                
                visited.add(chunk_id)
                chunk = self.chunk_index[chunk_id]
                expanded_chunks.append(chunk)
                
                # Find related chunks
                next_ids = []
                if 'relationships' in chunk:
                    for rel in chunk['relationships']:
                        next_ids.append(rel['target'])
                
                # Also add chunks from the same file (simple relationship)
                same_file_chunks = [c['chunk_id'] for c in self.chunks 
                                  if c['file_name'] == chunk['file_name'] and c['chunk_id'] not in visited]
                next_ids.extend(same_file_chunks[:2])  # Limit to avoid too many
                
                if next_ids and remaining_hops > 1:
                    expand_recursive(next_ids, remaining_hops - 1)
        
        expand_recursive(chunk_ids, hops)
        print(f"📖 Expanded to {len(expanded_chunks)} chunks total")
        return expanded_chunks
    
    def close(self):
        """No-op for compatibility with Neo4j interface"""
        pass
