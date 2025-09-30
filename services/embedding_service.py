import logging
from typing import Optional, List
import numpy as np
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating text embeddings using Google's Gemini API"""
    
    def __init__(self):
        """Initialize the embedding service"""
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model_name = settings.embedding_model
            logger.info(f"Embedding service initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            raise
    
    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for a single text"""
        try:
            if not text or not text.strip():
                return None
            
            # Use Gemini's embedding model
            result = genai.embed_content(
                model=self.model_name,
                content=text.strip()
            )
            
            # Convert to numpy array
            embedding = np.array(result['embedding'])
            
            logger.debug(f"Generated embedding with shape: {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding generation failed for text length {len(text)}: {e}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        
        return embeddings
    
    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return float(dot_product / (norm_a * norm_b))
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0