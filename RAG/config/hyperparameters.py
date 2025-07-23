#!/usr/bin/env python3
"""
Centralized Hyperparameters for RAG System
All configurable parameters in one place for easy experimentation
"""

class RAGHyperparameters:
    """Centralized hyperparameters for RAG retrieval and generation"""
    
    # ============================================================================
    # RETRIEVAL PARAMETERS
    # ============================================================================
    DEFAULT_TOP_K = 5                    # Default number of documents to retrieve
    MAX_TOP_K = 20                       # Maximum number of documents to retrieve
    MIN_SIMILARITY_SCORE = 0.7           # Minimum similarity score threshold
    SEARCH_TIMEOUT = 30                  # Search timeout in seconds
    EMBEDDING_BATCH_SIZE = 1             # Batch size for query embeddings
    
    # ============================================================================
    # AUGMENTATION PARAMETERS
    # ============================================================================
    DEFAULT_CONTEXT_LENGTH = 4000        # Default context length in characters
    MAX_CONTEXT_LENGTH = 8000            # Maximum context length
    MIN_CONTEXT_LENGTH = 500             # Minimum context length
    CONTEXT_SEPARATOR = "\n\n"           # Separator between context chunks
    SOURCE_FORMAT = "[Source: {filename}, Page: {page}, Score: {score:.3f}]"
    
    # ============================================================================
    # GENERATION PARAMETERS
    # ============================================================================
    DEFAULT_TEMPERATURE = 0.7            # Default temperature for generation
    DEFAULT_MAX_TOKENS = 500             # Default max tokens for response
    MAX_MAX_TOKENS = 1000                # Maximum tokens allowed
    MIN_MAX_TOKENS = 100                 # Minimum tokens allowed
    TOP_P = 0.9                          # Top-p sampling parameter
    FREQUENCY_PENALTY = 0.0              # Frequency penalty
    PRESENCE_PENALTY = 0.0               # Presence penalty
    
    # ============================================================================
    # CONFIDENCE CALCULATION PARAMETERS
    # ============================================================================
    BASE_CONFIDENCE = 0.8                # Base confidence score
    MIN_ANSWER_LENGTH = 20               # Minimum answer length for good confidence
    MAX_ANSWER_LENGTH = 1000             # Maximum answer length before penalty
    UNCERTAINTY_PENALTY = 0.3            # Penalty for uncertainty indicators
    SHORT_ANSWER_PENALTY = 0.2           # Penalty for very short answers
    LONG_ANSWER_PENALTY = 0.1            # Penalty for very long answers
    CONTEXT_REFERENCE_BONUS = 0.1        # Bonus for referencing context
    
    # ============================================================================
    # SEARCH TYPE PARAMETERS
    # ============================================================================
    DEFAULT_SEARCH_TYPE = "hybrid"       # Default search type
    SEMANTIC_WEIGHT = 0.7                # Weight for semantic search in hybrid
    KEYWORD_WEIGHT = 0.3                 # Weight for keyword search in hybrid
    
    # ============================================================================
    # PERFORMANCE PARAMETERS
    # ============================================================================
    MAX_PROCESSING_TIME = 60             # Maximum processing time in seconds
    CACHE_ENABLED = True                 # Enable response caching
    CACHE_TTL = 3600                     # Cache TTL in seconds
    MAX_CONCURRENT_REQUESTS = 10         # Maximum concurrent requests
    
    # ============================================================================
    # VALIDATION PARAMETERS
    # ============================================================================
    MIN_QUESTION_LENGTH = 5              # Minimum question length
    MAX_QUESTION_LENGTH = 1000           # Maximum question length
    MIN_CONTEXT_CHUNKS = 1               # Minimum context chunks required
    MAX_CONTEXT_CHUNKS = 10              # Maximum context chunks allowed
    
    # ============================================================================
    # ERROR HANDLING PARAMETERS
    # ============================================================================
    MAX_RETRIES = 3                      # Maximum retry attempts
    RETRY_DELAY = 1.0                    # Delay between retries in seconds
    BACKOFF_MULTIPLIER = 2.0             # Exponential backoff multiplier
    
    # ============================================================================
    # EXPERIMENTATION PARAMETERS
    # ============================================================================
    ENABLE_DEBUG_LOGGING = False         # Enable detailed debug logging
    LOG_RETRIEVAL_STEPS = True           # Log retrieval process steps
    LOG_AUGMENTATION_STEPS = True        # Log augmentation process steps
    LOG_GENERATION_STEPS = True          # Log generation process steps
    SAVE_INTERMEDIATE_RESULTS = False    # Save intermediate processing results
    
    # ============================================================================
    # ADVANCED PARAMETERS
    # ============================================================================
    ENABLE_RERANKING = False             # Enable result reranking
    RERANKING_MODEL = "cross-encoder"    # Reranking model type
    ENABLE_QUERY_EXPANSION = False       # Enable query expansion
    QUERY_EXPANSION_TERMS = 3            # Number of expansion terms
    ENABLE_CONTEXT_OPTIMIZATION = True   # Enable context optimization
    
    @classmethod
    def get_retrieval_config(cls):
        """Get retrieval configuration"""
        return {
            'default_top_k': cls.DEFAULT_TOP_K,
            'max_top_k': cls.MAX_TOP_K,
            'min_similarity_score': cls.MIN_SIMILARITY_SCORE,
            'search_timeout': cls.SEARCH_TIMEOUT,
            'embedding_batch_size': cls.EMBEDDING_BATCH_SIZE
        }
    
    @classmethod
    def get_augmentation_config(cls):
        """Get augmentation configuration"""
        return {
            'default_context_length': cls.DEFAULT_CONTEXT_LENGTH,
            'max_context_length': cls.MAX_CONTEXT_LENGTH,
            'min_context_length': cls.MIN_CONTEXT_LENGTH,
            'context_separator': cls.CONTEXT_SEPARATOR,
            'source_format': cls.SOURCE_FORMAT
        }
    
    @classmethod
    def get_generation_config(cls):
        """Get generation configuration"""
        return {
            'default_temperature': cls.DEFAULT_TEMPERATURE,
            'default_max_tokens': cls.DEFAULT_MAX_TOKENS,
            'max_max_tokens': cls.MAX_MAX_TOKENS,
            'min_max_tokens': cls.MIN_MAX_TOKENS,
            'top_p': cls.TOP_P,
            'frequency_penalty': cls.FREQUENCY_PENALTY,
            'presence_penalty': cls.PRESENCE_PENALTY
        }
    
    @classmethod
    def get_confidence_config(cls):
        """Get confidence calculation configuration"""
        return {
            'base_confidence': cls.BASE_CONFIDENCE,
            'min_answer_length': cls.MIN_ANSWER_LENGTH,
            'max_answer_length': cls.MAX_ANSWER_LENGTH,
            'uncertainty_penalty': cls.UNCERTAINTY_PENALTY,
            'short_answer_penalty': cls.SHORT_ANSWER_PENALTY,
            'long_answer_penalty': cls.LONG_ANSWER_PENALTY,
            'context_reference_bonus': cls.CONTEXT_REFERENCE_BONUS
        }
    
    @classmethod
    def get_search_config(cls):
        """Get search configuration"""
        return {
            'default_search_type': cls.DEFAULT_SEARCH_TYPE,
            'semantic_weight': cls.SEMANTIC_WEIGHT,
            'keyword_weight': cls.KEYWORD_WEIGHT
        }
    
    @classmethod
    def get_performance_config(cls):
        """Get performance configuration"""
        return {
            'max_processing_time': cls.MAX_PROCESSING_TIME,
            'cache_enabled': cls.CACHE_ENABLED,
            'cache_ttl': cls.CACHE_TTL,
            'max_concurrent_requests': cls.MAX_CONCURRENT_REQUESTS
        }
    
    @classmethod
    def get_validation_config(cls):
        """Get validation configuration"""
        return {
            'min_question_length': cls.MIN_QUESTION_LENGTH,
            'max_question_length': cls.MAX_QUESTION_LENGTH,
            'min_context_chunks': cls.MIN_CONTEXT_CHUNKS,
            'max_context_chunks': cls.MAX_CONTEXT_CHUNKS
        }
    
    @classmethod
    def get_error_handling_config(cls):
        """Get error handling configuration"""
        return {
            'max_retries': cls.MAX_RETRIES,
            'retry_delay': cls.RETRY_DELAY,
            'backoff_multiplier': cls.BACKOFF_MULTIPLIER
        }
    
    @classmethod
    def get_experimental_config(cls):
        """Get experimental features configuration"""
        return {
            'enable_debug_logging': cls.ENABLE_DEBUG_LOGGING,
            'log_retrieval_steps': cls.LOG_RETRIEVAL_STEPS,
            'log_augmentation_steps': cls.LOG_AUGMENTATION_STEPS,
            'log_generation_steps': cls.LOG_GENERATION_STEPS,
            'save_intermediate_results': cls.SAVE_INTERMEDIATE_RESULTS
        }
    
    @classmethod
    def get_advanced_config(cls):
        """Get advanced features configuration"""
        return {
            'enable_reranking': cls.ENABLE_RERANKING,
            'reranking_model': cls.RERANKING_MODEL,
            'enable_query_expansion': cls.ENABLE_QUERY_EXPANSION,
            'query_expansion_terms': cls.QUERY_EXPANSION_TERMS,
            'enable_context_optimization': cls.ENABLE_CONTEXT_OPTIMIZATION
        }
    
    @classmethod
    def get_all_config(cls):
        """Get all hyperparameters as a dictionary"""
        return {
            'retrieval': cls.get_retrieval_config(),
            'augmentation': cls.get_augmentation_config(),
            'generation': cls.get_generation_config(),
            'confidence': cls.get_confidence_config(),
            'search': cls.get_search_config(),
            'performance': cls.get_performance_config(),
            'validation': cls.get_validation_config(),
            'error_handling': cls.get_error_handling_config(),
            'experimental': cls.get_experimental_config(),
            'advanced': cls.get_advanced_config()
        } 