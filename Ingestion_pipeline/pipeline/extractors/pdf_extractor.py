#!/usr/bin/env python3
"""
PDF Content Extractor using PyMuPDF
Extracts text and individual visual elements from PDF documents
"""

import logging
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import fitz  # PyMuPDF
from PIL import Image
import io

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Enhanced PDF extractor with individual visual element extraction"""
    
    def __init__(self, temp_dir: str = "temp_images"):
        """
        Initialize PDF extractor
        
        Args:
            temp_dir: Directory for temporary image files
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        self.temp_files = set()
        
    def extract_content(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text and visual elements from PDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text and images
        """
        try:
            logger.info(f"Extracting content from PDF: {file_path}")
            
            # Open PDF
            pdf_document = fitz.open(str(file_path))
            
            # Extract text content
            text_content = self._extract_text(pdf_document)
            
            # Extract visual elements
            visual_elements = self._extract_visual_elements(pdf_document, file_path.stem)
            
            # Extract metadata
            metadata = self._extract_metadata(pdf_document, file_path)
            
            pdf_document.close()
            
            return {
                'success': True,
                'text_content': text_content,
                'visual_elements': visual_elements,
                'metadata': metadata,
                'filename': file_path.name,
                'file_size': file_path.stat().st_size,
                'temp_files_created': len(self.temp_files)
            }
            
        except Exception as e:
            logger.error(f"Error extracting PDF content: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': file_path.name
            }
    
    def _extract_text(self, pdf_document: fitz.Document) -> str:
        """Extract text content from PDF"""
        text_content = []
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            page_text = page.get_text()
            text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
        
        return "\n\n".join(text_content)
    
    def _extract_visual_elements(self, pdf_document: fitz.Document, filename: str) -> List[Dict[str, Any]]:
        """Extract individual visual elements from PDF"""
        visual_elements = []
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Extract embedded images
            embedded_images = self._extract_embedded_images(pdf_document, page, page_num, filename)
            visual_elements.extend(embedded_images)
            
            # Extract visual elements from drawings
            drawing_elements = self._extract_drawing_elements(page, page_num, filename)
            visual_elements.extend(drawing_elements)
        
        logger.info(f"Extracted {len(visual_elements)} visual elements from PDF")
        return visual_elements
    
    def _extract_embedded_images(self, pdf_document: fitz.Document, page: fitz.Page, 
                                page_num: int, filename: str) -> List[Dict[str, Any]]:
        """Extract embedded images from PDF page"""
        images = []
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            try:
                # Get image data
                xref = img[0]
                pix = fitz.Pixmap(pdf_document, xref)
                
                # Convert to RGB if necessary
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_data = pix.tobytes("png")
                else:  # CMYK: convert to RGB
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    img_data = pix1.tobytes("png")
                    pix1 = None
                
                # Create unique image ID
                image_hash = hashlib.md5(img_data).hexdigest()
                image_id = f"{filename}_page{page_num+1}_img{img_index+1}_{image_hash[:8]}"
                
                # Save image to temp directory
                image_path = self.temp_dir / f"{image_id}.png"
                with open(image_path, 'wb') as f:
                    f.write(img_data)
                
                self.temp_files.add(str(image_path))
                
                # Get image dimensions
                with Image.open(image_path) as img_pil:
                    width, height = img_pil.size
                
                image_info = {
                    'id': image_id,
                    'type': 'embedded_image',
                    'page_number': page_num + 1,
                    'image_index': img_index + 1,
                    'path': str(image_path),
                    'format': 'png',
                    'size': len(img_data),
                    'width': width,
                    'height': height,
                    'hash': image_hash,
                    'extraction_method': 'PyMuPDF_Embedded'
                }
                
                images.append(image_info)
                logger.debug(f"Extracted embedded image {image_id} from page {page_num + 1}")
                
                pix = None  # Free memory
                
            except Exception as e:
                logger.error(f"Error extracting embedded image {img_index} from page {page_num + 1}: {e}")
                continue
        
        return images
    
    def _extract_drawing_elements(self, page: fitz.Page, page_num: int, filename: str) -> List[Dict[str, Any]]:
        """Extract visual elements from drawings"""
        elements = []
        drawings_list = page.get_drawings()
        
        if not drawings_list:
            return elements
        
        # Group drawings by proximity to identify individual visual elements
        visual_elements = self._group_drawings_by_proximity(drawings_list)
        
        for elem_index, element_drawings in enumerate(visual_elements):
            try:
                # Get bounding box for this visual element
                bbox = self._get_drawings_bbox(element_drawings)
                
                # Skip if bounding box is too small (likely text or noise)
                if bbox.width < 20 or bbox.height < 20:
                    continue
                
                # Extract just this visual element region
                mat = fitz.Matrix(2, 2)  # 2x zoom for quality
                pix = page.get_pixmap(matrix=mat, clip=bbox)
                
                # Save the visual element
                elem_id = f"{filename}_page{page_num+1}_visual_elem{elem_index+1}"
                elem_path = self.temp_dir / f"{elem_id}.png"
                
                pix.save(str(elem_path))
                self.temp_files.add(str(elem_path))
                
                # Get dimensions
                with Image.open(elem_path) as img_pil:
                    width, height = img_pil.size
                
                # Read the saved image data
                with open(elem_path, 'rb') as f:
                    img_data = f.read()
                
                # Skip if image is too small (likely noise)
                if len(img_data) < 100:
                    continue
                
                image_hash = hashlib.md5(img_data).hexdigest()
                
                visual_element_info = {
                    'id': elem_id,
                    'type': 'visual_element',
                    'page_number': page_num + 1,
                    'image_index': elem_index + 1,
                    'path': str(elem_path),
                    'format': 'png',
                    'size': len(img_data),
                    'width': width,
                    'height': height,
                    'hash': image_hash,
                    'extraction_method': 'PyMuPDF_VisualElements',
                    'bbox': [bbox.x0, bbox.y0, bbox.x1, bbox.y1],
                    'drawing_count': len(element_drawings)
                }
                
                elements.append(visual_element_info)
                logger.debug(f"Extracted visual element {elem_id} from page {page_num + 1}")
                
                pix = None  # Free memory
                
            except Exception as e:
                logger.error(f"Error extracting visual element {elem_index} from page {page_num + 1}: {e}")
                continue
        
        return elements
    
    def _group_drawings_by_proximity(self, drawings, proximity_threshold=50):
        """Group drawings that are close to each other"""
        if not drawings:
            return []
        
        groups = []
        used = set()
        
        for i, drawing in enumerate(drawings):
            if i in used:
                continue
                
            group = [drawing]
            used.add(i)
            
            # Find drawings close to this one
            bbox1 = drawing.get('rect', [0, 0, 0, 0])
            
            for j, other_drawing in enumerate(drawings):
                if j in used:
                    continue
                    
                bbox2 = other_drawing.get('rect', [0, 0, 0, 0])
                
                # Check if drawings are close
                if self._are_bboxes_close(bbox1, bbox2, proximity_threshold):
                    group.append(other_drawing)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_bboxes_close(self, bbox1, bbox2, threshold):
        """Check if two bounding boxes are close to each other"""
        if not bbox1 or not bbox2:
            return False
        
        # Calculate center points
        center1 = ((bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2)
        center2 = ((bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2)
        
        # Calculate distance
        distance = ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5
        
        return distance < threshold
    
    def _get_drawings_bbox(self, drawings):
        """Get bounding box that encompasses all drawings in a group"""
        if not drawings:
            return fitz.Rect(0, 0, 0, 0)
        
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')
        
        for drawing in drawings:
            rect = drawing.get('rect', [0, 0, 0, 0])
            if rect:
                min_x = min(min_x, rect[0])
                min_y = min(min_y, rect[1])
                max_x = max(max_x, rect[2])
                max_y = max(max_y, rect[3])
        
        return fitz.Rect(min_x, min_y, max_x, max_y)
    
    def _extract_metadata(self, pdf_document: fitz.Document, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from PDF"""
        metadata = {
            'filename': file_path.name,
            'file_type': '.pdf',
            'page_count': len(pdf_document),
            'extractor': 'PyMuPDF'
        }
        
        try:
            # Extract PDF metadata
            pdf_metadata = pdf_document.metadata
            if pdf_metadata:
                metadata.update({
                    'title': pdf_metadata.get('title', ''),
                    'author': pdf_metadata.get('author', ''),
                    'subject': pdf_metadata.get('subject', ''),
                    'creator': pdf_metadata.get('creator', ''),
                    'producer': pdf_metadata.get('producer', ''),
                    'creation_date': pdf_metadata.get('creationDate', ''),
                    'modification_date': pdf_metadata.get('modDate', '')
                })
        except Exception as e:
            logger.warning(f"Could not extract PDF metadata: {e}")
        
        return metadata
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        import os
        
        cleaned_count = 0
        failed_count = 0
        
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    cleaned_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to clean up temp file {file_path}: {e}")
        
        self.temp_files.clear()
        logger.info(f"PDF extractor cleanup: {cleaned_count} files cleaned, {failed_count} failed")
        return cleaned_count, failed_count 