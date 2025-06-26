import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from modules.gui import ChatWindow

def setup_environment():
    """Set up the Python environment and paths."""
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

def main():
    # Set up the environment
    setup_environment()
    
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # Set application information
    app.setApplicationName("MAYA AI")
    app.setApplicationDisplayName("MAYA AI Assistant")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = ChatWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()