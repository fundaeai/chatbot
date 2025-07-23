#!/usr/bin/env python3
"""
Centralized Hyperparameters for Ingestion Pipeline
All configurable parameters in one place for easy experimentation
"""

class IngestionHyperparameters:
    """Centralized hyperparameters for document ingestion"""
    
    # ============================================================================
    # CHUNKING PARAMETERS
    # ============================================================================
    CHUNK_SIZE = 1000                    # Target size for each text chunk
    CHUNK_OVERLAP = 200                  # Overlap between chunks
    CHUNK_SEPARATORS = [                 # Text splitting separators (priority order)
        "\n\n",                          # Paragraph breaks
        "\n",                            # Line breaks
        ". ",                            # Sentences
        "! ",                            # Exclamations
        "? ",                            # Questions
        "; ",                            # Semicolons
        ", ",                            # Commas
        " ",                             # Words
        ""                               # Characters
    ]
    
    # ============================================================================
    # EMBEDDING PARAMETERS
    # ============================================================================
    EMBEDDING_BATCH_SIZE = 16            # Batch size for embedding generation
    EMBEDDING_MAX_RETRIES = 3            # Maximum retry attempts for embeddings
    EMBEDDING_RETRY_DELAY = 1.0          # Delay between retries (seconds)
    EMBEDDING_DIMENSION = 1536           # Vector dimension for embeddings
    
    # ============================================================================
    # IMAGE PROCESSING PARAMETERS
    # ============================================================================
    MAX_IMAGE_SIZE = 20971520            # Maximum image size (20MB)
    IMAGE_QUALITY = 85                   # JPEG quality for image compression
    MIN_IMAGE_SIZE = 1024                # Minimum image size to process
    IMAGE_FORMATS = [                    # Supported image formats
        '.jpg', '.jpeg', '.png', '.gif', 
        '.bmp', '.tiff', '.webp'
    ]
    
    # ============================================================================
    # PDF PROCESSING PARAMETERS
    # ============================================================================
    PDF_DPI = 300                        # DPI for PDF rendering
    PDF_IMAGE_THRESHOLD = 0.1            # Minimum image size ratio in PDF
    PDF_DRAWING_PROXIMITY = 50           # Proximity threshold for grouping drawings
    PDF_MIN_DRAWING_SIZE = 100           # Minimum drawing size to extract
    
    # ============================================================================
    # PROCESSING PARAMETERS
    # ============================================================================
    MAX_FILE_SIZE = 100 * 1024 * 1024   # Maximum file size (100MB)
    TEMP_FILE_CLEANUP = True             # Auto-cleanup temporary files
    SAVE_INTERMEDIATE_OUTPUTS = False    # Save intermediate processing outputs
    PROCESSING_TIMEOUT = 300             # Processing timeout (seconds)
    
    # ============================================================================
    # STORAGE PARAMETERS
    # ============================================================================
    BLOB_METADATA_FIELDS = [             # Metadata fields to store
        'filename', 'file_size', 'upload_date', 
        'chunk_count', 'embedding_count'
    ]
    SEARCH_INDEX_FIELDS = [              # Fields in search index
        'id', 'content', 'filename', 'chunk_index', 
        'page_number', 'chunk_type', 'tags', 'upload_date'
    ]
    
    # ============================================================================
    # PERFORMANCE PARAMETERS
    # ============================================================================
    MAX_CONCURRENT_UPLOADS = 5           # Maximum concurrent file uploads
    MEMORY_LIMIT = 2 * 1024 * 1024 * 1024  # Memory limit (2GB)
    CPU_THREADS = 4                      # Number of CPU threads to use
    
    # ============================================================================
    # VALIDATION PARAMETERS
    # ============================================================================
    MIN_CHUNK_SIZE = 50                  # Minimum chunk size
    MAX_CHUNK_SIZE = 2000                # Maximum chunk size
    MIN_TEXT_LENGTH = 10                 # Minimum text length to process
    MAX_TEXT_LENGTH = 1000000            # Maximum text length to process
    
    # ============================================================================
    # EXPERIMENTATION PARAMETERS
    # ============================================================================
    ENABLE_EXPERIMENTAL_FEATURES = False # Enable experimental features
    LOG_LEVEL = "INFO"                   # Logging level
    DEBUG_MODE = False                   # Debug mode for detailed logging
    
    @classmethod
    def get_chunking_config(cls):
        """Get chunking configuration"""
        return {
            'chunk_size': cls.CHUNK_SIZE,
            'chunk_overlap': cls.CHUNK_OVERLAP,
            'separators': cls.CHUNK_SEPARATORS
        }
    
    @classmethod
    def get_embedding_config(cls):
        """Get embedding configuration"""
        return {
            'batch_size': cls.EMBEDDING_BATCH_SIZE,
            'max_retries': cls.EMBEDDING_MAX_RETRIES,
            'retry_delay': cls.EMBEDDING_RETRY_DELAY,
            'dimension': cls.EMBEDDING_DIMENSION
        }
    
    @classmethod
    def get_image_config(cls):
        """Get image processing configuration"""
        return {
            'max_size': cls.MAX_IMAGE_SIZE,
            'quality': cls.IMAGE_QUALITY,
            'min_size': cls.MIN_IMAGE_SIZE,
            'formats': cls.IMAGE_FORMATS
        }
    
    @classmethod
    def get_pdf_config(cls):
        """Get PDF processing configuration"""
        return {
            'dpi': cls.PDF_DPI,
            'image_threshold': cls.PDF_IMAGE_THRESHOLD,
            'drawing_proximity': cls.PDF_DRAWING_PROXIMITY,
            'min_drawing_size': cls.PDF_MIN_DRAWING_SIZE
        }
    
    @classmethod
    def get_performance_config(cls):
        """Get performance configuration"""
        return {
            'max_concurrent': cls.MAX_CONCURRENT_UPLOADS,
            'memory_limit': cls.MEMORY_LIMIT,
            'cpu_threads': cls.CPU_THREADS,
            'timeout': cls.PROCESSING_TIMEOUT
        }
    
    @classmethod
    def get_all_config(cls):
        """Get all hyperparameters as a dictionary"""
        return {
            'chunking': cls.get_chunking_config(),
            'embedding': cls.get_embedding_config(),
            'image': cls.get_image_config(),
            'pdf': cls.get_pdf_config(),
            'performance': cls.get_performance_config(),
            'validation': {
                'min_chunk_size': cls.MIN_CHUNK_SIZE,
                'max_chunk_size': cls.MAX_CHUNK_SIZE,
                'min_text_length': cls.MIN_TEXT_LENGTH,
                'max_text_length': cls.MAX_TEXT_LENGTH
            },
            'processing': {
                'temp_cleanup': cls.TEMP_FILE_CLEANUP,
                'save_outputs': cls.SAVE_INTERMEDIATE_OUTPUTS,
                'max_file_size': cls.MAX_FILE_SIZE
            }
        } 