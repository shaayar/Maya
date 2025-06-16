from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt
import os

class SettingsDialog(QDialog):
    """Dialog for managing application settings including API key."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        self.api_key = os.getenv('GROQ_API_KEY', '')
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # API Key Section
        api_key_layout = QVBoxLayout()
        api_key_label = QLabel("Groq API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter your Groq API key")
        self.api_key_input.setText(self.api_key)
        
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        # Add all to main layout
        layout.addLayout(api_key_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_settings(self):
        """Save the API key to environment variables."""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Error", "API key cannot be empty!")
            return
        
        try:
            # Save to .env file
            with open('.env', 'w') as f:
                f.write(f"GROQ_API_KEY={api_key}")
            
            # Update environment variable for current session
            os.environ['GROQ_API_KEY'] = api_key
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    @staticmethod
    def get_api_key() -> str:
        """Get the API key from environment variables."""
        return os.getenv('GROQ_API_KEY', '')