"""
File manager module for handling file operations in the MAYA AI Chatbot.
"""

import os
import json
from pathlib import Path


class FileManager:
    """Manages file operations for the chatbot application."""
    
    def __init__(self, base_path: str = None):
        """
        Initialize the file manager.
        
        Args:
            base_path: Base directory for application files
        """
        self.base_path = Path(base_path) if base_path else Path.home() / ".maya"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "data").mkdir(exist_ok=True)
    
    def get_data_path(self, filename: str) -> Path:
        """Get the path to a data file."""
        return self.base_path / "data" / filename
    
    def load_json(self, path: Path) -> dict:
        """Load data from a JSON file."""
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return {}
    
    def save_json(self, path: Path, data: dict) -> bool:
        """Save data to a JSON file."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving {path}: {e}")
            return False
    
    def load_todos(self) -> dict:
        """Load todo list data."""
        path = self.get_data_path("todos.json")
        return self.load_json(path)
    
    def save_todos(self, data: dict) -> bool:
        """Save todo list data."""
        path = self.get_data_path("todos.json")
        return self.save_json(path, data)
    
    def load_voice_settings(self) -> dict:
        """Load voice settings."""
        path = self.get_data_path("voice_settings.json")
        return self.load_json(path)
    
    def save_voice_settings(self, settings: dict) -> bool:
        """Save voice settings."""
        path = self.get_data_path("voice_settings.json")
        return self.save_json(path, settings)
