"""
Character settings dialog for MAYA AI Chatbot.
Allows users to customize anime character traits and voice settings.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QPushButton, QGroupBox, QFormLayout,
                           QSlider, QCheckBox, QMessageBox, QLineEdit, QTextEdit)
from PyQt6.QtCore import Qt
from .character import CharacterSystem

class CharacterDialog(QDialog):
    """Dialog for customizing character traits and voice settings."""
    
    def __init__(self, voice_assistant, parent=None):
        """Initialize the character dialog.
        
        Args:
            voice_assistant: Reference to the VoiceAssistant instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.voice_assistant = voice_assistant
        self.character_system = voice_assistant.character_system
        self.setWindowTitle("Character Settings")
        self.setMinimumWidth(400)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Response Mode Group
        mode_group = QGroupBox("Response Mode")
        mode_layout = QHBoxLayout()
        
        self.text_mode_btn = QPushButton("Text Only")
        self.voice_mode_btn = QPushButton("Voice")
        self.text_mode_btn.setCheckable(True)
        self.voice_mode_btn.setCheckable(True)
        
        mode_btn_group = QHBoxLayout()
        mode_btn_group.addWidget(self.text_mode_btn)
        mode_btn_group.addWidget(self.voice_mode_btn)
        
        self.anime_voice_cb = QCheckBox("Anime Voice Mode")
        
        mode_layout.addLayout(mode_btn_group)
        mode_layout.addWidget(self.anime_voice_cb)
        mode_group.setLayout(mode_layout)
        
        # Character Traits Group
        trait_group = QGroupBox("Character Traits")
        trait_layout = QFormLayout()
        
        self.trait_combo = QComboBox()
        self.trait_combo.addItems(self.character_system.get_available_traits())
        self.trait_combo.currentTextChanged.connect(self.on_trait_changed)
        
        self.preview_btn = QPushButton("Preview Voice")
        self.preview_btn.clicked.connect(self.preview_voice)
        
        trait_layout.addRow("Character Type:", self.trait_combo)
        trait_layout.addRow("", self.preview_btn)
        
        # Customization Group
        custom_group = QGroupBox("Customize Trait")
        custom_layout = QFormLayout()
        
        self.trait_name_edit = QLineEdit()
        self.trait_desc_edit = QTextEdit()
        self.trait_desc_edit.setMaximumHeight(80)
        
        self.pitch_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_slider.setRange(-100, 100)
        self.pitch_slider.setValue(0)
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)
        
        custom_layout.addRow("Trait Name:", self.trait_name_edit)
        custom_layout.addRow("Description:", self.trait_desc_edit)
        custom_layout.addRow("Pitch (Low to High):", self.pitch_slider)
        custom_layout.addRow("Speed (Slow to Fast):", self.speed_slider)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        # Assemble layout
        trait_group.setLayout(trait_layout)
        custom_group.setLayout(custom_layout)
        
        layout.addWidget(mode_group)
        layout.addWidget(trait_group)
        layout.addWidget(custom_group)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connect signals
        self.text_mode_btn.clicked.connect(lambda: self.set_response_mode("text"))
        self.voice_mode_btn.clicked.connect(lambda: self.set_response_mode("voice"))
        self.anime_voice_cb.toggled.connect(self.toggle_anime_voice)
    
    def load_settings(self):
        """Load current settings into the UI."""
        # Set response mode
        if self.voice_assistant.response_mode == "voice":
            self.voice_mode_btn.setChecked(True)
        else:
            self.text_mode_btn.setChecked(True)
        
        # Set anime voice mode
        self.anime_voice_cb.setChecked(self.voice_assistant.anime_voice_enabled)
        
        # Load current trait if any
        current_trait = self.character_system.get_current_trait()
        if current_trait:
            trait_name = current_trait.name.lower()
            index = self.trait_combo.findText(trait_name, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.trait_combo.setCurrentIndex(index)
            self.update_trait_ui(current_trait)
    
    def update_trait_ui(self, trait):
        """Update UI with trait settings."""
        self.trait_name_edit.setText(trait.name)
        self.trait_desc_edit.setPlainText(trait.description)
        self.pitch_slider.setValue(int(trait.pitch_modifier * 100))
        self.speed_slider.setValue(int(trait.speed_modifier * 100))
    
    def on_trait_changed(self, trait_name):
        """Handle trait selection change."""
        if self.character_system.set_character_trait(trait_name.lower()):
            trait = self.character_system.get_current_trait()
            if trait:
                self.update_trait_ui(trait)
    
    def set_response_mode(self, mode):
        """Set the response mode."""
        if mode == "voice":
            self.voice_mode_btn.setChecked(True)
            self.text_mode_btn.setChecked(False)
        else:
            self.text_mode_btn.setChecked(True)
            self.voice_mode_btn.setChecked(False)
    
    def toggle_anime_voice(self, enabled):
        """Toggle anime voice mode."""
        self.voice_assistant.set_anime_voice(enabled)
        self.trait_combo.setEnabled(enabled)
        self.preview_btn.setEnabled(enabled)
    
    def preview_voice(self):
        """Preview the current voice settings."""
        test_phrase = "Konnichiwa! Watashi wa Maya desu!"
        self.voice_assistant.speak(test_phrase)
    
    def save_settings(self):
        """Save settings and close the dialog."""
        # Save response mode
        mode = "voice" if self.voice_mode_btn.isChecked() else "text"
        self.voice_assistant.set_response_mode(mode)
        
        # Save anime voice mode
        self.voice_assistant.set_anime_voice(self.anime_voice_cb.isChecked())
        
        # Save character trait
        trait_name = self.trait_name_edit.text().strip().lower()
        if trait_name and self.anime_voice_cb.isChecked():
            pitch = self.pitch_slider.value() / 100.0
            speed = self.speed_slider.value() / 100.0
            description = self.trait_desc_edit.toPlainText()
            
            self.character_system.customize_trait(
                trait_name,
                name=trait_name.capitalize(),
                description=description,
                pitch_modifier=pitch,
                speed_modifier=speed
            )
            self.character_system.save_traits()
        
        self.accept()
