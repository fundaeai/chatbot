#!/usr/bin/env python3
"""
Configuration management for the multimodal ingestion pipeline
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the multimodal ingestion pipeline"""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    
    # Model Configuration
    GPT41_MODEL = os.getenv('GPT41_MODEL', 'gpt-4-vision-preview')
    GPT41_DEPLOYMENT_NAME = os.getenv('GPT41_DEPLOYMENT_NAME', 'gpt-4-vision-preview')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')
    EMBEDDING_DEPLOYMENT_NAME = os.getenv('EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-ada-002')
    
    # Azure AI Search Configuration
    AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
    AZURE_SEARCH_KEY = os.getenv('AZURE_SEARCH_KEY')
    AZURE_SEARCH_INDEX_NAME = os.getenv('AZURE_SEARCH_INDEX_NAME', 'documents-index')
    
    # Azure Blob Storage Configuration
    AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'documents')
    
    # Processing Configuration
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))
    MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', '20971520'))  # 20MB
    TEMP_IMAGE_DIR = os.getenv('TEMP_IMAGE_DIR', 'temp_images')
    
    # Supported file formats
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    
    # AI Agent Configuration
    AGENT_SYSTEM_PROMPT = os.getenv('AGENT_SYSTEM_PROMPT', 
        "You are an AI research assistant specialized in analyzing images within the context of research documents. "
        "Your task is to: 1) Analyze images in detail, identifying all visual elements, charts, graphs, diagrams, and text, "
        "2) Understand the relationship between the image and surrounding document content, "
        "3) Provide comprehensive summaries that preserve semantic meaning and context, "
        "4) Extract key insights and data points from visual elements, "
        "5) Explain how the image supports or illustrates the document's content. "
        "Always maintain the academic and research context when analyzing images.")
    
    IMAGE_ANALYSIS_PROMPT = os.getenv('IMAGE_ANALYSIS_PROMPT',
        "Analyze this image in the context of the research document. Provide a comprehensive summary that includes: "
        "1) Detailed description of all visual elements, "
        "2) Key data points and insights, "
        "3) How this image relates to the surrounding text, "
        "4) Semantic meaning and context preservation, "
        "5) Any additional information the image provides beyond the text.")
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_vars = [
            'AZURE_OPENAI_API_KEY',
            'AZURE_OPENAI_ENDPOINT',
            'GPT41_DEPLOYMENT_NAME',
            'EMBEDDING_DEPLOYMENT_NAME'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def get_config_summary(cls):
        """Get a summary of the current configuration"""
        return {
            'azure_openai_configured': bool(cls.AZURE_OPENAI_API_KEY and cls.AZURE_OPENAI_ENDPOINT),
            'gpt41_model': cls.GPT41_MODEL,
            'gpt41_deployment': cls.GPT41_DEPLOYMENT_NAME,
            'embedding_model': cls.EMBEDDING_MODEL,
            'embedding_deployment': cls.EMBEDDING_DEPLOYMENT_NAME,
            'chunk_size': cls.CHUNK_SIZE,
            'chunk_overlap': cls.CHUNK_OVERLAP,
            'temp_image_dir': cls.TEMP_IMAGE_DIR,
            'azure_search_configured': bool(cls.AZURE_SEARCH_ENDPOINT and cls.AZURE_SEARCH_KEY),
            'azure_storage_configured': bool(cls.AZURE_STORAGE_CONNECTION_STRING)
        } 