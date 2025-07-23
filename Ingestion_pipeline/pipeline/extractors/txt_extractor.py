#!/usr/bin/env python3
"""
TXT Content Extractor
Extracts text from TXT documents
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TXTExtractor:
    """TXT extractor for text content"""
    
    def __init__(self, temp_dir: str = "temp_images"):
        """Initialize TXT extractor"""
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        self.temp_files = set()
    
    def extract_content(self, file_path: Path) -> Dict[str, Any]:
        """Extract content from TXT file"""
        try:
            logger.info(f"Extracting content from TXT: {file_path}")
            
            # Read text content
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            return {
                'success': True,
                'text_content': text_content,
                'visual_elements': [],  # TXT files don't have images
                'metadata': {
                    'filename': file_path.name,
                    'file_type': '.txt',
                    'extractor': 'TXTExtractor',
                    'content_length': len(text_content)
                },
                'filename': file_path.name,
                'file_size': file_path.stat().st_size,
                'temp_files_created': 0
            }
            
        except Exception as e:
            logger.error(f"Error extracting TXT content: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': file_path.name
            }
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        # TXT extractor doesn't create temp files
        pass 