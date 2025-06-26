"""
Voice module for MAYA AI Chatbot.
Handles speech recognition and text-to-speech functionality.
"""

import queue
import threading
import time
import speech_recognition as sr
import pyttsx3
from PyQt6.QtCore import QObject, pyqtSignal

class VoiceAssistant(QObject):
    """Handles voice input/output functionality."""
    
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
        self.available_voices = []
        self.current_voice_id = 0
        
        # Initialize voices
        self._init_voices()
        
        # Configure the speech engine
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def speak(self, text):
        """Convert text to speech.
        
        Args:
            text (str): The text to speak.
        """
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.error_occurred.emit(f"Error in text-to-speech: {str(e)}")
    
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
        
        # Set default voice (first male voice if available, otherwise first voice)
        default_voice = next((v for v in self.available_voices if 'male' in v['name'].lower()), 
                           self.available_voices[0] if self.available_voices else None)
        if default_voice:
            self.set_voice(default_voice['id'])
    
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
