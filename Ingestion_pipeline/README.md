# Document Ingestion Pipeline

A powerful, production-ready document ingestion pipeline that converts documents into searchable vector embeddings and stores them in Azure AI Search and Azure Blob Storage.

## 🚀 Features

- **Multi-format Support**: PDF, DOCX, PPTX, TXT, MD files
- **Multimodal Processing**: Text extraction + visual content analysis
- **Semantic Chunking**: Intelligent text splitting with context preservation
- **Vector Embeddings**: Azure OpenAI integration for embedding generation
- **Azure AI Search**: Vector search capabilities
- **Azure Blob Storage**: Original document storage with metadata
- **FastAPI Web Interface**: Clean REST API for document uploads
- **Background Processing**: Asynchronous document processing
- **Clean File Naming**: No UUID prefixes in storage
- **Error Handling**: Robust error handling and retry logic

## 📋 Prerequisites

### Azure Services Required
- **Azure OpenAI Service** with GPT-4 and text-embedding-ada-002 deployments
- **Azure AI Search** service
- **Azure Blob Storage** account

### System Requirements
- Python 3.8+
- 4GB+ RAM (for processing large documents)
- Internet connection for Azure services

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/fundaeai/ingestion_pipeline.git
cd Ingestion_pipeline
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX_NAME=your-index-name

# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-account;AccountKey=your-key;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER_NAME=knowledgebase
```

### 5. Azure Setup

#### Azure OpenAI Service
1. Create an Azure OpenAI resource
2. Deploy these models:
   - **GPT-4** (for image analysis)
   - **text-embedding-ada-002** (for embeddings)
3. Note the endpoint and API key

#### Azure AI Search
1. Create an Azure AI Search service
2. Create an index using the provided `azure_search_index.json`:
   ```bash
   python create_index.py
   ```

#### Azure Blob Storage
1. Create a storage account
2. Create a container named `knowledgebase`
3. Get the connection string from Access Keys

## 🚀 Quick Start

### Start the API Server
```bash
python start_api.py
```

The server will start at: http://localhost:8001

### Upload Documents via API

#### Using curl
```bash
# Upload a single document
curl -X POST "http://localhost:8001/upload" \
  -F "file=@your_document.pdf"

# Upload with force reprocess
curl -X POST "http://localhost:8001/upload?force_reprocess=true" \
  -F "file=@your_document.pdf"
```

#### Using Python
```python
import requests

# Upload document
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/upload',
        files={'file': f}
    )
    job_id = response.json()['job_id']

# Check status
status = requests.get(f'http://localhost:8001/status/{job_id}').json()
print(f"Status: {status['status']}")

# Get results
results = requests.get(f'http://localhost:8001/results/{job_id}').json()
print(f"Chunks created: {results['chunks_created']}")
```

### Command Line Interface
```bash
# Process single file
python complete_ingestion_pipeline.py document.pdf

# Process multiple files
python complete_ingestion_pipeline.py file1.pdf file2.docx file3.txt

# Force reprocess existing files
python complete_ingestion_pipeline.py document.pdf --force
```

## 📖 API Reference

### Endpoints

#### Health Check
```http
GET /health
```
Returns server and pipeline status.

#### Upload Document
```http
POST /upload
```
Upload a document for processing.

**Parameters:**
- `file`: Document file (multipart/form-data)
- `force_reprocess`: Boolean (optional) - Force reprocessing

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "filename": "document.pdf",
  "progress": {
    "step": "uploaded",
    "message": "File uploaded successfully"
  },
  "created_at": "2025-07-20T16:25:17.791635",
  "updated_at": "2025-07-20T16:25:17.791639"
}
```

#### Get Job Status
```http
GET /status/{job_id}
```
Get processing status for a job.

#### Get Job Results
```http
GET /results/{job_id}
```
Get detailed processing results.

**Response:**
```json
{
  "success": true,
  "job_id": "uuid",
  "filename": "document.pdf",
  "chunks_created": 29,
  "chunks_uploaded": 29,
  "images_analyzed": 13,
  "vector_storage_success": true,
  "blob_storage_uploaded": true,
  "processing_time": 41.42,
  "error": null
}
```

#### List All Jobs
```http
GET /jobs
```
List all processing jobs.

#### Delete Job
```http
DELETE /jobs/{job_id}
```
Delete a job from memory.

### Interactive Documentation
Visit http://localhost:8001/docs for Swagger UI interface.

## 🔧 Configuration

### Pipeline Settings
The pipeline can be configured through environment variables or by modifying the config:

```python
config = {
    'chunk_size': 1000,           # Text chunk size
    'chunk_overlap': 200,         # Overlap between chunks
    'save_outputs': True,         # Save intermediate outputs
    'auto_cleanup': True          # Clean up temporary files
}
```

### Supported File Types
- **PDF** (.pdf) - Full text and image extraction
- **Word** (.docx, .doc) - Text and embedded images
- **PowerPoint** (.pptx, .ppt) - Text and slides
- **Text** (.txt) - Plain text
- **Markdown** (.md, .markdown) - Formatted text

## 📊 Processing Pipeline

### 1. Document Upload
- File validation and type checking
- Temporary storage with unique naming
- Job creation and tracking

### 2. Content Extraction
- **Text Extraction**: Extract all text content
- **Visual Analysis**: Analyze images and diagrams using GPT-4 Vision
- **Metadata Extraction**: Document properties and structure

### 3. Semantic Chunking
- Intelligent text splitting based on semantic boundaries
- Context preservation across chunks
- Image context integration

### 4. Embedding Generation
- Azure OpenAI text-embedding-ada-002 model
- Batch processing with retry logic
- Vector dimension: 1536

### 5. Storage
- **Azure AI Search**: Vector embeddings for semantic search
- **Azure Blob Storage**: Original documents with metadata
- **Clean Naming**: Original filenames preserved

### 6. Cleanup
- Temporary file removal
- Memory cleanup
- Job completion tracking

## 📈 Performance

### Processing Times (Approximate)
- **Small PDF (1-5 pages)**: 10-30 seconds
- **Medium PDF (5-20 pages)**: 30-90 seconds
- **Large PDF (20+ pages)**: 90+ seconds
- **Text files**: 5-15 seconds

### Resource Usage
- **Memory**: 500MB-2GB depending on document size
- **CPU**: Moderate usage during processing
- **Network**: High during Azure API calls

### Azure App Service
1. Deploy to Azure App Service
2. Configure environment variables
3. Set up custom domain and SSL
4. Configure scaling rules


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

