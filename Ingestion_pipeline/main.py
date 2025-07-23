#!/usr/bin/env python3
"""
Ingestion Pipeline - Main Entry Point
Production-ready main entry point for document ingestion pipeline
"""

import uvicorn
import sys
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup Python path and environment"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Set environment variables if needed
    os.environ.setdefault('INGESTION_PORT', '8001')
    os.environ.setdefault('INGESTION_HOST', '0.0.0.0')

def print_startup_info():
    """Print startup information"""
    print("🚀 Starting Document Ingestion Pipeline")
    print("=" * 50)
    print("✅ Server: http://localhost:8001")
    print("📖 API Docs: http://localhost:8001/docs")
    print("💚 Health: http://localhost:8001/health")
    print("📁 Upload: http://localhost:8001/upload")
    print("\nPress Ctrl+C to stop")
    print("-" * 50)

def main():
    """Main entry point for ingestion pipeline"""
    try:
        # Setup environment
        setup_environment()
        
        # Print startup info
        print_startup_info()
        
        # Start the FastAPI server
        uvicorn.run(
            "api.main:app",
            host=os.environ.get('INGESTION_HOST', '0.0.0.0'),
            port=int(os.environ.get('INGESTION_PORT', 8001)),
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Ingestion Pipeline stopped by user")
    except Exception as e:
        logger.error(f"❌ Error starting Ingestion Pipeline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 