import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

class FileManager:
    """Handles all file operations for the application."""
    
    @staticmethod
    def create_file(file_path: str, content: str = "") -> bool:
        """Create a new file with optional content."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error creating file {file_path}: {e}")
            return False
    
    @staticmethod
    def read_file(file_path: str) -> Optional[str]:
        """Read content from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    @staticmethod
    def append_to_file(file_path: str, content: str) -> bool:
        """Append content to an existing file."""
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content + "\n")
            return True
        except Exception as e:
            print(f"Error appending to file {file_path}: {e}")
            return False
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Check if a file exists."""
        return os.path.exists(file_path)
    
    @staticmethod
    def get_file_info(file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a file."""
        try:
            stat_info = os.stat(file_path)
            return {
                'size': stat_info.st_size,
                'created': datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'is_file': os.path.isfile(file_path),
                'is_dir': os.path.isdir(file_path)
            }
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")
            return None
