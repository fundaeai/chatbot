# RAG2.0 - Complete RAG System

A comprehensive Retrieval-Augmented Generation (RAG) system with document ingestion and intelligent search capabilities.

## 🏗️ Project Structure

```
RAG2.0/
├── Ingestion_pipeline/     # Document ingestion and processing
├── RAG/                   # RAG retrieval and question answering
├── .env                   # Environment configuration
└── .gitignore            # Git ignore rules
```

## 🚀 Features

### Ingestion Pipeline
- **Multi-format Support**: PDF, DOCX, PPTX, TXT, MD files
- **Multimodal Processing**: Text extraction + visual content analysis
- **Semantic Chunking**: Intelligent text splitting with context preservation
- **Vector Embeddings**: Azure OpenAI integration for embedding generation
- **Azure AI Search**: Vector search capabilities
- **Azure Blob Storage**: Original document storage with metadata
- **FastAPI Web Interface**: Clean REST API for document uploads

### RAG Retrieval System
- **Semantic Search**: Vector-based similarity search using Azure AI Search
- **Hybrid Search**: Combines semantic and keyword search for better results
- **Context-Aware Retrieval**: Intelligent chunk selection and context building
- **Question Answering**: GPT-4 powered Q&A with retrieved context
- **Multi-Modal Support**: Handles text and visual content from documents
- **Real-time Processing**: Fast response times with caching
- **RESTful API**: Clean API interface for integration
- **Web Interface**: User-friendly web UI for document search

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
git clone <repository-url>
cd RAG2.0
```

### 2. Environment Configuration
Create a `.env` file in the project root:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX_NAME=documents-index

# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-account;AccountKey=your-key;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER_NAME=knowledgebase

# RAG Configuration
RAG_CHUNK_SIZE=1000
RAG_OVERLAP=200
MAX_CONTEXT_LENGTH=4000
TOP_K_RESULTS=5
```

### 3. Install Dependencies

#### Ingestion Pipeline
```bash
cd Ingestion_pipeline
pip install -r requirements.txt
```

#### RAG System
```bash
cd RAG
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1. Start Complete System (Recommended)
```bash
python main.py
```
This starts both the ingestion pipeline and RAG system together.

### 2. Start Individual Components

**Ingestion Pipeline:**
```bash
cd Ingestion_pipeline
python main.py
```
- **API Server**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

**RAG System:**
```bash
cd RAG
python main.py
```
- **API Server**: http://localhost:8002
- **API Docs**: http://localhost:8002/docs

## 📖 Usage

### Document Ingestion

#### Upload Documents via API
```bash
# Upload a document
curl -X POST "http://localhost:8001/upload" \
  -F "file=@your_document.pdf"

# Check processing status
curl "http://localhost:8001/status/{job_id}"

# Get results
curl "http://localhost:8001/results/{job_id}"
```

#### Command Line Interface
```bash
cd Ingestion_pipeline
python complete_ingestion_pipeline.py document.pdf
```

### RAG Retrieval

#### Search Documents
```bash
curl -X POST "http://localhost:8002/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "top_k": 5,
    "search_type": "hybrid"
  }'
```

#### Ask Questions
```bash
curl -X POST "http://localhost:8002/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main types of machine learning?",
    "context_length": 4000,
    "temperature": 0.7
  }'
```

#### Python Client
```python
from Retreival.rag_client import RAGClient

client = RAGClient("http://localhost:8002")

# Search documents
results = client.search("machine learning algorithms")

# Ask questions
answer = client.ask("What is deep learning?")
```

## 🔧 Configuration

### Ingestion Pipeline Settings
- `chunk_size`: Text chunk size (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 200)
- `save_outputs`: Save intermediate outputs (default: true)
- `auto_cleanup`: Clean up temporary files (default: true)

### RAG Settings
- `top_k`: Number of results to retrieve (default: 5)
- `search_type`: "semantic", "keyword", or "hybrid" (default: "hybrid")
- `context_length`: Maximum context length for GPT-4 (default: 4000)
- `temperature`: Response creativity (default: 0.7)

## 📊 Performance

### Ingestion Pipeline
- **Small PDF (1-5 pages)**: 10-30 seconds
- **Medium PDF (5-20 pages)**: 30-90 seconds
- **Large PDF (20+ pages)**: 90+ seconds

### RAG Retrieval
- **Search**: 100-500ms
- **Q&A**: 2-5 seconds
- **Web Interface**: < 1 second

## 🎯 Supported File Types

- **PDF** (.pdf) - Full text and image extraction
- **Word** (.docx, .doc) - Text and embedded images
- **PowerPoint** (.pptx, .ppt) - Text and slides
- **Text** (.txt) - Plain text
- **Markdown** (.md, .markdown) - Formatted text

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 