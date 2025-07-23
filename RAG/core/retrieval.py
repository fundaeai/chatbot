#!/usr/bin/env python3
"""
Step 1: Retrieval Component
Searches through document database to find relevant chunks
"""

import logging
import time
from typing import List, Dict, Any, Optional
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from openai import AzureOpenAI
from config import config
from config.hyperparameters import RAGHyperparameters

logger = logging.getLogger(__name__)

class RetrievalComponent:
    """Step 1: Retrieves relevant documents from the database"""
    
    def __init__(self):
        """Initialize the retrieval component"""
        # Initialize Azure Search client
        self.search_client = SearchClient(
            endpoint=config.Config.AZURE_SEARCH_ENDPOINT,
            index_name=config.Config.AZURE_SEARCH_INDEX_NAME,
            credential=AzureKeyCredential(config.Config.AZURE_SEARCH_KEY)
        )
        
        # Initialize OpenAI client for embeddings
        self.openai_client = AzureOpenAI(
            api_key=config.Config.AZURE_OPENAI_API_KEY,
            api_version=config.Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=config.Config.AZURE_OPENAI_ENDPOINT
        )
        
        logger.info("Retrieval component initialized")
    
    def retrieve(self, query: str, top_k: int = None, search_type: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents based on the query
        
        Args:
            query: The search query
            top_k: Number of results to retrieve
            search_type: Type of search ("semantic", "keyword", "hybrid")
            
        Returns:
            List of relevant document chunks
        """
        try:
            # Use hyperparameters for defaults
            top_k = top_k or RAGHyperparameters.DEFAULT_TOP_K
            search_type = search_type or RAGHyperparameters.DEFAULT_SEARCH_TYPE
            
            # Validate parameters
            top_k = min(top_k, RAGHyperparameters.MAX_TOP_K)
            
            start_time = time.time()
            logger.info(f"Retrieving documents for query: '{query}'")
            
            if search_type == "semantic":
                results = self._semantic_search(query, top_k)
            elif search_type == "keyword":
                results = self._keyword_search(query, top_k)
            else:  # hybrid
                results = self._hybrid_search(query, top_k)
            
            retrieval_time = time.time() - start_time
            logger.info(f"Retrieved {len(results)} documents in {retrieval_time:.3f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in retrieval: {e}")
            return []
    
    def _semantic_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Semantic search using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Perform vector search
            search_results = self.search_client.search(
                search_text=query,
                vector_queries=[{
                    "vector": query_embedding,
                    "fields": "content_vector",
                    "k": top_k,
                    "kind": "vector"
                }],
                select=["id", "content", "filename", "chunk_index", "page_number", "chunk_type", "tags", "upload_date"],
                top=top_k
            )
            
            return self._process_search_results(search_results)
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Keyword-based search"""
        try:
            search_results = self.search_client.search(
                search_text=query,
                select=["id", "content", "filename", "chunk_index", "page_number", "chunk_type", "tags", "upload_date"],
                top=top_k,
                query_type=QueryType.SIMPLE
            )
            
            return self._process_search_results(search_results)
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return []
    
    def _hybrid_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Hybrid search combining vector and keyword search"""
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Try vector search first
            try:
                search_results = self.search_client.search(
                    search_text=query,
                    vector_queries=[{
                        "vector": query_embedding,
                        "fields": "content_vector",
                        "k": top_k,
                        "kind": "vector"
                    }],
                    select=["id", "content", "filename", "chunk_index", "page_number", "chunk_type", "tags", "upload_date"],
                    top=top_k,
                    query_type=QueryType.SIMPLE
                )
                
                results = self._process_search_results(search_results)
                
                # If vector search found results, return them
                if results:
                    logger.info(f"Hybrid search (vector) found {len(results)} results")
                    return results
                    
            except Exception as vector_error:
                logger.warning(f"Vector search failed, falling back to keyword: {vector_error}")
            
            # Fall back to keyword search if vector search fails or returns no results
            logger.info("Falling back to keyword search for hybrid")
            return self._keyword_search(query, top_k)
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    def _process_search_results(self, search_results) -> List[Dict[str, Any]]:
        """Process search results into standardized format"""
        results = []
        for result in search_results:
            results.append({
                'content': result.get('content', ''),
                'filename': result.get('filename', ''),
                'chunk_index': result.get('chunk_index', 0),
                'page_number': result.get('page_number', 0),
                'chunk_type': result.get('chunk_type', 'text'),
                'tags': result.get('tags', []),
                'upload_date': result.get('upload_date', ''),
                'score': result.get('@search.score', 0.0)
            })
        return results
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Azure OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model=config.Config.EMBEDDING_DEPLOYMENT_NAME,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get retrieval component statistics"""
        try:
            total_docs = self.search_client.get_document_count()
            return {
                'total_documents': total_docs,
                'search_service': 'Azure AI Search',
                'index_name': config.Config.AZURE_SEARCH_INDEX_NAME
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'error': str(e)} 