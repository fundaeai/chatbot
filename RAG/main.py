#!/usr/bin/env python3
"""
RAG System - Main Entry Point
Production-ready main entry point for RAG retrieval and question answering
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
    
    # Add parent directory to path for proper imports
    parent_dir = current_dir.parent
    sys.path.insert(0, str(parent_dir))
    
    # Set environment variables if needed
    os.environ.setdefault('RAG_PORT', '8002')
    os.environ.setdefault('RAG_HOST', '0.0.0.0')

def print_startup_info():
    """Print startup information"""
    print("🚀 Starting RAG System")
    print("=" * 50)
    print("✅ API Server: http://localhost:8002")
    print("📖 API Docs: http://localhost:8002/docs")
    print("💚 Health: http://localhost:8002/health")
    print("📊 Statistics: http://localhost:8002/statistics")
    print("🔍 Search: http://localhost:8002/search")
    print("❓ Ask: http://localhost:8002/ask")
    print("\nPress Ctrl+C to stop")
    print("-" * 50)

def main():
    """Main entry point for RAG system"""
    try:
        # Setup environment
        setup_environment()
        
        # Print startup info
        print_startup_info()
        
        # Start the FastAPI server
        uvicorn.run(
            "api.rag_api:app",
            host=os.environ.get('RAG_HOST', '0.0.0.0'),
            port=int(os.environ.get('RAG_PORT', 8002)),
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 RAG System stopped by user")
    except Exception as e:
        logger.error(f"❌ Error starting RAG System: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 