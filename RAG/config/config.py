#!/usr/bin/env python3
"""
Configuration management for the RAG retrieval system
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the RAG retrieval system"""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    
    # Model Configuration
    GPT4_MODEL = os.getenv('GPT41_MODEL', 'gpt-4.1')
    GPT4_DEPLOYMENT_NAME = os.getenv('GPT41_DEPLOYMENT_NAME', 'gpt-4.1')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-large')
    EMBEDDING_DEPLOYMENT_NAME = os.getenv('EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-3-large')
    
    # Azure AI Search Configuration
    AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
    AZURE_SEARCH_KEY = os.getenv('AZURE_SEARCH_KEY')
    AZURE_SEARCH_INDEX_NAME = os.getenv('AZURE_SEARCH_INDEX_NAME', 'documents-index')
    
    # Azure Blob Storage Configuration
    AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'knowledgebase')
    
    # RAG Configuration - Now using centralized hyperparameters
    # See hyperparameters.py for all configurable parameters
    # Legacy environment variables for backward compatibility
    RAG_CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
    RAG_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))
    MAX_CONTEXT_LENGTH = int(os.getenv('MAX_CONTEXT_LENGTH', '4000'))
    TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', '5'))
    MIN_SIMILARITY_SCORE = float(os.getenv('MIN_SIMILARITY_SCORE', '0.7'))
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '8002'))
    WEB_UI_PORT = int(os.getenv('WEB_UI_PORT', '8003'))
    
    # RAG Prompts - Now using centralized prompts
    # See prompts.py for all configurable prompts
    # Legacy environment variables for backward compatibility
    RAG_SYSTEM_PROMPT = os.getenv('RAG_SYSTEM_PROMPT', 
        "You are an AI assistant that provides accurate, helpful answers based on the provided context. "
        "Always base your responses on the given context and cite specific sources when possible. "
        "If the context doesn't contain enough information to answer the question, say so clearly. "
        "Be concise but thorough in your explanations.")
    
    RAG_USER_PROMPT_TEMPLATE = os.getenv('RAG_USER_PROMPT_TEMPLATE',
        "Context:\n{context}\n\nQuestion: {question}\n\nAnswer based on the context above:")
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_vars = [
            'AZURE_OPENAI_API_KEY',
            'AZURE_OPENAI_ENDPOINT',
            'GPT4_DEPLOYMENT_NAME',
            'AZURE_SEARCH_ENDPOINT',
            'AZURE_SEARCH_KEY'
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
            'gpt4_model': cls.GPT4_MODEL,
            'gpt4_deployment': cls.GPT4_DEPLOYMENT_NAME,
            'embedding_model': cls.EMBEDDING_MODEL,
            'embedding_deployment': cls.EMBEDDING_DEPLOYMENT_NAME,
            'azure_search_configured': bool(cls.AZURE_SEARCH_ENDPOINT and cls.AZURE_SEARCH_KEY),
            'azure_storage_configured': bool(cls.AZURE_STORAGE_CONNECTION_STRING),
            'rag_chunk_size': cls.RAG_CHUNK_SIZE,
            'rag_overlap': cls.RAG_OVERLAP,
            'max_context_length': cls.MAX_CONTEXT_LENGTH,
            'top_k_results': cls.TOP_K_RESULTS,
            'api_port': cls.API_PORT,
            'web_ui_port': cls.WEB_UI_PORT
        } 