import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon, QFontDatabase, QKeySequence
from PyQt6.QtCore import Qt
from modules.gui import ChatWindow
from modules.theme_manager import ThemeManager
from modules.screen_reader import ScreenReader

def setup_environment():
    """Set up the Python environment and paths."""
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('maya.log')
        ]
    )
    
    # Create necessary directories
    Path("themes").mkdir(exist_ok=True)

class MayaApplication(QApplication):
    """Custom QApplication with accessibility features."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen_reader = ScreenReader()
        self.theme_manager = None
        
    def set_theme_manager(self, theme_manager):
        """Set the theme manager instance."""
        self.theme_manager = theme_manager

def main():
    # Set up the environment
    setup_environment()
    
    # Create the Qt Application
    app = MayaApplication(sys.argv)
    
    # Set application information
    app.setApplicationName("MAYA AI")
    app.setApplicationDisplayName("MAYA AI")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set up theme manager
    theme_manager = ThemeManager(app)
    app.set_theme_manager(theme_manager)
    
    # Load default theme
    theme_manager.load_theme("default")
    
    # Create and show the main window
    window = ChatWindow(screen_reader=app.screen_reader)
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()