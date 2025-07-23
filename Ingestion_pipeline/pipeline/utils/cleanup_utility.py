#!/usr/bin/env python3
"""
Comprehensive cleanup utility for production use
Ensures all temporary files are properly deleted after processing
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Tuple, List

logger = logging.getLogger(__name__)

class CleanupUtility:
    """Production-grade cleanup utility"""
    
    def __init__(self, temp_dirs: List[str] = None):
        """
        Initialize cleanup utility
        
        Args:
            temp_dirs: List of temporary directories to clean
        """
        self.temp_dirs = temp_dirs or ["temp_images", "test_outputs"]
        self.cleaned_files = []
        self.failed_files = []
    
    def cleanup_all_temp_files(self) -> Tuple[int, int]:
        """
        Clean up all temporary files from all configured directories
        
        Returns:
            Tuple of (cleaned_count, failed_count)
        """
        total_cleaned = 0
        total_failed = 0
        
        logger.info("Starting comprehensive cleanup of temporary files")
        
        for temp_dir in self.temp_dirs:
            cleaned, failed = self.cleanup_directory(temp_dir)
            total_cleaned += cleaned
            total_failed += failed
        
        # Also clean up any orphaned temp files in root
        cleaned, failed = self.cleanup_orphaned_files()
        total_cleaned += cleaned
        total_failed += failed
        
        logger.info(f"Comprehensive cleanup completed: {total_cleaned} files cleaned, {total_failed} failed")
        return total_cleaned, total_failed
    
    def cleanup_directory(self, directory: str) -> Tuple[int, int]:
        """
        Clean up all files in a specific directory
        
        Args:
            directory: Directory path to clean
            
        Returns:
            Tuple of (cleaned_count, failed_count)
        """
        cleaned_count = 0
        failed_count = 0
        
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.debug(f"Directory {directory} does not exist, skipping")
            return cleaned_count, failed_count
        
        logger.info(f"Cleaning directory: {directory}")
        
        # Clean up all image files
        for pattern in ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.tiff"]:
            for file_path in dir_path.glob(pattern):
                try:
                    os.unlink(file_path)
                    cleaned_count += 1
                    self.cleaned_files.append(str(file_path))
                    logger.debug(f"Cleaned up: {file_path}")
                except Exception as e:
                    failed_count += 1
                    self.failed_files.append(str(file_path))
                    logger.error(f"Failed to clean up {file_path}: {e}")
        
        # Clean up any other temporary files
        for pattern in ["*.tmp", "*.temp", "*_temp.*"]:
            for file_path in dir_path.glob(pattern):
                try:
                    os.unlink(file_path)
                    cleaned_count += 1
                    self.cleaned_files.append(str(file_path))
                    logger.debug(f"Cleaned up: {file_path}")
                except Exception as e:
                    failed_count += 1
                    self.failed_files.append(str(file_path))
                    logger.error(f"Failed to clean up {file_path}: {e}")
        
        # Remove empty directories
        try:
            if dir_path.exists() and not any(dir_path.iterdir()):
                dir_path.rmdir()
                logger.debug(f"Removed empty directory: {directory}")
        except Exception as e:
            logger.debug(f"Could not remove directory {directory}: {e}")
        
        return cleaned_count, failed_count
    
    def cleanup_orphaned_files(self) -> Tuple[int, int]:
        """
        Clean up orphaned temporary files in the current working directory
        
        Returns:
            Tuple of (cleaned_count, failed_count)
        """
        cleaned_count = 0
        failed_count = 0
        
        current_dir = Path.cwd()
        logger.debug("Checking for orphaned temporary files in current directory")
        
        # Look for common temporary file patterns
        patterns = [
            "temp_*.png", "temp_*.jpg", "temp_*.jpeg",
            "*.tmp", "*.temp", "*_temp.*",
            "test_*_output.*", "debug_*.*"
        ]
        
        for pattern in patterns:
            for file_path in current_dir.glob(pattern):
                # Skip if it's a directory
                if file_path.is_dir():
                    continue
                
                try:
                    os.unlink(file_path)
                    cleaned_count += 1
                    self.cleaned_files.append(str(file_path))
                    logger.debug(f"Cleaned up orphaned file: {file_path}")
                except Exception as e:
                    failed_count += 1
                    self.failed_files.append(str(file_path))
                    logger.error(f"Failed to clean up orphaned file {file_path}: {e}")
        
        return cleaned_count, failed_count
    
    def cleanup_session_files(self, session_id: str = None) -> Tuple[int, int]:
        """
        Clean up files from a specific processing session
        
        Args:
            session_id: Session identifier to clean up
            
        Returns:
            Tuple of (cleaned_count, failed_count)
        """
        cleaned_count = 0
        failed_count = 0
        
        if not session_id:
            logger.warning("No session ID provided for session cleanup")
            return cleaned_count, failed_count
        
        logger.info(f"Cleaning up files for session: {session_id}")
        
        for temp_dir in self.temp_dirs:
            dir_path = Path(temp_dir)
            if not dir_path.exists():
                continue
            
            # Look for files matching session ID
            for file_path in dir_path.glob(f"*{session_id}*"):
                try:
                    os.unlink(file_path)
                    cleaned_count += 1
                    self.cleaned_files.append(str(file_path))
                    logger.debug(f"Cleaned up session file: {file_path}")
                except Exception as e:
                    failed_count += 1
                    self.failed_files.append(str(file_path))
                    logger.error(f"Failed to clean up session file {file_path}: {e}")
        
        return cleaned_count, failed_count
    
    def get_cleanup_report(self) -> dict:
        """
        Get a detailed report of the cleanup operation
        
        Returns:
            Dictionary with cleanup statistics
        """
        return {
            'cleaned_files': self.cleaned_files,
            'failed_files': self.failed_files,
            'total_cleaned': len(self.cleaned_files),
            'total_failed': len(self.failed_files),
            'success_rate': len(self.cleaned_files) / (len(self.cleaned_files) + len(self.failed_files)) if (len(self.cleaned_files) + len(self.failed_files)) > 0 else 0
        }
    
    def force_cleanup(self) -> Tuple[int, int]:
        """
        Force cleanup - removes entire temp directories and recreates them
        
        Returns:
            Tuple of (cleaned_count, failed_count)
        """
        cleaned_count = 0
        failed_count = 0
        
        logger.warning("Performing force cleanup - removing entire temp directories")
        
        for temp_dir in self.temp_dirs:
            dir_path = Path(temp_dir)
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    cleaned_count += 1
                    logger.info(f"Force cleaned directory: {temp_dir}")
                    
                    # Recreate empty directory
                    dir_path.mkdir(exist_ok=True)
                    logger.debug(f"Recreated directory: {temp_dir}")
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to force clean directory {temp_dir}: {e}")
        
        return cleaned_count, failed_count


def cleanup_production_files():
    """
    Production cleanup function - cleans up all temporary files
    """
    utility = CleanupUtility()
    cleaned, failed = utility.cleanup_all_temp_files()
    
    if failed > 0:
        logger.warning(f"Production cleanup completed with {failed} failures")
        # In production, we might want to force cleanup if there are failures
        if failed > cleaned * 0.1:  # If more than 10% failed
            logger.warning("Too many cleanup failures, performing force cleanup")
            utility.force_cleanup()
    
    return utility.get_cleanup_report()


if __name__ == "__main__":
    # Test the cleanup utility
    logging.basicConfig(level=logging.INFO)
    
    print("🧹 Testing Production Cleanup Utility")
    print("=" * 40)
    
    utility = CleanupUtility()
    cleaned, failed = utility.cleanup_all_temp_files()
    
    print(f"✅ Cleaned: {cleaned} files")
    print(f"❌ Failed: {failed} files")
    
    report = utility.get_cleanup_report()
    print(f"📊 Success rate: {report['success_rate']:.2%}") 