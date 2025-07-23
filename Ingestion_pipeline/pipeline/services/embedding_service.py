#!/usr/bin/env python3
"""
Embedding Service for Multimodal Ingestion Pipeline
Generates vector embeddings using Azure OpenAI
"""

import logging
import time
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from ..utils.config import Config

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Azure OpenAI embedding service for text chunks"""
    
    def __init__(self):
        """Initialize the embedding service"""
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        self.model = Config.EMBEDDING_MODEL
        self.deployment = Config.EMBEDDING_DEPLOYMENT_NAME
        
        # Rate limiting and retry settings
        self.max_retries = 3
        self.retry_delay = 1.0
        self.batch_size = 16  # Azure OpenAI batch size limit
        
        logger.info(f"Embedding service initialized with model: {self.model}")
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for text chunks
        
        Args:
            chunks: List of chunk dictionaries with 'content' key
            
        Returns:
            List of chunks with embeddings added
        """
        try:
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            
            # Prepare text inputs
            texts = [chunk.get('content', '') for chunk in chunks]
            
            # Generate embeddings in batches
            embeddings = self._generate_embeddings_batch(texts)
            
            # Add embeddings to chunks
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk['embedding'] = embedding
                chunk['embedding_model'] = self.model
                chunk['embedding_timestamp'] = time.time()
            
            logger.info(f"Successfully generated embeddings for {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return chunks
    
    def _generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings in batches to handle rate limits
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            
            for attempt in range(self.max_retries):
                try:
                    logger.debug(f"Generating embeddings for batch {i//self.batch_size + 1}")
                    
                    response = self.client.embeddings.create(
                        model=self.deployment,
                        input=batch_texts
                    )
                    
                    # Extract embeddings
                    batch_embeddings = [data.embedding for data in response.data]
                    all_embeddings.extend(batch_embeddings)
                    
                    logger.debug(f"Successfully generated {len(batch_embeddings)} embeddings")
                    break
                    
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for batch {i//self.batch_size + 1}: {e}")
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"Failed to generate embeddings for batch after {self.max_retries} attempts")
                        # Return zero vectors for failed batch
                        all_embeddings.extend([[0.0] * 1536] * len(batch_texts))  # Default embedding dimension
        
        return all_embeddings
    
    def generate_single_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        try:
            response = self.client.embeddings.create(
                model=self.deployment,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating single embedding: {e}")
            return None
    
    def get_embedding_summary(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for embeddings
        
        Args:
            chunks: List of chunks with embeddings
            
        Returns:
            Summary statistics
        """
        chunks_with_embeddings = [c for c in chunks if 'embedding' in c]
        chunks_without_embeddings = [c for c in chunks if 'embedding' not in c]
        
        embedding_dimensions = []
        for chunk in chunks_with_embeddings:
            if 'embedding' in chunk:
                embedding_dimensions.append(len(chunk['embedding']))
        
        return {
            'total_chunks': len(chunks),
            'chunks_with_embeddings': len(chunks_with_embeddings),
            'chunks_without_embeddings': len(chunks_without_embeddings),
            'embedding_success_rate': len(chunks_with_embeddings) / max(len(chunks), 1) * 100,
            'embedding_dimension': embedding_dimensions[0] if embedding_dimensions else 0,
            'model_used': self.model,
            'average_embedding_magnitude': self._calculate_average_magnitude(chunks_with_embeddings)
        }
    
    def _calculate_average_magnitude(self, chunks: List[Dict[str, Any]]) -> float:
        """Calculate average magnitude of embeddings"""
        if not chunks:
            return 0.0
        
        total_magnitude = 0.0
        count = 0
        
        for chunk in chunks:
            if 'embedding' in chunk:
                embedding = chunk['embedding']
                magnitude = sum(x * x for x in embedding) ** 0.5
                total_magnitude += magnitude
                count += 1
        
        return total_magnitude / count if count > 0 else 0.0
    
    def validate_embeddings(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate embedding quality and consistency
        
        Args:
            chunks: List of chunks with embeddings
            
        Returns:
            Validation results
        """
        validation_results = {
            'total_chunks': len(chunks),
            'valid_embeddings': 0,
            'invalid_embeddings': 0,
            'zero_embeddings': 0,
            'dimension_mismatches': 0,
            'expected_dimension': 1536  # Default for text-embedding-ada-002
        }
        
        for chunk in chunks:
            if 'embedding' not in chunk:
                validation_results['invalid_embeddings'] += 1
                continue
            
            embedding = chunk['embedding']
            
            # Check if embedding is a list
            if not isinstance(embedding, list):
                validation_results['invalid_embeddings'] += 1
                continue
            
            # Check dimension
            if len(embedding) != validation_results['expected_dimension']:
                validation_results['dimension_mismatches'] += 1
                continue
            
            # Check for zero embeddings
            if all(x == 0.0 for x in embedding):
                validation_results['zero_embeddings'] += 1
                continue
            
            validation_results['valid_embeddings'] += 1
        
        validation_results['validation_success_rate'] = (
            validation_results['valid_embeddings'] / max(validation_results['total_chunks'], 1) * 100
        )
        
        return validation_results 