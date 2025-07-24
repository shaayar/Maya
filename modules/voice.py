"""
Voice module for MAYA AI Chatbot.
Handles speech recognition and text-to-speech functionality.
"""

import queue
import threading
import time
import os
from pathlib import Path
import speech_recognition as sr
import pyttsx3
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from .character import CharacterSystem, CharacterTrait

class VoiceAssistant(QObject):
    """Handles voice input/output functionality with video support."""
    
    # Signals
    wake_word_detected = pyqtSignal()
    speech_recognized = pyqtSignal(str)
    listening_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, wake_word="hey maya"):
        """Initialize the voice assistant.
        
        Args:
            wake_word (str): The wake word to activate the assistant.
        """
        super().__init__()
        self.wake_word = wake_word.lower()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.stop_listening = threading.Event()
        self.voice_thread = None
        
        # Voice and character settings
        self.available_voices = []
        self.current_voice_id = 0
        self.character_system = CharacterSystem()
        self.response_mode = "text"  # 'text' or 'voice'
        self.anime_voice_enabled = False
        
        # Video player attributes
        self.video_player = None
        self.video_file = None
        self.video_visible = False
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self._check_video_status)
        
        # Initialize voices
        self._init_voices()
        
        # Configure the speech engine
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def set_video_file(self, file_path):
        """Set the video file to play during voice mode.
        
        Args:
            file_path (str): Path to the video file.
        """
        if os.path.exists(file_path):
            self.video_file = file_path
            if self.video_player:
                self.video_player.set_video_file(file_path)
            return True
        return False
    
    def _init_video_player(self):
        """Initialize the video player if not already created."""
        if not self.video_player:
            from .video_player import VideoPlayer
            self.video_player = VideoPlayer()
            if self.video_file:
                self.video_player.set_video_file(self.video_file)
    
    def _show_video(self):
        """Show the video player and start playback."""
        if not self.video_visible and self.video_file:
            self._init_video_player()
            self.video_player.show()
            self.video_player.play()
            self.video_visible = True
            # Start timer to check video status
            self.video_timer.start(1000)  # Check every second
    
    def _hide_video(self):
        """Hide the video player and stop playback."""
        if self.video_visible and self.video_player:
            self.video_player.stop()
            self.video_player.hide()
            self.video_visible = False
            self.video_timer.stop()
    
    def _check_video_status(self):
        """Check if video playback has finished and hide if needed."""
        if self.video_player and not self.video_player.media_player.isPlaying():
            self._hide_video()
    
    def set_response_mode(self, mode: str):
        """Set the response mode ('text' or 'voice')."""
        if mode in ["text", "voice"]:
            self.response_mode = mode
            return True
        return False
    
    def set_anime_voice(self, enabled: bool):
        """Enable or disable anime voice mode."""
        self.anime_voice_enabled = enabled
        if enabled and not self.character_system.get_current_trait():
            # Set default trait if none selected
            self.character_system.set_character_trait("tsundere")
        self._apply_voice_settings()
    
    def set_character_trait(self, trait_name: str) -> bool:
        """Set the current character trait."""
        success = self.character_system.set_character_trait(trait_name)
        if success:
            self._apply_voice_settings()
        return success
    
    def _apply_voice_settings(self):
        """Apply current voice settings to the TTS engine."""
        if not self.anime_voice_enabled:
            # Reset to default voice settings
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 1.0)
            if self.available_voices and self.current_voice_id < len(self.available_voices):
                self.engine.setProperty('voice', self.available_voices[self.current_voice_id].id)
            return
        
        # Apply anime character voice settings
        trait = self.character_system.get_current_trait()
        if trait:
            # Base rate is 150, apply modifier (-50% to +50%)
            rate = 150 * (1.0 + (trait.speed_modifier - 1.0) * 0.5)
            self.engine.setProperty('rate', int(rate))
            
            # Adjust pitch (if supported by the TTS engine)
            try:
                # This is engine-specific and might not work with all TTS engines
                self.engine.setProperty('pitch', 1.0 + trait.pitch_modifier)
            except:
                pass  # Pitch adjustment not supported
    
    def speak(self, text):
        """Convert text to speech and show video if available.
        
        Args:
            text (str): The text to speak.
        """
        try:
            # Format text based on character traits if in anime mode
            if self.anime_voice_enabled:
                text = self.character_system.format_response(text)
            
            # Only speak if in voice mode
            if self.response_mode == "voice":
                # Show video when speaking starts
                self._show_video()
                
                # Speak the text
                self.engine.say(text)
                self.engine.runAndWait()
                
                # Schedule video to hide after a short delay
                QTimer.singleShot(2000, self._hide_video)
            
            return text
            
        except Exception as e:
            self.error_occurred.emit(f"Error in text-to-speech: {str(e)}")
            self._hide_video()
    
    def listen_in_background(self):
        """Start listening for the wake word in a background thread."""
        if self.voice_thread and self.voice_thread.is_alive():
            return
            
        self.stop_listening.clear()
        self.voice_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.voice_thread.start()
    
    def _listen_loop(self):
        """Main listening loop for the wake word."""
        while not self.stop_listening.is_set():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                
                try:
                    # Recognize speech using Google's speech recognition
                    text = self.recognizer.recognize_google(audio).lower()
                    
                    # Check for wake word
                    if self.wake_word in text:
                        self.wake_word_detected.emit()
                        self.speak("Yes, how can I help you?")
                        self.start_speech_recognition()
                        
                except sr.UnknownValueError:
                    # Speech was unintelligible
                    pass
                except sr.RequestError as e:
                    self.error_occurred.emit(f"Could not request results; {e}")
                
            except sr.WaitTimeoutError:
                # No speech detected, continue listening
                pass
            except Exception as e:
                self.error_occurred.emit(f"Error in listen loop: {str(e)}")
    
    def start_speech_recognition(self):
        """Start actively listening for user commands."""
        self.is_listening = True
        self.listening_changed.emit(True)
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    self.speech_recognized.emit(text)
                except sr.UnknownValueError:
                    self.speak("I didn't catch that. Could you repeat?")
                except sr.RequestError as e:
                    self.error_occurred.emit(f"Could not request results; {e}")
                    
        except Exception as e:
            self.error_occurred.emit(f"Error in speech recognition: {str(e)}")
        finally:
            self.is_listening = False
            self.listening_changed.emit(False)
    
    def stop(self):
        """Stop all voice activities."""
        self.stop_listening.set()
        if self.voice_thread and self.voice_thread.is_alive():
            self.voice_thread.join(timeout=1)
        self.engine.stop()
    
    def _init_voices(self):
        """Initialize available voices and set default voice."""
        voices = self.engine.getProperty('voices')
        self.available_voices = [{'id': i, 'name': voice.name, 'gender': 'Male' if 'male' in voice.name.lower() else 'Female'}
                               for i, voice in enumerate(voices)]
        
        # Try to find a female voice first, then fall back to any available voice
        default_voice = next(
            (v for v in self.available_voices if 'female' in v['name'].lower() or v['gender'] == 'Female'),
            next((v for v in self.available_voices if 'male' in v['name'].lower() or v['gender'] == 'Male'),
                 self.available_voices[0] if self.available_voices else None)
        )
        
        if default_voice:
            self.set_voice(default_voice['id'])
            self.current_voice_id = default_voice['id']
    
    def get_available_voices(self):
        """Get list of available voices.
        
        Returns:
            list: List of dictionaries with voice information
        """
        return self.available_voices
    
    def get_current_voice(self):
        """Get the current voice ID.
        
        Returns:
            int: Current voice ID
        """
        return self.current_voice_id
    
    def set_voice(self, voice_id):
        """Set the voice to use for speech.
        
        Args:
            voice_id (int): ID of the voice to use
            
        Returns:
            bool: True if voice was set successfully, False otherwise
        """
        try:
            voices = self.engine.getProperty('voices')
            if 0 <= voice_id < len(voices):
                self.engine.setProperty('voice', voices[voice_id].id)
                self.current_voice_id = voice_id
                return True
            return False
        except Exception as e:
            print(f"Error setting voice: {e}")
            return False
    
    def __del__(self):
        """Cleanup resources."""
        self.stop()
