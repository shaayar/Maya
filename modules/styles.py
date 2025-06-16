"""
CSS styles for the MAYA chat application.
"""

# Base styles for the application
BASE_STYLES = """
QMainWindow {
    background-color: #f5f5f5;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QTextBrowser {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    font-size: 14px;
    color: #333;
}

QTextEdit {
    background-color: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 8px;
    font-size: 14px;
    selection-background-color: #4a90e2;
}

QPushButton {
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 14px;
    min-width: 100px;
    max-width: 150px;
    margin: 2px;
}

QPushButton:hover {
    background-color: #357abd;
}

QPushButton:pressed {
    background-color: #2c5d8a;
}

QProgressBar {
    border: 1px solid #ddd;
    border-radius: 4px;
    text-align: center;
    height: 15px;
}

QProgressBar::chunk {
    background-color: #4a90e2;
    border-radius: 2px;
}
"""

# Animation styles
ANIMATION_STYLES = """
/* Animation for message appearance */
@keyframes fadeIn {
    from { 
        opacity: 0; 
        transform: translateY(10px); 
    }
    to { 
        opacity: 1; 
        transform: translateY(0); 
    }
}

/* Apply animation to chat messages */
QTextBrowser QTextBlock {
    animation: fadeIn 0.3s ease-out;
}
"""

def get_styles() -> str:
    """Return the combined styles."""
    return BASE_STYLES + ANIMATION_STYLES
