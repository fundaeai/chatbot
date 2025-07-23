# Document Ingestion Pipeline API

A clean FastAPI server for uploading and processing documents.

## 🚀 Quick Start

### Start the Server
```bash
# Activate virtual environment
source venv/bin/activate

# Start the API server
python start_api.py
```

Server will be available at: http://localhost:8001

## 📖 API Endpoints

### Health Check
```bash
GET /health
```
Check if the server and pipeline are ready.

### Upload Document
```bash
POST /upload
```
Upload a document for processing.

**Parameters:**
- `file`: Document file (PDF, DOCX, PPTX, TXT, MD)
- `force_reprocess`: Boolean (optional) - Force reprocessing if file exists

**Example:**
```bash
curl -X POST "http://localhost:8001/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

### Get Job Status
```bash
GET /status/{job_id}
```
Get the current status of a processing job.

### Get Job Results
```bash
GET /results/{job_id}
```
Get the processing results for a completed job.

### List All Jobs
```bash
GET /jobs
```
List all processing jobs.

### Delete Job
```bash
DELETE /jobs/{job_id}
```
Delete a job from memory.

## 🔧 API Documentation

Visit http://localhost:8001/docs for interactive API documentation.

## 📝 Example Usage

### 1. Upload a Document
```bash
curl -X POST "http://localhost:8001/upload" \
  -F "file=@research_paper.pdf"
```

Response:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "filename": "research_paper.pdf",
  "progress": {
    "step": "uploaded",
    "message": "File uploaded successfully"
  },
  "created_at": "2025-07-20T16:17:51.140507",
  "updated_at": "2025-07-20T16:17:51.140507"
}
```

### 2. Check Status
```bash
curl "http://localhost:8001/status/123e4567-e89b-12d3-a456-426614174000"
```

### 3. Get Results
```bash
curl "http://localhost:8001/results/123e4567-e89b-12d3-a456-426614174000"
```

## 🎯 What Happens

1. **Upload** - File is saved and job is created
2. **Processing** - Document is converted to text and images
3. **Chunking** - Text is split into semantic chunks
4. **Embeddings** - Vector embeddings are generated
5. **Storage** - Chunks uploaded to Azure AI Search
6. **Blob Storage** - Original file stored in Azure Blob Storage
7. **Cleanup** - Temporary files are removed

## 📁 Supported File Types

- PDF (.pdf)
- Word (.docx, .doc)
- PowerPoint (.pptx, .ppt)
- Text (.txt)
- Markdown (.md, .markdown)

## ⚙️ Environment Variables

Make sure your `.env` file contains:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_API_KEY`
- `AZURE_STORAGE_CONNECTION_STRING` 