#!/usr/bin/env python3
"""
Complete Ingestion Pipeline with Vector Storage
Document → Text/Image Analysis → Chunking → Embeddings → Azure AI Search
"""

import os
import sys
import logging
import hashlib
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

sys.path.append(str(Path(__file__).parent))

from pipeline import MultimodalPipeline
from pipeline.utils.config import Config
from pipeline.services.embedding_service import EmbeddingService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChunkingService:
    """Semantic chunking service for documents"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            logger.info(f"Chunking service initialized with size={chunk_size}, overlap={chunk_overlap}")
        except ImportError:
            logger.error("langchain not available, using basic text splitting")
            self.splitter = None
    
    def chunk_document(self, text_content: str, visual_analysis: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        chunks = []
        
        if self.splitter:
            text_chunks = self.splitter.split_text(text_content)
        else:
            text_chunks = self._basic_text_split(text_content)
        
        for i, chunk in enumerate(text_chunks):
            chunks.append({
                'id': f"text_chunk_{i}",
                'content': chunk,
                'chunk_type': 'text',
                'chunk_index': i,
                'page_number': self._extract_page_number(chunk)
            })
        
        if visual_analysis:
            for i, analysis in enumerate(visual_analysis):
                visual_content = f"[Image Summary: {analysis.get('analysis', '')}]"
                chunks.append({
                    'id': f"visual_chunk_{i}",
                    'content': visual_content,
                    'chunk_type': 'visual',
                    'chunk_index': len(chunks) + i,
                    'page_number': analysis.get('page_number', 0)
                })
        
        return chunks
    
    def _basic_text_split(self, text: str) -> List[str]:
        """Basic text splitting as fallback"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _extract_page_number(self, chunk: str) -> int:
        """Extract page number from chunk content"""
        import re
        page_match = re.search(r'--- Page (\d+) ---', chunk)
        return int(page_match.group(1)) if page_match else 0

class AzureAISearchService:
    """Azure AI Search service for vector storage"""
    
    def __init__(self):
        self.endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        self.key = os.getenv('AZURE_SEARCH_KEY')
        self.index_name = os.getenv('AZURE_SEARCH_INDEX_NAME', 'documents-index')
        
        if not self.endpoint or not self.key:
            logger.error("Azure Search configuration missing")
            raise ValueError("AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY required")
        
        try:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents.indexes import SearchIndexClient
            from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchableField
            
            self.credential = AzureKeyCredential(self.key)
            self.search_client = SearchClient(self.endpoint, self.index_name, self.credential)
            self.index_client = SearchIndexClient(self.endpoint, self.credential)
            
            self._ensure_index_exists()
            logger.info(f"Azure AI Search service initialized for index: {self.index_name}")
            
        except ImportError:
            logger.error("azure-search-documents not available")
            raise
    
    def _ensure_index_exists(self):
        """Ensure the search index exists"""
        try:
            self.index_client.get_index(self.index_name)
            logger.info(f"Index {self.index_name} already exists")
        except Exception:
            logger.info(f"Creating Azure AI Search index: {self.index_name}")
            
            index = SearchIndex(
                name=self.index_name,
                fields=[
                    SimpleField(name="id", type="Edm.String", key=True),
                    SearchableField(name="content", type="Edm.String"),
                    SimpleField(name="filename", type="Edm.String", filterable=True, facetable=True),
                    SimpleField(name="chunk_index", type="Edm.Int32", filterable=True, sortable=True),
                    SimpleField(name="page_number", type="Edm.Int32", filterable=True),
                    SimpleField(name="chunk_type", type="Edm.String", filterable=True, facetable=True),
                    SimpleField(name="tags", type="Collection(Edm.String)", filterable=True, facetable=True),
                    SimpleField(name="upload_date", type="Edm.DateTimeOffset", filterable=True, sortable=True)
                ]
            )
            
            self.index_client.create_index(index)
            logger.info(f"Created index: {self.index_name}")
    
    def upload_chunks(self, chunks: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bool:
        """Upload chunks to Azure AI Search"""
        try:
            docs = []
            for chunk in chunks:
                safe_filename = metadata['filename'].replace('.', '_')
                doc = {
                    "id": f"{safe_filename}_{chunk['id']}_{uuid.uuid4().hex[:8]}",
                    "content": chunk['content'],
                    "chunk_index": chunk['chunk_index'],
                    "filename": metadata['filename'],
                    "page_number": chunk['page_number'],
                    "chunk_type": chunk['chunk_type'],
                    "tags": metadata.get('tags', []),
                    "upload_date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
                docs.append(doc)
            
            result = self.search_client.upload_documents(docs)
            logger.info(f"Uploaded {len(docs)} chunks to Azure AI Search")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading chunks to Azure AI Search: {e}")
            return False

class StorageChecker:
    """Azure Blob Storage service for file storage"""
    
    def __init__(self):
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'knowledgebase')
        
        if not self.connection_string:
            logger.warning("Azure Storage not available: Connection string is either blank or malformed.")
            self.storage_available = False
            return
        
        try:
            from azure.storage.blob import BlobServiceClient
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
            self.storage_available = True
            logger.info(f"Azure Storage initialized for container: {self.container_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Storage: {e}")
            self.storage_available = False
    
    def file_exists_in_storage(self, file_path: str) -> bool:
        """Check if file exists in blob storage"""
        if not self.storage_available:
            logger.warning("Storage not available, assuming file doesn't exist")
            return False
        
        try:
            blob_name = Path(file_path).name
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.get_blob_properties()
            logger.info(f"File {file_path} exists in storage: True")
            return True
        except Exception:
            logger.info(f"File {file_path} exists in storage: False")
            return False
    
    def get_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def upload_to_storage(self, file_path: str, blob_name: str = None, metadata: Dict[str, Any] = None) -> bool:
        """Upload file to Azure Blob Storage"""
        if not self.storage_available:
            logger.warning("Storage not available, skipping upload")
            return False
        
        try:
            # Use provided blob name or default to file name
            if blob_name is None:
                blob_name = Path(file_path).name
            
            blob_client = self.container_client.get_blob_client(blob_name)
            
            with open(file_path, 'rb') as f:
                blob_client.upload_blob(f, overwrite=True, metadata=metadata)
            
            logger.info(f"Successfully uploaded {file_path} to storage as {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading file to storage: {e}")
            return False

class CompleteIngestionPipeline:
    """Complete ingestion pipeline with storage checking and vector storage"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.pipeline = MultimodalPipeline(self.config)
        self.storage_checker = StorageChecker()
        self.chunking_service = ChunkingService(
            chunk_size=self.config.get('chunk_size', Config.CHUNK_SIZE),
            chunk_overlap=self.config.get('chunk_overlap', Config.CHUNK_OVERLAP)
        )
        self.embedding_service = EmbeddingService()
        self.search_service = AzureAISearchService()
        self.processed_files = []
        self.skipped_files = []
        self.failed_files = []
        
        logger.info("Complete ingestion pipeline initialized with vector storage")
    
    def process_file_with_storage_check(self, file_path: str, 
                                      original_filename: str = None,
                                      force_reprocess: bool = False,
                                      save_outputs: bool = False,
                                      auto_cleanup: bool = True) -> Dict[str, Any]:
        """Process file with storage existence check"""
        
        print(f"📄 Processing: {file_path}")
        print("-" * 50)
        
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            print(f"❌ {error_msg}")
            self.failed_files.append({'file': file_path, 'error': error_msg})
            return {'success': False, 'error': error_msg}
        
        file_exists = self.storage_checker.file_exists_in_storage(file_path)
        
        if file_exists and not force_reprocess:
            print(f"⏭️ File already exists in storage, skipping processing")
            self.skipped_files.append(file_path)
            return {
                'success': True, 
                'status': 'skipped', 
                'reason': 'file_exists_in_storage',
                'filename': Path(file_path).name
            }
        
        file_hash = self.storage_checker.get_file_hash(file_path)
        
        try:
            print(f"🔄 Processing file...")
            result = self.pipeline.process_document(file_path, save_outputs=save_outputs)
            
            if result['success']:
                print(f"🔄 Document processed, creating chunks...")
                chunks = self.chunking_service.chunk_document(
                    result['text_content'], 
                    result.get('visual_analysis', [])
                )
                
                print(f"🔄 Generated {len(chunks)} chunks, creating embeddings...")
                embedded_chunks = self.embedding_service.generate_embeddings(chunks)
                
                if embedded_chunks:
                    print(f"🔄 Generated embeddings, uploading to Azure AI Search...")
                    
                    metadata = {
                        'filename': Path(file_path).name,
                        'file_path': file_path,
                        'file_hash': file_hash,
                        'tags': self._extract_tags(file_path),
                        'processing_timestamp': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    }
                    
                    upload_success = self.search_service.upload_chunks(embedded_chunks, metadata)
                    
                    if upload_success:
                        print(f"✅ Successfully uploaded {len(embedded_chunks)} chunks to Azure AI Search")
                        
                        # Use original filename for blob storage if provided
                        blob_filename = original_filename if original_filename else Path(file_path).name
                        blob_upload_success = self.storage_checker.upload_to_storage(
                            file_path, 
                            blob_name=blob_filename,
                            metadata={
                                'file_hash': file_hash,
                                'processed_date': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                'chunks_created': str(len(chunks)),
                                'chunks_uploaded': str(len(embedded_chunks)),
                                'pipeline_version': '2.0'
                            }
                        )
                        
                        result.update({
                            'chunks_created': len(chunks),
                            'chunks_uploaded': len(embedded_chunks),
                            'vector_storage_success': upload_success,
                            'blob_storage_uploaded': blob_upload_success,
                            'file_hash': file_hash,
                            'processing_timestamp': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                            'storage_checked': True,
                            'file_exists_in_storage': file_exists
                        })
                        
                        print(f"   - Chunks created: {len(chunks)}")
                        print(f"   - Images analyzed: {result.get('statistics', {}).get('total_images', 0)}")
                        print(f"   - Vector storage: {'✅ Success' if upload_success else '❌ Failed'}")
                        print(f"   - Blob storage: {'✅ Success' if blob_upload_success else '❌ Failed'}")
                        
                        self.processed_files.append(result)
                        
                    else:
                        error_msg = "Failed to upload chunks to Azure AI Search"
                        print(f"❌ {error_msg}")
                        self.failed_files.append({'file': file_path, 'error': error_msg})
                        result['success'] = False
                        result['error'] = error_msg
                else:
                    error_msg = "Failed to generate embeddings"
                    print(f"❌ {error_msg}")
                    self.failed_files.append({'file': file_path, 'error': error_msg})
                    result['success'] = False
                    result['error'] = error_msg
            else:
                print(f"❌ Processing failed: {result.get('error')}")
                self.failed_files.append({'file': file_path, 'error': result.get('error')})
            
            if auto_cleanup:
                self._cleanup_temp_files(file_path)
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing file: {e}"
            print(f"❌ {error_msg}")
            self.failed_files.append({'file': file_path, 'error': error_msg})
            return {'success': False, 'error': error_msg}
    
    def _extract_tags(self, file_path: str) -> List[str]:
        """Extract tags from file path and content"""
        tags = []
        
        file_ext = Path(file_path).suffix.lower()
        if file_ext in ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.txt', '.md']:
            tags.append(f"type:{file_ext[1:]}")
        
        filename = Path(file_path).stem.lower()
        if 'research' in filename:
            tags.append('research')
        if 'paper' in filename:
            tags.append('paper')
        if 'whitepaper' in filename:
            tags.append('whitepaper')
        if 'report' in filename:
            tags.append('report')
        
        return tags
    
    def _cleanup_temp_files(self, file_path: str):
        """Clean up temporary files after processing"""
        try:
            base_name = Path(file_path).stem
            temp_patterns = [
                f"temp_images/{base_name}_*",
                f"test_outputs/{base_name}_*",
                f"temp_images/{base_name}*",
                f"test_outputs/{base_name}*"
            ]
            
            cleaned_count = 0
            for pattern in temp_patterns:
                for temp_file in Path('.').glob(pattern):
                    try:
                        temp_file.unlink()
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete {temp_file}: {e}")
            
            logger.info(f"Cleaned up {cleaned_count} temporary files for {base_name}")
            
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
    
    def process_batch_with_storage_check(self, file_paths: List[str],
                                       force_reprocess: bool = False,
                                       save_outputs: bool = False,
                                       auto_cleanup: bool = True) -> List[Dict[str, Any]]:
        """Process multiple files with storage checking"""
        
        print(f"🚀 Batch Processing {len(file_paths)} Files")
        print("=" * 60)
        
        results = []
        for i, file_path in enumerate(file_paths, 1):
            print(f"\n[{i}/{len(file_paths)}] 📄 Processing: {file_path}")
            print("-" * 50)
            
            result = self.process_file_with_storage_check(
                file_path, force_reprocess, save_outputs, auto_cleanup
            )
            results.append(result)
        
        self.print_batch_summary()
        return results
    
    def print_batch_summary(self):
        """Print batch processing summary"""
        print(f"\n📊 Batch Processing Summary")
        print("=" * 40)
        print(f"   - Files processed: {len(self.processed_files)}")
        print(f"   - Files skipped: {len(self.skipped_files)}")
        print(f"   - Files failed: {len(self.failed_files)}")
        
        if self.processed_files:
            total_chunks = sum(r.get('chunks_created', 0) for r in self.processed_files)
            total_vectors = sum(r.get('chunks_uploaded', 0) for r in self.processed_files)
            total_images = sum(r.get('statistics', {}).get('total_images', 0) for r in self.processed_files)
            vector_success = sum(1 for r in self.processed_files if r.get('vector_storage_success', False))
            blob_success = sum(1 for r in self.processed_files if r.get('blob_storage_uploaded', False))
            
            print(f"   - Total chunks created: {total_chunks}")
            print(f"   - Total chunks uploaded to vectors: {total_vectors}")
            print(f"   - Total images analyzed: {total_images}")
            print(f"   - Vector storage success: {vector_success}/{len(self.processed_files)}")
            print(f"   - Blob storage success: {blob_success}/{len(self.processed_files)}")
        
        if self.failed_files:
            print(f"\n❌ Failed Files:")
            for failed in self.failed_files:
                print(f"   - {failed['file']}: {failed['error']}")
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = {
            'total_files_processed': len(self.processed_files),
            'total_files_skipped': len(self.skipped_files),
            'total_files_failed': len(self.failed_files),
            'total_chunks_created': sum(r.get('chunks_created', 0) for r in self.processed_files),
            'total_chunks_uploaded': sum(r.get('chunks_uploaded', 0) for r in self.processed_files),
            'total_images_analyzed': sum(r.get('statistics', {}).get('total_images', 0) for r in self.processed_files),
            'vector_storage_success_rate': len([r for r in self.processed_files if r.get('vector_storage_success', False)]) / max(len(self.processed_files), 1),
            'blob_storage_success_rate': len([r for r in self.processed_files if r.get('blob_storage_uploaded', False)]) / max(len(self.processed_files), 1)
        }
        return stats

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Complete Ingestion Pipeline")
    parser.add_argument("files", nargs="+", help="Files to process")
    parser.add_argument("--force", action="store_true", help="Force reprocessing")
    parser.add_argument("--save-outputs", action="store_true", help="Save intermediate outputs")
    parser.add_argument("--no-cleanup", action="store_true", help="Skip cleanup")
    
    args = parser.parse_args()
    
    print("🚀 Complete Ingestion Pipeline with Vector Storage")
    print("=" * 60)
    
    # Validate configuration
    required_env_vars = [
        'AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_API_KEY',
        'AZURE_SEARCH_ENDPOINT', 'AZURE_SEARCH_KEY'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    print("✅ Configuration validated")
    
    # Initialize and run pipeline
    pipeline = CompleteIngestionPipeline()
    results = pipeline.process_batch_with_storage_check(
        args.files,
        force_reprocess=args.force,
        save_outputs=args.save_outputs,
        auto_cleanup=not args.no_cleanup
    )
    
    # Print final statistics
    stats = pipeline.get_processing_statistics()
    print(f"\n🎯 Final Statistics:")
    print(f"   - Success Rate: {stats['total_files_processed']}/{len(args.files)} ({stats['total_files_processed']/len(args.files)*100:.1f}%)")
    print(f"   - Vector Storage: {stats['vector_storage_success_rate']*100:.1f}%")
    print(f"   - Blob Storage: {stats['blob_storage_success_rate']*100:.1f}%")

if __name__ == "__main__":
    main() 