#!/usr/bin/env python3
"""
Content Chunker for Multimodal Ingestion Pipeline
Creates semantic-aware chunks with overlap for optimal embedding generation
"""

import logging
import re
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

logger = logging.getLogger(__name__)

class ContentChunker:
    """Semantic-aware content chunker with overlap"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, 
                 separators: Optional[List[str]] = None):
        """
        Initialize content chunker
        
        Args:
            chunk_size: Target size for each chunk
            chunk_overlap: Overlap between chunks
            separators: Custom separators for splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Default separators optimized for document content
        if separators is None:
            separators = [
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentences
                "! ",    # Exclamations
                "? ",    # Questions
                "; ",    # Semicolons
                ", ",    # Commas
                " ",     # Words
                ""       # Characters
            ]
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len
        )
        
        logger.info(f"Content chunker initialized: chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def chunk_text(self, text_content: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Chunk text content into semantic pieces
        
        Args:
            text_content: Text to chunk
            metadata: Additional metadata for chunks
            
        Returns:
            List of chunk dictionaries
        """
        try:
            logger.info(f"Chunking text content of length {len(text_content)}")
            
            # Create document for chunking
            doc = Document(page_content=text_content, metadata=metadata or {})
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Convert to dictionary format
            chunk_dicts = []
            for i, chunk in enumerate(chunks):
                chunk_dict = {
                    'id': f"chunk_{i+1}",
                    'content': chunk.page_content,
                    'metadata': chunk.metadata.copy(),
                    'chunk_index': i + 1,
                    'chunk_size': len(chunk.page_content),
                    'start_char': text_content.find(chunk.page_content),
                    'end_char': text_content.find(chunk.page_content) + len(chunk.page_content)
                }
                chunk_dicts.append(chunk_dict)
            
            logger.info(f"Created {len(chunk_dicts)} chunks from text content")
            return chunk_dicts
            
        except Exception as e:
            logger.error(f"Error chunking text content: {e}")
            return []
    
    def chunk_with_image_context(self, text_content: str, image_analyses: List[Dict[str, Any]], 
                                metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Chunk text content with integrated image analysis
        
        Args:
            text_content: Text to chunk
            image_analyses: List of image analysis results
            metadata: Additional metadata for chunks
            
        Returns:
            List of chunk dictionaries with image context
        """
        try:
            logger.info(f"Chunking text with {len(image_analyses)} image analyses")
            
            # Enhance text with image analyses
            enhanced_content = self._integrate_image_analyses(text_content, image_analyses)
            
            # Chunk the enhanced content
            chunks = self.chunk_text(enhanced_content, metadata)
            
            # Add image context to each chunk
            for chunk in chunks:
                chunk['image_context'] = self._get_chunk_image_context(chunk, image_analyses)
                chunk['has_images'] = bool(chunk['image_context'])
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking with image context: {e}")
            return self.chunk_text(text_content, metadata)
    
    def _integrate_image_analyses(self, text_content: str, image_analyses: List[Dict[str, Any]]) -> str:
        """Integrate image analyses into text content"""
        enhanced_content = text_content
        
        for analysis in image_analyses:
            if analysis.get('success') and analysis.get('analysis'):
                image_id = analysis.get('image_id', '')
                image_analysis = analysis.get('analysis', '')
                page_number = analysis.get('page_number', 0)
                
                # Find appropriate location to insert image analysis
                insertion_point = self._find_image_insertion_point(enhanced_content, page_number)
                
                # Create image summary
                image_summary = f"\n\n[Image Analysis - {image_id}]\n{image_analysis}\n"
                
                # Insert at appropriate location
                if insertion_point >= 0:
                    enhanced_content = (enhanced_content[:insertion_point] + 
                                      image_summary + 
                                      enhanced_content[insertion_point:])
                else:
                    # Append to end if no good insertion point found
                    enhanced_content += image_summary
        
        return enhanced_content
    
    def _find_image_insertion_point(self, text_content: str, page_number: int) -> int:
        """Find appropriate location to insert image analysis"""
        try:
            # Look for page markers
            page_markers = list(re.finditer(r'--- Page \d+ ---', text_content))
            
            if page_markers and page_number <= len(page_markers):
                # Insert after the corresponding page marker
                marker = page_markers[page_number - 1]
                return marker.end()
            else:
                # If no page markers, insert at 1/3 of the content
                return len(text_content) // 3
                
        except Exception:
            # Fallback to middle of content
            return len(text_content) // 2
    
    def _get_chunk_image_context(self, chunk: Dict[str, Any], image_analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get image context relevant to a specific chunk"""
        chunk_content = chunk.get('content', '').lower()
        relevant_images = []
        
        for analysis in image_analyses:
            if not analysis.get('success'):
                continue
            
            image_id = analysis.get('image_id', '')
            image_analysis = analysis.get('analysis', '')
            
            # Check if chunk contains image reference or analysis
            if (image_id.lower() in chunk_content or 
                any(word in chunk_content for word in image_analysis.lower().split()[:10])):
                
                relevant_images.append({
                    'image_id': image_id,
                    'analysis': image_analysis,
                    'page_number': analysis.get('page_number', 0),
                    'relevance_score': self._calculate_relevance_score(chunk_content, image_analysis)
                })
        
        # Sort by relevance score
        relevant_images.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_images
    
    def _calculate_relevance_score(self, chunk_content: str, image_analysis: str) -> float:
        """Calculate relevance score between chunk and image analysis"""
        try:
            # Simple word overlap scoring
            chunk_words = set(chunk_content.lower().split())
            analysis_words = set(image_analysis.lower().split())
            
            if not chunk_words or not analysis_words:
                return 0.0
            
            overlap = len(chunk_words.intersection(analysis_words))
            total = len(chunk_words.union(analysis_words))
            
            return overlap / total if total > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def merge_small_chunks(self, chunks: List[Dict[str, Any]], 
                          min_chunk_size: int = 200) -> List[Dict[str, Any]]:
        """
        Merge small chunks with adjacent chunks
        
        Args:
            chunks: List of chunks to merge
            min_chunk_size: Minimum size for a chunk
            
        Returns:
            List of merged chunks
        """
        if not chunks:
            return chunks
        
        merged_chunks = []
        current_chunk = chunks[0].copy()
        
        for next_chunk in chunks[1:]:
            # If current chunk is too small, merge with next
            if len(current_chunk['content']) < min_chunk_size:
                current_chunk['content'] += f"\n\n{next_chunk['content']}"
                current_chunk['end_char'] = next_chunk['end_char']
                
                # Merge image context
                if 'image_context' in current_chunk and 'image_context' in next_chunk:
                    current_chunk['image_context'].extend(next_chunk['image_context'])
                elif 'image_context' in next_chunk:
                    current_chunk['image_context'] = next_chunk['image_context']
                
                current_chunk['has_images'] = current_chunk.get('has_images', False) or next_chunk.get('has_images', False)
            else:
                # Current chunk is large enough, add it and start new
                merged_chunks.append(current_chunk)
                current_chunk = next_chunk.copy()
        
        # Add the last chunk
        merged_chunks.append(current_chunk)
        
        # Update chunk IDs
        for i, chunk in enumerate(merged_chunks):
            chunk['id'] = f"chunk_{i+1}"
            chunk['chunk_index'] = i + 1
        
        logger.info(f"Merged {len(chunks)} chunks into {len(merged_chunks)} chunks")
        return merged_chunks
    
    def get_chunking_summary(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for chunking
        
        Args:
            chunks: List of chunks
            
        Returns:
            Summary statistics
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'average_chunk_size': 0,
                'total_content_length': 0,
                'chunks_with_images': 0
            }
        
        total_content = sum(len(chunk.get('content', '')) for chunk in chunks)
        chunks_with_images = sum(1 for chunk in chunks if chunk.get('has_images', False))
        
        return {
            'total_chunks': len(chunks),
            'average_chunk_size': total_content / len(chunks),
            'total_content_length': total_content,
            'chunks_with_images': chunks_with_images,
            'image_chunk_percentage': (chunks_with_images / len(chunks)) * 100 if chunks else 0
        } 