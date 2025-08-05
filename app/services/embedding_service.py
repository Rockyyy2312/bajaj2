import pinecone
import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from app.utils.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Handle text embeddings and vector search using Pinecone"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.vector_dimension = settings.VECTOR_DIMENSION
        
        # Initialize sentence transformer model
        self.embedding_model = SentenceTransformer(self.model_name)
        
        # Initialize Pinecone
        self.pinecone = pinecone.Pinecone(
            api_key=settings.PINECONE_API_KEY
        )
        
        # Get or create index
        self.index_name = settings.PINECONE_INDEX_NAME
        self._ensure_index_exists()
        
    def _ensure_index_exists(self):
        """Ensure Pinecone index exists, create if not"""
        try:
            if self.index_name not in self.pinecone.list_indexes().names():
                self.pinecone.create_index(
                    name=self.index_name,
                    dimension=self.vector_dimension,
                    metric="cosine"
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            else:
                logger.info(f"Using existing Pinecone index: {self.index_name}")
        except Exception as e:
            logger.error(f"Error ensuring Pinecone index exists: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            embeddings = self.embedding_model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def get_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            embedding = self.embedding_model.encode([text])
            return embedding[0].tolist()
        except Exception as e:
            logger.error(f"Error generating single embedding: {e}")
            raise
    
    def upsert_clauses(self, clauses: List[Dict[str, Any]], document_id: str) -> bool:
        """Upsert clauses to Pinecone index"""
        try:
            index = self.pinecone.Index(self.index_name)
            
            vectors = []
            for clause in clauses:
                # Generate embedding for clause content
                embedding = self.get_single_embedding(clause["clause_content"])
                
                # Create metadata
                metadata = {
                    "document_id": document_id,
                    "clause_id": clause["clause_id"],
                    "clause_title": clause["clause_title"],
                    "clause_content": clause["clause_content"],
                    "content_type": "clause"
                }
                
                # Create vector record
                vector_id = f"{document_id}_{clause['clause_id']}"
                vectors.append((vector_id, embedding, metadata))
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                index.upsert(vectors=batch)
            
            logger.info(f"Upserted {len(vectors)} clauses for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting clauses to Pinecone: {e}")
            return False
    
    def search_similar_clauses(self, query: str, top_k: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar clauses using vector similarity"""
        try:
            index = self.pinecone.Index(self.index_name)
            
            # Generate query embedding
            query_embedding = self.get_single_embedding(query)
            
            # Perform search
            search_kwargs = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True
            }
            
            if filter_dict:
                search_kwargs["filter"] = filter_dict
            
            results = index.query(**search_kwargs)
            
            # Format results
            matched_clauses = []
            for match in results.matches:
                metadata = match.metadata
                matched_clauses.append({
                    "clause_id": metadata.get("clause_id", ""),
                    "clause_title": metadata.get("clause_title", ""),
                    "clause_content": metadata.get("clause_content", ""),
                    "relevance_score": match.score,
                    "document_id": metadata.get("document_id", ""),
                    "content_type": metadata.get("content_type", "clause")
                })
            
            logger.info(f"Found {len(matched_clauses)} similar clauses for query")
            return matched_clauses
            
        except Exception as e:
            logger.error(f"Error searching similar clauses: {e}")
            return []
    
    def delete_document_clauses(self, document_id: str) -> bool:
        """Delete all clauses for a specific document"""
        try:
            index = self.pinecone.Index(self.index_name)
            
            # Delete vectors with document_id filter
            index.delete(filter={"document_id": document_id})
            
            logger.info(f"Deleted clauses for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document clauses: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get Pinecone index statistics"""
        try:
            index = self.pinecone.Index(self.index_name)
            stats = index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}
