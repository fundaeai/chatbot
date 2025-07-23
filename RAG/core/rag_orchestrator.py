#!/usr/bin/env python3
"""
RAG Orchestrator
Combines Retrieval, Augmentation, and Generation components
"""

import logging
import time
from typing import Dict, Any, List, Optional
from .retrieval import RetrievalComponent
from .augmentation import AugmentationComponent
from .generation import GenerationComponent
from config import config

logger = logging.getLogger(__name__)

class RAGOrchestrator:
    """Orchestrates the complete RAG pipeline: Retrieval → Augmentation → Generation"""
    
    def __init__(self):
        """Initialize the RAG orchestrator with all three components"""
        # Initialize all three components
        self.retrieval = RetrievalComponent()
        self.augmentation = AugmentationComponent()
        self.generation = GenerationComponent()
        
        logger.info("RAG Orchestrator initialized with all three components")
    
    def ask(self, question: str, top_k: int = 5, search_type: str = "hybrid",
            context_length: int = None, temperature: float = 0.7, 
            max_tokens: int = 500) -> Dict[str, Any]:
        """
        Complete RAG pipeline: Ask a question and get an answer
        
        Args:
            question: The user's question
            top_k: Number of documents to retrieve
            search_type: Type of search ("semantic", "keyword", "hybrid")
            context_length: Maximum context length
            temperature: Response creativity
            max_tokens: Maximum response length
            
        Returns:
            Complete RAG result with answer and metadata
        """
        try:
            start_time = time.time()
            logger.info(f"Starting RAG pipeline for question: '{question[:50]}...'")
            
            # Step 1: Retrieval
            logger.info("Step 1: Retrieving relevant documents")
            retrieved_chunks = self.retrieval.retrieve(question, top_k, search_type)
            
            if not retrieved_chunks:
                logger.warning("No relevant documents found")
                return {
                    'answer': "I couldn't find any relevant information to answer your question. Please try rephrasing or ask about a different topic.",
                    'sources': [],
                    'confidence': 0.0,
                    'processing_time': time.time() - start_time,
                    'steps': {
                        'retrieval': {'status': 'no_results', 'chunks_found': 0},
                        'augmentation': {'status': 'skipped', 'context_length': 0},
                        'generation': {'status': 'skipped', 'tokens_used': 0}
                    }
                }
            
            # Step 2: Augmentation
            logger.info("Step 2: Augmenting context")
            context = self.augmentation.augment(retrieved_chunks, context_length)
            
            if not context.strip():
                logger.warning("Failed to build context from retrieved chunks")
                return {
                    'answer': "I found some documents but couldn't build proper context. Please try a different question.",
                    'sources': self._format_sources(retrieved_chunks),
                    'confidence': 0.0,
                    'processing_time': time.time() - start_time,
                    'steps': {
                        'retrieval': {'status': 'success', 'chunks_found': len(retrieved_chunks)},
                        'augmentation': {'status': 'failed', 'context_length': 0},
                        'generation': {'status': 'skipped', 'tokens_used': 0}
                    }
                }
            
            # Step 3: Generation
            logger.info("Step 3: Generating answer")
            generation_result = self.generation.generate(question, context, temperature, max_tokens)
            
            # Calculate total processing time
            total_time = time.time() - start_time
            
            # Prepare final result
            result = {
                'answer': generation_result['answer'],
                'sources': self._format_sources(retrieved_chunks),
                'confidence': generation_result.get('confidence', 0.0),
                'processing_time': total_time,
                'context_length': len(context),
                'search_type': search_type,
                'steps': {
                    'retrieval': {
                        'status': 'success',
                        'chunks_found': len(retrieved_chunks),
                        'time': 0.0  # Could be enhanced with timing
                    },
                    'augmentation': {
                        'status': 'success',
                        'context_length': len(context),
                        'time': 0.0  # Could be enhanced with timing
                    },
                    'generation': {
                        'status': 'success',
                        'tokens_used': generation_result.get('tokens_used', 0),
                        'time': generation_result.get('generation_time', 0.0)
                    }
                }
            }
            
            logger.info(f"RAG pipeline completed in {total_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return {
                'answer': f"Sorry, I encountered an error while processing your question: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'processing_time': time.time() - start_time,
                'error': str(e),
                'steps': {
                    'retrieval': {'status': 'error'},
                    'augmentation': {'status': 'error'},
                    'generation': {'status': 'error'}
                }
            }
    
    def search_only(self, query: str, top_k: int = 5, search_type: str = "hybrid") -> List[Dict[str, Any]]:
        """
        Only perform retrieval (Step 1)
        
        Args:
            query: Search query
            top_k: Number of results
            search_type: Type of search
            
        Returns:
            List of retrieved chunks
        """
        try:
            logger.info(f"Performing search-only for query: '{query}'")
            return self.retrieval.retrieve(query, top_k, search_type)
        except Exception as e:
            logger.error(f"Error in search-only: {e}")
            return []
    
    def get_pipeline_statistics(self) -> Dict[str, Any]:
        """Get statistics from all three components"""
        try:
            retrieval_stats = self.retrieval.get_statistics()
            augmentation_stats = self.augmentation.get_augmentation_summary([], "")
            generation_stats = self.generation.get_generation_summary({})
            
            return {
                'retrieval': retrieval_stats,
                'augmentation': augmentation_stats,
                'generation': generation_stats,
                'pipeline': 'RAG with GPT-4'
            }
        except Exception as e:
            logger.error(f"Error getting pipeline statistics: {e}")
            return {'error': str(e)}
    
    def _format_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format retrieved chunks as sources
        
        Args:
            chunks: Retrieved chunks
            
        Returns:
            List of formatted sources
        """
        sources = []
        for chunk in chunks:
            sources.append({
                'filename': chunk.get('filename', ''),
                'page': chunk.get('page_number', 0),
                'content': chunk.get('content', '')[:200] + "..." if len(chunk.get('content', '')) > 200 else chunk.get('content', ''),
                'score': chunk.get('score', 0.0),
                'chunk_type': chunk.get('chunk_type', 'text')
            })
        return sources
    
    def validate_pipeline(self) -> Dict[str, Any]:
        """Validate that all components are working correctly"""
        try:
            validation = {
                'retrieval': {'status': 'unknown'},
                'augmentation': {'status': 'unknown'},
                'generation': {'status': 'unknown'},
                'overall': 'unknown'
            }
            
            # Test retrieval
            try:
                retrieval_stats = self.retrieval.get_statistics()
                if 'error' not in retrieval_stats:
                    validation['retrieval'] = {'status': 'healthy', 'total_docs': retrieval_stats.get('total_documents', 0)}
                else:
                    validation['retrieval'] = {'status': 'error', 'error': retrieval_stats['error']}
            except Exception as e:
                validation['retrieval'] = {'status': 'error', 'error': str(e)}
            
            # Test augmentation (basic validation)
            try:
                test_context = self.augmentation.augment([], 100)
                validation['augmentation'] = {'status': 'healthy'}
            except Exception as e:
                validation['augmentation'] = {'status': 'error', 'error': str(e)}
            
            # Test generation (basic validation)
            try:
                test_result = self.generation.generate("test", "test context", 0.7, 50)
                validation['generation'] = {'status': 'healthy'}
            except Exception as e:
                validation['generation'] = {'status': 'error', 'error': str(e)}
            
            # Overall status
            all_healthy = all(comp['status'] == 'healthy' for comp in validation.values() if isinstance(comp, dict) and 'status' in comp)
            validation['overall'] = 'healthy' if all_healthy else 'error'
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validating pipeline: {e}")
            return {'error': str(e)}

# Example usage
if __name__ == "__main__":
    # Initialize RAG orchestrator
    rag = RAGOrchestrator()
    
    # Ask a question
    result = rag.ask("What is machine learning?")
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Sources: {len(result['sources'])}") 