#!/usr/bin/env python3
"""
Centralized Prompts for Ingestion Pipeline
All AI prompts in one place for easy experimentation and tuning
"""

class IngestionPrompts:
    """Centralized prompts for document ingestion and processing"""
    
    # ============================================================================
    # IMAGE ANALYSIS PROMPTS
    # ============================================================================
    
    IMAGE_ANALYSIS_SYSTEM_PROMPT = """You are an AI research assistant specialized in analyzing images within the context of research documents. Your task is to:

1. Analyze images in detail, identifying all visual elements, charts, graphs, diagrams, and text
2. Understand the relationship between the image and surrounding document content
3. Provide comprehensive summaries that preserve semantic meaning and context
4. Extract key insights and data points from visual elements
5. Explain how the image supports or illustrates the document's content

Always maintain the academic and research context when analyzing images. Be concise but thorough."""

    IMAGE_ANALYSIS_USER_PROMPT = """Analyze this image in the context of the research document. Provide a comprehensive summary that includes:

1. Detailed description of all visual elements
2. Key data points and insights
3. How this image relates to the surrounding text
4. Semantic meaning and context preservation
5. Any additional information the image provides beyond the text

Image Context: {context_text}

Please provide a clear, structured analysis."""

    # ============================================================================
    # SPECIALIZED IMAGE ANALYSIS PROMPTS
    # ============================================================================
    
    SCIENTIFIC_FIGURE_PROMPT = """Provide a concise description of this scientific figure:

1. Type of visualization (chart, graph, diagram, etc.)
2. Key data or metrics shown
3. Main trends or patterns
4. Brief scientific context
5. How it relates to the research

Focus on accuracy and scientific relevance."""

    TECHNICAL_DIAGRAM_PROMPT = """Provide a brief description of this technical diagram:

1. Type of diagram or schematic
2. Main components or elements
3. Key technical information
4. Brief purpose or function
5. Technical relationships shown

Be precise and technical in your description."""

    DOCUMENT_IMAGE_PROMPT = """Briefly describe this document image:

1. Type of visual content
2. Key information it contains
3. How it relates to the document
4. Any important labels or text
5. Document context relevance

Focus on document-specific information."""

    # ============================================================================
    # CONTENT ENHANCEMENT PROMPTS
    # ============================================================================
    
    CONTENT_ENHANCEMENT_PROMPT = """Enhance the following document content by integrating image analysis:

Original Text: {original_text}

Image Analysis: {image_analysis}

Please:
1. Integrate the image insights naturally into the text
2. Maintain the original meaning and flow
3. Add relevant context from the image analysis
4. Ensure the enhanced content is coherent and readable

Provide the enhanced content that combines text and image information."""

    # ============================================================================
    # METADATA EXTRACTION PROMPTS
    # ============================================================================
    
    METADATA_EXTRACTION_PROMPT = """Extract key metadata from this document content:

Content: {content}

Please identify:
1. Document type and format
2. Key topics and themes
3. Important entities (people, organizations, concepts)
4. Document structure and organization
5. Technical complexity level

Return the metadata in a structured format."""

    # ============================================================================
    # QUALITY ASSESSMENT PROMPTS
    # ============================================================================
    
    QUALITY_ASSESSMENT_PROMPT = """Assess the quality of this processed document chunk:

Chunk Content: {chunk_content}

Please evaluate:
1. Completeness of information
2. Clarity and readability
3. Relevance to document context
4. Technical accuracy
5. Semantic coherence

Provide a quality score (0-1) and brief assessment."""

    # ============================================================================
    # ERROR RECOVERY PROMPTS
    # ============================================================================
    
    ERROR_RECOVERY_PROMPT = """The following content extraction encountered an error:

Error: {error_message}
Original Content: {original_content}

Please attempt to:
1. Identify the nature of the error
2. Suggest recovery strategies
3. Provide alternative processing approaches
4. Estimate content quality impact

Help improve the extraction process."""

    # ============================================================================
    # CONTENT SUMMARIZATION PROMPTS
    # ============================================================================
    
    CONTENT_SUMMARY_PROMPT = """Summarize the key points from this document content:

Content: {content}

Please provide:
1. Main topics and themes
2. Key findings or conclusions
3. Important data points
4. Technical concepts
5. Document structure overview

Keep the summary concise but comprehensive."""

    # ============================================================================
    # CONTEXT BUILDING PROMPTS
    # ============================================================================
    
    CONTEXT_BUILDING_PROMPT = """Build context for the following document chunks:

Chunks: {chunks}

Please:
1. Identify relationships between chunks
2. Create a coherent narrative flow
3. Highlight key connections
4. Maintain document structure
5. Preserve semantic meaning

Provide enhanced context that connects the chunks meaningfully."""

    # ============================================================================
    # VALIDATION PROMPTS
    # ============================================================================
    
    CONTENT_VALIDATION_PROMPT = """Validate the quality and completeness of this processed content:

Content: {content}
Original Source: {source_info}

Please check for:
1. Information completeness
2. Accuracy and consistency
3. Proper formatting
4. Missing elements
5. Processing artifacts

Provide validation results and recommendations."""

    # ============================================================================
    # EXPERIMENTAL PROMPTS
    # ============================================================================
    
    ADVANCED_ANALYSIS_PROMPT = """Perform advanced analysis of this document content:

Content: {content}

Please provide:
1. Deep semantic analysis
2. Cross-reference identification
3. Knowledge graph extraction
4. Conceptual relationships
5. Advanced insights

Use sophisticated analysis techniques."""

    @classmethod
    def get_image_prompts(cls):
        """Get all image analysis prompts"""
        return {
            'system': cls.IMAGE_ANALYSIS_SYSTEM_PROMPT,
            'user': cls.IMAGE_ANALYSIS_USER_PROMPT,
            'scientific': cls.SCIENTIFIC_FIGURE_PROMPT,
            'technical': cls.TECHNICAL_DIAGRAM_PROMPT,
            'document': cls.DOCUMENT_IMAGE_PROMPT
        }
    
    @classmethod
    def get_processing_prompts(cls):
        """Get all processing prompts"""
        return {
            'enhancement': cls.CONTENT_ENHANCEMENT_PROMPT,
            'metadata': cls.METADATA_EXTRACTION_PROMPT,
            'quality': cls.QUALITY_ASSESSMENT_PROMPT,
            'summary': cls.CONTENT_SUMMARY_PROMPT,
            'context': cls.CONTEXT_BUILDING_PROMPT,
            'validation': cls.CONTENT_VALIDATION_PROMPT
        }
    
    @classmethod
    def get_all_prompts(cls):
        """Get all prompts as a dictionary"""
        return {
            'image_analysis': cls.get_image_prompts(),
            'processing': cls.get_processing_prompts(),
            'error_recovery': cls.ERROR_RECOVERY_PROMPT,
            'experimental': cls.ADVANCED_ANALYSIS_PROMPT
        } 