#!/usr/bin/env python3
"""
Clean FastAPI Application for Document Ingestion Pipeline
Simple API for document upload and processing
"""

import os
import sys
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from complete_ingestion_pipeline import CompleteIngestionPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Document Ingestion Pipeline API",
    description="API for uploading and processing documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance
pipeline = None
processing_jobs = {}

# Pydantic models
class ProcessingStatus(BaseModel):
    job_id: str
    status: str
    filename: str
    progress: Dict[str, Any]
    created_at: str
    updated_at: str

class ProcessingResult(BaseModel):
    success: bool
    job_id: str
    filename: str
    chunks_created: int
    chunks_uploaded: int
    images_analyzed: int
    vector_storage_success: bool
    blob_storage_uploaded: bool
    processing_time: float
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the pipeline on startup"""
    global pipeline
    
    try:
        # Initialize pipeline
        config = {
            "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "azure_openai_api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "azure_openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            "azure_search_endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
            "azure_search_api_key": os.getenv("AZURE_SEARCH_API_KEY"),
            "azure_search_index_name": os.getenv("AZURE_SEARCH_INDEX_NAME", "fundae-knowledgebase"),
            "azure_storage_connection_string": os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
            "azure_storage_container_name": os.getenv("AZURE_STORAGE_CONTAINER_NAME", "knowledgebase")
        }
        
        pipeline = CompleteIngestionPipeline(config)
        logger.info("Pipeline initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "pipeline_ready": pipeline is not None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/upload", response_model=ProcessingStatus)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    force_reprocess: bool = Query(False, description="Force reprocessing even if file exists in storage")
):
    """Upload and process a document"""
    
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
    
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.txt', '.md', '.markdown']
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Create unique job ID
    job_id = str(uuid4())
    
    # Create uploads directory
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    # Save uploaded file with unique local name but preserve original name for blob storage
    clean_filename = file.filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_filename = f"{timestamp}_{clean_filename}"
    file_path = uploads_dir / local_filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    
    # Initialize job status
    processing_jobs[job_id] = {
        "job_id": job_id,
        "status": "processing",
        "filename": clean_filename,
        "file_path": str(file_path),
        "progress": {
            "step": "uploaded",
            "message": "File uploaded successfully"
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "result": None
    }
    
    # Start background processing
    background_tasks.add_task(
        process_document_background,
        job_id=job_id,
        file_path=str(file_path),
        original_filename=clean_filename,
        force_reprocess=force_reprocess
    )
    
    return ProcessingStatus(**processing_jobs[job_id])

async def process_document_background(job_id: str, file_path: str, original_filename: str, force_reprocess: bool):
    """Background task to process document"""
    
    try:
        # Update status to processing
        processing_jobs[job_id]["status"] = "processing"
        processing_jobs[job_id]["progress"] = {
            "step": "processing",
            "message": "Processing document..."
        }
        processing_jobs[job_id]["updated_at"] = datetime.now().isoformat()
        
        # Process the document with original filename for blob storage
        result = pipeline.process_file_with_storage_check(
            file_path=file_path,
            original_filename=original_filename,
            force_reprocess=force_reprocess,
            save_outputs=True,
            auto_cleanup=True
        )
        
        # Update job with result
        processing_jobs[job_id]["status"] = "completed" if result.get("success") else "failed"
        processing_jobs[job_id]["result"] = result
        processing_jobs[job_id]["updated_at"] = datetime.now().isoformat()
        
        if result.get("success"):
            processing_jobs[job_id]["progress"] = {
                "step": "completed",
                "message": "Document processed successfully"
            }
        else:
            processing_jobs[job_id]["progress"] = {
                "step": "failed",
                "message": result.get("error", "Processing failed")
            }
            
    except Exception as e:
        logger.error(f"Error processing document {filename}: {e}")
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["result"] = {"success": False, "error": str(e)}
        processing_jobs[job_id]["progress"] = {
            "step": "failed",
            "message": f"Processing error: {str(e)}"
        }
        processing_jobs[job_id]["updated_at"] = datetime.now().isoformat()

@app.get("/status/{job_id}", response_model=ProcessingStatus)
async def get_processing_status(job_id: str):
    """Get processing status for a job"""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return ProcessingStatus(**processing_jobs[job_id])

@app.get("/results/{job_id}", response_model=ProcessingResult)
async def get_processing_results(job_id: str):
    """Get processing results for a job"""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = processing_jobs[job_id]
    result = job.get("result", {})
    
    return ProcessingResult(
        success=result.get("success", False),
        job_id=job_id,
        filename=job["filename"],
        chunks_created=result.get("chunks_created", 0),
        chunks_uploaded=result.get("chunks_uploaded", 0),
        images_analyzed=result.get("images_analyzed", 0),
        vector_storage_success=result.get("vector_storage_success", False),
        blob_storage_uploaded=result.get("blob_storage_uploaded", False),
        processing_time=result.get("processing_time", 0.0),
        error=result.get("error")
    )

@app.get("/jobs")
async def list_jobs():
    """List all processing jobs"""
    return {
        "jobs": [
            {
                "job_id": job["job_id"],
                "filename": job["filename"],
                "status": job["status"],
                "created_at": job["created_at"],
                "updated_at": job["updated_at"]
            }
            for job in processing_jobs.values()
        ],
        "total": len(processing_jobs)
    }

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a processing job"""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Remove job from memory
    del processing_jobs[job_id]
    
    return {"message": "Job deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 