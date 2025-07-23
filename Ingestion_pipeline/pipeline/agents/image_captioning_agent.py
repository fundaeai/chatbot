#!/usr/bin/env python3
"""
Image Captioning Agent using GPT-4.1 Vision
Analyzes visual elements and provides context-aware summaries
"""

import logging
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
from openai import AzureOpenAI
from ..utils.config import Config

logger = logging.getLogger(__name__)

class ImageCaptioningAgent:
    """GPT-4.1 Vision agent for image analysis and captioning"""
    
    def __init__(self):
        """Initialize the image captioning agent"""
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        self.model = Config.GPT41_MODEL
        self.deployment = Config.GPT41_DEPLOYMENT_NAME
        
        # Analysis prompts for different contexts
        self.analysis_prompts = {
            'default': """Briefly describe this image and its key content. Include:
1. Type of image (chart, graph, diagram, photo, etc.)
2. Main visual elements
3. Key information or data shown
4. Brief context or purpose""",
            
            'scientific': """Provide a concise description of this scientific figure:
1. Type of visualization
2. Key data or metrics shown
3. Main trends or patterns
4. Brief scientific context""",
            
            'document': """Briefly describe this document image:
1. Type of visual content
2. Key information it contains
3. How it relates to the document
4. Any important labels or text""",
            
            'technical': """Provide a brief description of this technical diagram:
1. Type of diagram or schematic
2. Main components or elements
3. Key technical information
4. Brief purpose or function"""
        }
    
    def analyze_image(self, image_path: str, context_text: str = "", 
                     image_id: str = "", analysis_type: str = "default") -> Dict[str, Any]:
        """
        Analyze image using GPT-4.1 Vision
        
        Args:
            image_path: Path to the image file
            context_text: Surrounding text context
            image_id: Unique identifier for the image
            analysis_type: Type of analysis ('default', 'scientific', 'document', 'technical')
            
        Returns:
            Dictionary with analysis results
        """
        try:
            logger.info(f"Analyzing image {image_id} with GPT-4.1 Vision")
            
            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare analysis prompt
            base_prompt = self.analysis_prompts.get(analysis_type, self.analysis_prompts['default'])
            
            if context_text:
                enhanced_prompt = f"""
{base_prompt}

Context from surrounding text:
{context_text[:1000]}...

Please analyze the image in relation to this context and provide insights about how the image complements or illustrates the text content.
"""
            else:
                enhanced_prompt = base_prompt
            
            # Create messages for GPT-4.1
            messages = [
                {
                    "role": "system",
                    "content": "You are an AI assistant that provides concise, accurate descriptions of images in documents. Focus on preserving essential information without excessive detail."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": enhanced_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            # Call GPT-4.1
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_tokens=300,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            
            return {
                'success': True,
                'analysis': analysis,
                'image_id': image_id,
                'context_used': bool(context_text),
                'analysis_type': analysis_type,
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else None,
                'model_used': self.model,
                'image_path': image_path
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'image_id': image_id,
                'image_path': image_path
            }
    
    def analyze_multiple_images(self, images: List[Dict[str, Any]], 
                              context_text: str = "", analysis_type: str = "default") -> List[Dict[str, Any]]:
        """
        Analyze multiple images with shared context
        
        Args:
            images: List of image dictionaries with 'path' and 'id' keys
            context_text: Shared context text for all images
            analysis_type: Type of analysis to perform
            
        Returns:
            List of analysis results
        """
        results = []
        
        for image_info in images:
            image_path = image_info.get('path')
            image_id = image_info.get('id', '')
            
            if not image_path or not Path(image_path).exists():
                logger.warning(f"Image path not found: {image_path}")
                continue
            
            result = self.analyze_image(
                image_path=image_path,
                context_text=context_text,
                image_id=image_id,
                analysis_type=analysis_type
            )
            
            results.append(result)
        
        logger.info(f"Analyzed {len(results)} images with GPT-4.1 Vision")
        return results
    
    def get_image_context(self, text_content: str, page_number: int, 
                         context_window: int = 500) -> str:
        """
        Extract relevant context for an image from surrounding text
        
        Args:
            text_content: Full text content
            page_number: Page number where image appears
            context_window: Number of characters around the image reference
            
        Returns:
            Extracted context text
        """
        try:
            # Split text into pages
            pages = text_content.split("--- Page")
            
            if page_number <= len(pages):
                page_text = pages[page_number - 1] if page_number > 0 else pages[0]
                
                # Extract context window around the page
                start = max(0, len(page_text) // 2 - context_window // 2)
                end = min(len(page_text), start + context_window)
                
                return page_text[start:end].strip()
            else:
                return text_content[:context_window]
                
        except Exception as e:
            logger.warning(f"Error extracting image context: {e}")
            return text_content[:context_window]
    
    def enhance_content_with_image_analysis(self, text_content: str, 
                                          image_analyses: List[Dict[str, Any]]) -> str:
        """
        Enhance text content with image analysis results
        
        Args:
            text_content: Original text content
            image_analyses: List of image analysis results
            
        Returns:
            Enhanced text content with image summaries
        """
        enhanced_content = text_content
        
        for analysis in image_analyses:
            if analysis.get('success') and analysis.get('analysis'):
                image_id = analysis.get('image_id', '')
                image_analysis = analysis.get('analysis', '')
                
                # Add image analysis to content
                image_summary = f"\n\n[Image Analysis - {image_id}]\n{image_analysis}\n"
                enhanced_content += image_summary
        
        return enhanced_content
    
    def get_analysis_summary(self, image_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for image analyses
        
        Args:
            image_analyses: List of image analysis results
            
        Returns:
            Summary statistics
        """
        successful_analyses = [a for a in image_analyses if a.get('success')]
        failed_analyses = [a for a in image_analyses if not a.get('success')]
        
        total_tokens = sum(a.get('tokens_used', 0) for a in successful_analyses)
        avg_analysis_length = sum(len(a.get('analysis', '')) for a in successful_analyses) / max(len(successful_analyses), 1)
        
        return {
            'total_images': len(image_analyses),
            'successful_analyses': len(successful_analyses),
            'failed_analyses': len(failed_analyses),
            'success_rate': len(successful_analyses) / max(len(image_analyses), 1) * 100,
            'total_tokens_used': total_tokens,
            'average_analysis_length': avg_analysis_length,
            'model_used': self.model
        } 