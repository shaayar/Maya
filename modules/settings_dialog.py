from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QHBoxLayout, QMessageBox, QComboBox,
                            QGroupBox, QFormLayout, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal
import os
import json
from typing import Dict, Any, List

class SettingsDialog(QDialog):
    """Dialog for managing application settings including API key and voice preferences."""
    
    settings_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None, voice_assistant=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.api_key = os.getenv('GROQ_API_KEY', '')
        self.voice_assistant = voice_assistant
        self.settings_file = 'settings.json'
        self.settings = self._load_settings()
        self.voice_combo = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # API Key Section
        api_group = QGroupBox("API Settings")
        api_layout = QVBoxLayout()
        
        api_key_layout = QVBoxLayout()
        api_key_label = QLabel("Groq API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter your Groq API key")
        self.api_key_input.setText(self.api_key)
        
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        api_layout.addLayout(api_key_layout)
        api_group.setLayout(api_layout)
        
        # Voice Settings Section
        voice_group = QGroupBox("Voice Settings")
        voice_layout = QFormLayout()
        
        # Voice Selection
        self.voice_combo = QComboBox()
        self.voice_combo.currentIndexChanged.connect(self.on_voice_changed)
        voice_layout.addRow("Voice:", self.voice_combo)
        
        # Voice Rate
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setRange(100, 300)  # 100% to 300% of normal rate
        self.rate_slider.setValue(150)  # Default to 150%
        self.rate_slider.valueChanged.connect(self.on_rate_changed)
        voice_layout.addRow("Speech Rate:", self.rate_slider)
        
        voice_group.setLayout(voice_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        # Add all to main layout
        layout.addWidget(api_group)
        layout.addWidget(voice_group)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Load voice settings
        self.load_voice_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or return defaults."""
        default_settings = {
            'voice_id': 0,
            'voice_rate': 150
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return {**default_settings, **json.load(f)}
        except Exception as e:
            print(f"Error loading settings: {e}")
            
        return default_settings
    
    def _save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def load_voice_settings(self):
        """Load and populate voice settings."""
        if not self.voice_assistant:
            return
            
        # Populate voices
        voices = self.voice_assistant.get_available_voices()
        self.voice_combo.clear()
        for voice in voices:
            self.voice_combo.addItem(f"{voice['name']} ({voice['gender']})", voice['id'])
        
        # Set current voice
        current_voice = self.settings.get('voice_id', 0)
        if 0 <= current_voice < len(voices):
            self.voice_combo.setCurrentIndex(current_voice)
        
        # Set rate
        rate = self.settings.get('voice_rate', 150)
        self.rate_slider.setValue(rate)
    
    def on_voice_changed(self, index):
        """Handle voice selection change."""
        if self.voice_assistant and 0 <= index < len(self.voice_assistant.available_voices):
            self.settings['voice_id'] = index
            self.voice_assistant.set_voice(index)
    
    def on_rate_changed(self, value):
        """Handle speech rate change."""
        if self.voice_assistant:
            self.settings['voice_rate'] = value
            self.voice_assistant.engine.setProperty('rate', value)
    
    def save_settings(self):
        """Save all settings to file and environment."""
        # Save API key
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Error", "API key cannot be empty!")
            return
        
        try:
            # Save API key to .env
            with open('.env', 'w') as f:
                f.write(f"GROQ_API_KEY={api_key}")
            
            # Update environment variable for current session
            os.environ['GROQ_API_KEY'] = api_key
            
            # Save other settings
            self._save_settings()
            
            # Emit signal that settings were updated
            self.settings_updated.emit(self.settings)
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    @staticmethod
    def get_api_key() -> str:
        """Get the API key from environment variables."""
        return os.getenv('GROQ_API_KEY', '')