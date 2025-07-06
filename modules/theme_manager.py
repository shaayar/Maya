"""
Theme Manager for MAYA AI Chatbot.
Handles loading and applying custom CSS themes.
"""
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from PyQt6.QtCore import QFile, QTextStream
from PyQt6.QtWidgets import QApplication, QMessageBox

class ThemeManager:
    """Manages application themes and styles."""
    
    def __init__(self, app: QApplication, themes_dir: str = "themes"):
        """
        Initialize the theme manager.
        
        Args:
            app: The QApplication instance
            themes_dir: Directory containing theme files (relative to app directory)
        """
        self.app = app
        self.themes_dir = Path(themes_dir)
        self.current_theme = "default"
        self.available_themes: Dict[str, str] = {}
        self._discover_themes()
    
    def _discover_themes(self) -> None:
        """Scan the themes directory for available themes."""
        # Convert to absolute path
        abs_themes_dir = Path(os.getcwd()) / self.themes_dir
        
        if not abs_themes_dir.exists():
            abs_themes_dir.mkdir(parents=True, exist_ok=True)
            self._create_default_theme()
        
        # Look for CSS files in the themes directory
        for file in abs_themes_dir.glob("*.css"):
            theme_name = file.stem
            self.available_themes[theme_name] = str(file.absolute())
        
        # If no themes found, create default
        if not self.available_themes:
            self._create_default_theme()
            self._discover_themes()
    
    def _create_default_theme(self) -> None:
        """Create a default theme if none exists."""
        abs_themes_dir = Path(os.getcwd()) / self.themes_dir
        default_theme = abs_themes_dir / "default.css"
        
        # If default.css doesn't exist, create it
        if not default_theme.exists():
            default_css = """
            /* Default MAYA AI Theme */
            QMainWindow, QDialog, QWidget {
                background-color: #f0f0f0;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QTextEdit, QPlainTextEdit, QLineEdit, QTextBrowser {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #3a7bc8;
            }
            
            QPushButton:pressed {
                background-color: #2c6cb0;
            }
            
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin: 2px;
            }
            
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #cccccc;
                padding: 5px 10px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom-color: #ffffff;
            }
            
            QStatusBar {
                background-color: #e0e0e0;
                color: #555555;
                border-top: 1px solid #cccccc;
            }
            """
            try:
                with open(default_theme, 'w', encoding='utf-8') as f:
                    f.write(default_css)
            except Exception as e:
                logging.error(f"Failed to create default theme: {e}")
    
    def get_available_themes(self) -> List[str]:
        """Get a list of available theme names."""
        return list(self.available_themes.keys())
    
    def load_theme(self, theme_name: str) -> bool:
        """
        Load and apply a theme by name.
        
        Args:
            theme_name: Name of the theme to load
            
        Returns:
            bool: True if theme was loaded successfully, False otherwise
        """
        if theme_name not in self.available_themes:
            logging.warning(f"Theme not found: {theme_name}")
            return False
        
        try:
            theme_file = self.available_themes[theme_name]
            file = QFile(theme_file)
            if not file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
                logging.error(f"Failed to open theme file: {theme_file}")
                return False
            
            stream = QTextStream(file)
            self.app.setStyleSheet(stream.readAll())
            self.current_theme = theme_name
            logging.info(f"Applied theme: {theme_name}")
            return True
            
        except Exception as e:
            logging.error(f"Error loading theme {theme_name}: {str(e)}")
            return False
    
    def load_custom_theme(self, file_path: str) -> bool:
        """
        Load and apply a theme from a custom CSS file.
        
        Args:
            file_path: Path to the CSS file
            
        Returns:
            bool: True if theme was loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                logging.error(f"Custom theme file not found: {file_path}")
                return False
                
            file = QFile(file_path)
            if not file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
                logging.error(f"Failed to open custom theme file: {file_path}")
                return False
            
            stream = QTextStream(file)
            self.app.setStyleSheet(stream.readAll())
            self.current_theme = "custom"
            logging.info(f"Applied custom theme from: {file_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error loading custom theme {file_path}: {str(e)}")
            return False
    
    def get_current_theme(self) -> str:
        """Get the name of the currently applied theme."""
        return self.current_theme
