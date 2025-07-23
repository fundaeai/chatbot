#!/usr/bin/env python3
"""
Multimodal Ingestion Pipeline
End-to-end pipeline for processing documents with text and visual content
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .dispatcher import ContentDispatcher
from .agents.image_captioning_agent import ImageCaptioningAgent
from .utils.chunker import ContentChunker
from .services.embedding_service import EmbeddingService
from .utils.config import Config

logger = logging.getLogger(__name__)

class MultimodalPipeline:
    """End-to-end multimodal ingestion pipeline"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the multimodal pipeline
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Initialize components
        self.dispatcher = ContentDispatcher()
        self.image_agent = ImageCaptioningAgent()
        self.chunker = ContentChunker(
            chunk_size=self.config.get('chunk_size', 1000),
            chunk_overlap=self.config.get('chunk_overlap', 200)
        )
        self.embedding_service = EmbeddingService()
        
        # Pipeline statistics
        self.stats = {
            'files_processed': 0,
            'total_chunks': 0,
            'total_images': 0,
            'total_embeddings': 0,
            'processing_times': []
        }
        
        logger.info("Multimodal pipeline initialized")
    
    def process_document(self, file_path: str, save_outputs: bool = False, 
                        auto_cleanup: bool = True) -> Dict[str, Any]:
        """
        Process a single document through the complete pipeline
        
        Args:
            file_path: Path to the document file
            save_outputs: Whether to save intermediate outputs
            auto_cleanup: Whether to automatically cleanup temporary files
            
        Returns:
            Complete processing results
        """
        start_time = time.time()
        file_path = Path(file_path)
        
        try:
            logger.info(f"Starting pipeline processing for: {file_path}")
            
            # Step 1: Content Extraction
            logger.info("Step 1: Extracting content from document")
            extraction_result = self.dispatcher.extract_content(file_path)
            
            if not extraction_result.get('success'):
                raise Exception(f"Content extraction failed: {extraction_result.get('error')}")
            
            # Step 2: Image Analysis
            logger.info("Step 2: Analyzing visual elements")
            image_analyses = self._analyze_visual_elements(
                extraction_result.get('visual_elements', []),
                extraction_result.get('text_content', '')
            )
            
            # Step 3: Content Chunking
            logger.info("Step 3: Chunking content with image context")
            chunks = self.chunker.chunk_with_image_context(
                extraction_result.get('text_content', ''),
                image_analyses,
                extraction_result.get('metadata', {})
            )
            
            # Step 4: Generate Embeddings
            logger.info("Step 4: Generating embeddings")
            chunks_with_embeddings = self.embedding_service.generate_embeddings(chunks)
            
            # Step 5: Prepare Final Output
            logger.info("Step 5: Preparing final output")
            final_result = self._prepare_final_output(
                file_path, extraction_result, image_analyses, chunks_with_embeddings
            )
            
            # Step 6: Save outputs if requested
            if save_outputs:
                self._save_processing_outputs(file_path, final_result)
            
            # Step 7: Cleanup temporary files
            if auto_cleanup:
                self._cleanup_temp_files(extraction_result)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_statistics(final_result, processing_time)
            
            logger.info(f"Pipeline processing completed in {processing_time:.2f} seconds")
            return final_result
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': file_path.name,
                'processing_time': time.time() - start_time
            }
    
    def _analyze_visual_elements(self, visual_elements: List[Dict[str, Any]], 
                                text_content: str) -> List[Dict[str, Any]]:
        """Analyze visual elements using GPT-4.1 Vision"""
        if not visual_elements:
            logger.info("No visual elements found for analysis")
            return []
        
        logger.info(f"Analyzing {len(visual_elements)} visual elements")
        
        # Prepare image data for analysis
        images_for_analysis = []
        for element in visual_elements:
            images_for_analysis.append({
                'path': element.get('path'),
                'id': element.get('id'),
                'page_number': element.get('page_number', 1)
            })
        
        # Analyze images with context
        image_analyses = []
        for image_info in images_for_analysis:
            # Get context for this image
            context = self.image_agent.get_image_context(
                text_content, 
                image_info.get('page_number', 1)
            )
            
            # Analyze the image
            analysis = self.image_agent.analyze_image(
                image_path=image_info['path'],
                context_text=context,
                image_id=image_info['id'],
                analysis_type='document'
            )
            
            # Add metadata from original element
            analysis.update({
                'page_number': image_info.get('page_number', 1),
                'type': next((e.get('type') for e in visual_elements if e.get('id') == image_info['id']), 'unknown'),
                'size': next((e.get('size') for e in visual_elements if e.get('id') == image_info['id']), 0),
                'width': next((e.get('width') for e in visual_elements if e.get('id') == image_info['id']), 0),
                'height': next((e.get('height') for e in visual_elements if e.get('id') == image_info['id']), 0)
            })
            
            image_analyses.append(analysis)
        
        return image_analyses
    
    def _prepare_final_output(self, file_path: Path, extraction_result: Dict[str, Any],
                             image_analyses: List[Dict[str, Any]], 
                             chunks_with_embeddings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare the final output structure"""
        
        # Generate summaries
        chunking_summary = self.chunker.get_chunking_summary(chunks_with_embeddings)
        embedding_summary = self.embedding_service.get_embedding_summary(chunks_with_embeddings)
        image_summary = self.image_agent.get_analysis_summary(image_analyses)
        
        # Prepare chunks for storage
        storage_chunks = []
        for chunk in chunks_with_embeddings:
            storage_chunk = {
                'id': f"{file_path.stem}_{chunk['id']}",
                'content': chunk['content'],
                'embedding': chunk.get('embedding', []),
                'metadata': {
                    'filename': file_path.name,
                    'chunk_index': chunk.get('chunk_index', 0),
                    'chunk_size': chunk.get('chunk_size', 0),
                    'has_images': chunk.get('has_images', False),
                    'image_context': chunk.get('image_context', []),
                    'embedding_model': chunk.get('embedding_model', ''),
                    'embedding_timestamp': chunk.get('embedding_timestamp', 0)
                }
            }
            storage_chunks.append(storage_chunk)
        
        return {
            'success': True,
            'filename': file_path.name,
            'file_path': str(file_path),
            'file_size': extraction_result.get('file_size', 0),
            'processing_timestamp': datetime.utcnow().isoformat(),
            
            # Content
            'text_content': extraction_result.get('text_content', ''),
            'visual_elements': extraction_result.get('visual_elements', []),
            'image_analyses': image_analyses,
            'chunks': storage_chunks,
            
            # Metadata
            'metadata': extraction_result.get('metadata', {}),
            
            # Summaries
            'summaries': {
                'chunking': chunking_summary,
                'embedding': embedding_summary,
                'image_analysis': image_summary
            },
            
            # Statistics
            'statistics': {
                'total_chunks': len(storage_chunks),
                'total_images': len(image_analyses),
                'successful_image_analyses': len([a for a in image_analyses if a.get('success')]),
                'chunks_with_images': sum(1 for c in storage_chunks if c['metadata']['has_images']),
                'embedding_success_rate': embedding_summary.get('embedding_success_rate', 0)
            }
        }
    
    def _save_processing_outputs(self, file_path: Path, result: Dict[str, Any]):
        """Save processing outputs for debugging/analysis"""
        try:
            output_dir = Path("test_outputs")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            base_name = f"{file_path.stem}_pipeline_output_{timestamp}"
            
            # Save JSON result
            import json
            json_path = output_dir / f"{base_name}.json"
            with open(json_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            # Save extracted text
            text_path = output_dir / f"{base_name}_extracted_text.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(result.get('text_content', ''))
            
            # Save enhanced content with image analyses
            enhanced_content = self.image_agent.enhance_content_with_image_analysis(
                result.get('text_content', ''),
                result.get('image_analyses', [])
            )
            enhanced_path = output_dir / f"{base_name}_enhanced_content.txt"
            with open(enhanced_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
            
            logger.info(f"Processing outputs saved to {output_dir}")
            
        except Exception as e:
            logger.error(f"Error saving processing outputs: {e}")
    
    def _cleanup_temp_files(self, extraction_result: Dict[str, Any]):
        """Clean up temporary files"""
        try:
            # Import cleanup utility
            from pipeline.utils.cleanup_utility import CleanupUtility
            
            # Initialize cleanup utility
            cleanup_util = CleanupUtility()
            
            # Clean up from extractors first
            cleaned_count = 0
            failed_count = 0
            
            if hasattr(self.dispatcher, 'extractors'):
                for extractor in self.dispatcher.extractors.values():
                    if hasattr(extractor, 'cleanup_temp_files'):
                        cleaned, failed = extractor.cleanup_temp_files()
                        cleaned_count += cleaned
                        failed_count += failed
            
            # Use comprehensive cleanup utility
            util_cleaned, util_failed = cleanup_util.cleanup_all_temp_files()
            cleaned_count += util_cleaned
            failed_count += util_failed
            
            logger.info(f"Production cleanup completed: {cleaned_count} cleaned, {failed_count} failed")
            
            # Log cleanup report for debugging
            report = cleanup_util.get_cleanup_report()
            if report['total_cleaned'] > 0:
                logger.info(f"Cleanup success rate: {report['success_rate']:.2%}")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            # Fallback to basic cleanup
            try:
                import os
                from pathlib import Path
                
                temp_dir = Path("temp_images")
                if temp_dir.exists():
                    for temp_file in temp_dir.glob("*.png"):
                        try:
                            os.unlink(temp_file)
                        except Exception as fallback_e:
                            logger.error(f"Fallback cleanup failed for {temp_file}: {fallback_e}")
            except Exception as fallback_e:
                logger.error(f"Fallback cleanup completely failed: {fallback_e}")
    
    def _update_statistics(self, result: Dict[str, Any], processing_time: float):
        """Update pipeline statistics"""
        self.stats['files_processed'] += 1
        self.stats['total_chunks'] += result.get('statistics', {}).get('total_chunks', 0)
        self.stats['total_images'] += result.get('statistics', {}).get('total_images', 0)
        self.stats['total_embeddings'] += result.get('statistics', {}).get('total_chunks', 0)
        self.stats['processing_times'].append(processing_time)
    
    def get_pipeline_statistics(self) -> Dict[str, Any]:
        """Get overall pipeline statistics"""
        if not self.stats['processing_times']:
            return self.stats
        
        return {
            **self.stats,
            'average_processing_time': sum(self.stats['processing_times']) / len(self.stats['processing_times']),
            'total_processing_time': sum(self.stats['processing_times']),
            'fastest_processing': min(self.stats['processing_times']),
            'slowest_processing': max(self.stats['processing_times'])
        }
    
    def process_batch(self, file_paths: List[str], save_outputs: bool = False, 
                     auto_cleanup: bool = True) -> List[Dict[str, Any]]:
        """
        Process multiple documents in batch
        
        Args:
            file_paths: List of file paths to process
            save_outputs: Whether to save intermediate outputs
            auto_cleanup: Whether to automatically cleanup temporary files
            
        Returns:
            List of processing results
        """
        results = []
        
        for i, file_path in enumerate(file_paths):
            logger.info(f"Processing file {i+1}/{len(file_paths)}: {file_path}")
            
            result = self.process_document(file_path, save_outputs, auto_cleanup)
            results.append(result)
            
            if not result.get('success'):
                logger.warning(f"Failed to process {file_path}: {result.get('error')}")
        
        logger.info(f"Batch processing completed: {len(results)} files processed")
        return results 