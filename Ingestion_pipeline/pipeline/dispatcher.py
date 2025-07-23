#!/usr/bin/env python3
"""
File Type Dispatcher for Multimodal Ingestion Pipeline
Routes different file types to appropriate content extractors
"""

import logging
from pathlib import Path
from typing import Dict, Any, Union
from .extractors.pdf_extractor import PDFExtractor
from .extractors.docx_extractor import DOCXExtractor
from .extractors.pptx_extractor import PPTXExtractor
from .extractors.txt_extractor import TXTExtractor
from .extractors.markdown_extractor import MarkdownExtractor

logger = logging.getLogger(__name__)

class ContentDispatcher:
    """Dispatcher for routing file types to appropriate extractors"""
    
    def __init__(self):
        """Initialize the content dispatcher with supported extractors"""
        self.extractors = {
            '.pdf': PDFExtractor(),
            '.docx': DOCXExtractor(),
            '.doc': DOCXExtractor(),
            '.pptx': PPTXExtractor(),
            '.ppt': PPTXExtractor(),
            '.txt': TXTExtractor(),
            '.md': MarkdownExtractor(),
            '.markdown': MarkdownExtractor()
        }
        
        self.supported_extensions = list(self.extractors.keys())
        logger.info(f"Content dispatcher initialized with support for: {self.supported_extensions}")
    
    def dispatch_extractor(self, file_path: Union[str, Path]) -> Any:
        """
        Dispatch file to appropriate extractor based on file extension
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Appropriate extractor instance
            
        Raises:
            ValueError: If file type is not supported
        """
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower()
        
        if file_extension not in self.extractors:
            raise ValueError(f"Unsupported file type: {file_extension}. Supported types: {self.supported_extensions}")
        
        extractor = self.extractors[file_extension]
        logger.info(f"Dispatching {file_path} to {extractor.__class__.__name__}")
        
        return extractor
    
    def extract_content(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Extract content from file using appropriate extractor
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary containing extracted text and images
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extractor = self.dispatch_extractor(file_path)
        return extractor.extract_content(file_path)
    
    def get_supported_extensions(self) -> list:
        """Get list of supported file extensions"""
        return self.supported_extensions.copy()
    
    def is_supported(self, file_path: Union[str, Path]) -> bool:
        """Check if file type is supported"""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.extractors 