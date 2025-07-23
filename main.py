#!/usr/bin/env python3
"""
RAG2.0 - Main Entry Point
Production-ready main entry point for the complete RAG system
"""

import subprocess
import sys
import time
import os
import signal
import logging
from pathlib import Path
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RAGSystemManager:
    """Manages the complete RAG2.0 system lifecycle"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.root_dir = Path(__file__).parent
        
    def print_banner(self):
        """Print system startup banner"""
        print("=" * 70)
        print("🚀 RAG2.0 - Production RAG System")
        print("=" * 70)
        print("📁 Ingestion Pipeline: http://localhost:8001")
        print("🔍 RAG API: http://localhost:8002")
        print("📖 FastAPI Docs: http://localhost:8002/docs")
        print("💚 Health Check: http://localhost:8002/health")
        print("=" * 70)
    
    def check_environment(self) -> bool:
        """Verify environment configuration"""
        env_file = self.root_dir / ".env"
        if not env_file.exists():
            logger.error("❌ .env file not found!")
            print("Please create a .env file with your Azure configuration.")
            return False
        
        # Check required directories
        required_dirs = ["Ingestion_pipeline", "RAG"]
        for dir_name in required_dirs:
            if not (self.root_dir / dir_name).exists():
                logger.error(f"❌ {dir_name} directory not found!")
                return False
        
        logger.info("✅ Environment check passed")
        return True
    
    def start_ingestion_pipeline(self) -> bool:
        """Start the document ingestion pipeline"""
        logger.info("🔄 Starting Ingestion Pipeline...")
        try:
            ingestion_dir = self.root_dir / "Ingestion_pipeline"
            
            # Change to ingestion directory
            original_dir = os.getcwd()
            os.chdir(ingestion_dir)
            
            # Start the ingestion API
            process = subprocess.Popen([
                sys.executable, "main.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Return to original directory
            os.chdir(original_dir)
            
            # Wait for startup
            time.sleep(3)
            
            if process.poll() is None:
                self.processes.append(process)
                logger.info("✅ Ingestion Pipeline started successfully")
                return True
            else:
                logger.error("❌ Failed to start Ingestion Pipeline")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting Ingestion Pipeline: {e}")
            return False
    
    def start_rag_system(self) -> bool:
        """Start the RAG system"""
        logger.info("🔄 Starting RAG System...")
        try:
            rag_dir = self.root_dir / "RAG"
            
            # Change to RAG directory
            original_dir = os.getcwd()
            os.chdir(rag_dir)
            
            # Start the RAG API
            process = subprocess.Popen([
                sys.executable, "main.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Return to original directory
            os.chdir(original_dir)
            
            # Wait for startup
            time.sleep(3)
            
            if process.poll() is None:
                self.processes.append(process)
                logger.info("✅ RAG System started successfully")
                return True
            else:
                logger.error("❌ Failed to start RAG System")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting RAG System: {e}")
            return False
    
    def stop_all_services(self):
        """Gracefully stop all running services"""
        logger.info("🛑 Stopping all services...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("Force killing process")
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping process: {e}")
        
        self.processes.clear()
        logger.info("✅ All services stopped")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.stop_all_services()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run(self):
        """Main system execution"""
        self.print_banner()
        
        # Check environment
        if not self.check_environment():
            sys.exit(1)
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        logger.info("🚀 Starting RAG2.0 System...")
        print("This will start all components in sequence.")
        print("Press Ctrl+C to stop all services.\n")
        
        try:
            # Start services
            success = True
            
            # Start ingestion pipeline
            if not self.start_ingestion_pipeline():
                success = False
            
            # Start RAG system
            if not self.start_rag_system():
                success = False
            
            if success:
                print("\n🎉 RAG2.0 System started successfully!")
                print("\n📋 Services:")
                print("  • Ingestion Pipeline: http://localhost:8001")
                print("  • RAG API: http://localhost:8002")
                print("  • FastAPI Docs: http://localhost:8002/docs")
                print("\n💡 Usage:")
                print("  1. Upload documents via Ingestion Pipeline")
                print("  2. Search and ask questions via RAG API or Postman")
                print("\nPress Ctrl+C to stop all services.")
                
                # Keep running
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            else:
                logger.error("❌ Failed to start some services. Please check the logs.")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            sys.exit(1)
        finally:
            self.stop_all_services()

def main():
    """Main entry point"""
    manager = RAGSystemManager()
    manager.run()

if __name__ == "__main__":
    main() 