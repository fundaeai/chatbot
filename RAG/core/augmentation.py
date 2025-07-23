#!/usr/bin/env python3
"""
Step 2: Augmentation Component
Builds context by combining retrieved chunks
"""

import logging
import time
from typing import List, Dict, Any, Optional
from config import config
from config.hyperparameters import RAGHyperparameters

logger = logging.getLogger(__name__)

class AugmentationComponent:
    """Step 2: Augments retrieved chunks into context for the language model"""
    
    def __init__(self):
        """Initialize the augmentation component"""
        logger.info("Augmentation component initialized")
    
    def augment(self, retrieved_chunks: List[Dict[str, Any]], max_length: int = None) -> str:
        """
        Augment retrieved chunks into context
        
        Args:
            retrieved_chunks: List of retrieved document chunks
            max_length: Maximum context length
            
        Returns:
            Formatted context string
        """
        try:
            start_time = time.time()
            logger.info(f"Augmenting {len(retrieved_chunks)} chunks into context")
            
            if not retrieved_chunks:
                logger.warning("No chunks to augment")
                return ""
            
            # Build context from chunks
            context = self._build_context(retrieved_chunks, max_length)
            
            augmentation_time = time.time() - start_time
            logger.info(f"Augmented context length: {len(context)} chars in {augmentation_time:.3f}s")
            
            return context
            
        except Exception as e:
            logger.error(f"Error in augmentation: {e}")
            return ""
    
    def _build_context(self, chunks: List[Dict[str, Any]], max_length: int = None) -> str:
        """
        Build context string from retrieved chunks
        
        Args:
            chunks: List of retrieved chunks
            max_length: Maximum context length
            
        Returns:
            Formatted context string
        """
        try:
            max_length = max_length or RAGHyperparameters.DEFAULT_CONTEXT_LENGTH
            context_parts = []
            current_length = 0
            
            # Sort chunks by relevance score (highest first)
            sorted_chunks = sorted(chunks, key=lambda x: x.get('score', 0), reverse=True)
            
            for chunk in sorted_chunks:
                content = chunk.get('content', '')
                filename = chunk.get('filename', '')
                page = chunk.get('page_number', 0)
                score = chunk.get('score', 0.0)
                chunk_type = chunk.get('chunk_type', 'text')
                tags = chunk.get('tags', [])
                upload_date = chunk.get('upload_date', '')
                
                # Format the context part with source information
                context_part = self._format_chunk_with_source(content, filename, page, score, chunk_type, tags, upload_date)
                
                # Check if adding this would exceed the limit
                if current_length + len(context_part) > max_length:
                    logger.info(f"Context length limit reached ({max_length} chars)")
                    break
                
                context_parts.append(context_part)
                current_length += len(context_part)
            
            # Join all parts with separators
            final_context = "\n\n".join(context_parts)
            
            logger.info(f"Built context with {len(context_parts)} chunks, total length: {len(final_context)}")
            return final_context
            
        except Exception as e:
            logger.error(f"Error building context: {e}")
            return ""
    
    def _format_chunk_with_source(self, content: str, filename: str, page: int, score: float, 
                                 chunk_type: str = 'text', tags: list = None, upload_date: str = '') -> str:
        """
        Format a chunk with source information
        
        Args:
            content: The chunk content
            filename: Source filename
            page: Page number
            score: Relevance score
            chunk_type: Type of chunk (text, image, etc.)
            tags: Associated tags
            upload_date: Upload date
            
        Returns:
            Formatted chunk with source info
        """
        try:
            # Clean and format the content
            cleaned_content = content.strip()
            
            # Create source header using hyperparameter format
            source_header = RAGHyperparameters.SOURCE_FORMAT.format(
                filename=filename, 
                page=page, 
                score=score
            )
            
            # Add additional metadata if available
            metadata_parts = []
            if chunk_type and chunk_type != 'text':
                metadata_parts.append(f"Type: {chunk_type}")
            if tags:
                metadata_parts.append(f"Tags: {', '.join(tags)}")
            if upload_date:
                metadata_parts.append(f"Uploaded: {upload_date}")
            
            if metadata_parts:
                metadata_line = f"[Metadata: {' | '.join(metadata_parts)}]"
                source_header = f"{source_header}\n{metadata_line}"
            
            # Combine source header with content
            formatted_chunk = f"{source_header}\n{cleaned_content}"
            
            return formatted_chunk
            
        except Exception as e:
            logger.error(f"Error formatting chunk: {e}")
            return content
    
    def get_augmentation_summary(self, chunks: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
        """
        Get summary of augmentation process
        
        Args:
            chunks: Original retrieved chunks
            context: Final augmented context
            
        Returns:
            Summary dictionary
        """
        try:
            total_chunks = len(chunks)
            context_length = len(context)
            
            # Calculate average score
            scores = [chunk.get('score', 0.0) for chunk in chunks]
            avg_score = sum(scores) / len(scores) if scores else 0.0
            
            # Get unique sources
            sources = set(chunk.get('filename', '') for chunk in chunks)
            
            return {
                'chunks_processed': total_chunks,
                'context_length': context_length,
                'average_score': avg_score,
                'unique_sources': len(sources),
                'sources': list(sources)
            }
            
        except Exception as e:
            logger.error(f"Error getting augmentation summary: {e}")
            return {'error': str(e)}
    
    def validate_context(self, context: str) -> Dict[str, Any]:
        """
        Validate the augmented context
        
        Args:
            context: The augmented context to validate
            
        Returns:
            Validation results
        """
        try:
            validation = {
                'is_valid': True,
                'length': len(context),
                'has_content': bool(context.strip()),
                'issues': []
            }
            
            # Check if context is empty
            if not context.strip():
                validation['is_valid'] = False
                validation['issues'].append("Context is empty")
            
            # Check if context is too short
            if len(context) < 100:
                validation['issues'].append("Context is very short")
            
            # Check if context is too long
            max_length = RAGHyperparameters.MAX_CONTEXT_LENGTH
            if len(context) > max_length:
                validation['issues'].append(f"Context exceeds maximum length ({max_length})")
            
            # Check for source formatting
            if "[Source:" not in context:
                validation['issues'].append("Missing source information")
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validating context: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'issues': ['Validation error occurred']
            }

# Import time for timing
import time 