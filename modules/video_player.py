"""
Video player module for MAYA AI Chatbot.
Handles video playback during voice mode.
"""
import os
from pathlib import Path
from PyQt6.QtCore import Qt, QUrl, QSize, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                           QSizePolicy, QHBoxLayout)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QIcon

class VideoPlayer(QWidget):
    """A video player widget that can be shown during voice mode."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MAYA - Voice Mode")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set up the media player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        # Set up the video widget
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        
        # Set up the layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.video_widget)
        
        # Add a close button
        self.close_button = QPushButton()
        self.close_button.setIcon(QIcon(":/icons/close.png"))
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 100);
                border: none;
                border-radius: 15px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 150);
            }
        """)
        self.close_button.clicked.connect(self.hide)
        
        # Position the close button in the top-right corner
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        button_layout.setContentsMargins(0, 5, 5, 0)
        
        # Add layouts to main layout
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Set default size
        self.resize(320, 240)
        
        # Set video file path (can be changed later)
        self.video_file = ""
        
    def set_video_file(self, file_path):
        """Set the video file to play."""
        if os.path.exists(file_path):
            self.video_file = file_path
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            return True
        return False
    
    def play(self):
        """Start playing the video."""
        if self.video_file and os.path.exists(self.video_file):
            self.media_player.play()
    
    def stop(self):
        """Stop the video playback."""
        self.media_player.stop()
    
    def set_volume(self, volume):
        """Set the volume (0-100)."""
        self.audio_output.setVolume(volume / 100.0)
    
    def showEvent(self, event):
        """Handle show event - position the window in the bottom-right corner."""
        super().showEvent(event)
        screen_geometry = self.screen().availableGeometry()
        self.move(
            screen_geometry.right() - self.width() - 20,
            screen_geometry.bottom() - self.height() - 20
        )
        
    def closeEvent(self, event):
        """Handle close event - stop the video."""
        self.stop()
        event.accept()
