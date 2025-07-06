"""
Screen Reader module for MAYA AI Chatbot.
Provides accessibility features including text-to-speech for UI elements.
"""
import logging
import sys
import traceback
from typing import Optional, Callable, TYPE_CHECKING

# Import Qt modules
try:
    from PyQt6.QtCore import QObject, pyqtSignal, QTimer, Qt
    from PyQt6.QtWidgets import QApplication, QWidget
    PYSIDE = False
except ImportError as e:
    logging.error("Failed to import PyQt6: %s", str(e))
    raise

# Try to import pyttsx3 with fallback to espeak
try:
    import pyttsx3
    TTS_ENGINE = 'pyttsx3'
except ImportError:
    logging.warning("pyttsx3 not found, falling back to espeak (if available)")
    TTS_ENGINE = 'espeak' if sys.platform != 'win32' else None
    if TTS_ENGINE == 'espeak':
        try:
            import subprocess
            subprocess.run(['espeak', '--version'], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            logging.warning("espeak not found, text-to-speech will be disabled")
            TTS_ENGINE = None

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(ch)

logger.info("Screen reader module initialized")

class ScreenReader(QObject):
    """Handles screen reading functionality for accessibility."""
    
    # Signal emitted when screen reader state changes
    state_changed = pyqtSignal(bool)
    
    def __init__(self, parent: Optional[QObject] = None):
        """Initialize the screen reader."""
        super().__init__(parent)
        logger.info("Initializing ScreenReader instance")
        
        self.engine = None
        self.enabled: bool = False
        self.speech_queue: list[str] = []
        self.is_speaking: bool = False
        self.last_spoken: str = ""
        self.repeat_count: int = 0
        self.max_repeats: int = 2
        
        # Initialize TTS engine
        logger.debug("Initializing TTS engine")
        try:
            self.initialize_engine()
            if self.engine is not None:
                logger.info("Screen reader initialized successfully with %s", 
                           'pyttsx3' if TTS_ENGINE == 'pyttsx3' else 'espeak')
            else:
                logger.warning("Screen reader initialized without TTS engine")
        except Exception as e:
            logger.error("Failed to initialize screen reader: %s", str(e), exc_info=True)
        
        # Connect to application focus change events
        try:
            app = QApplication.instance()
            if app:
                logger.debug("Connecting to application focus change events")
                app.focusChanged.connect(self.on_focus_changed)
                logger.debug("Successfully connected to focus change events")
            else:
                logger.warning("No QApplication instance found")
        except Exception as e:
            logger.error("Failed to connect to focus change events: %s", str(e), exc_info=True)
            
        logger.info("ScreenReader initialization complete")
    
    def initialize_engine(self) -> None:
        """Initialize the text-to-speech engine."""
        logger.debug("Initializing TTS engine with TTS_ENGINE=%s", TTS_ENGINE)
        
        if TTS_ENGINE == 'pyttsx3':
            try:
                logger.debug("Attempting to initialize pyttsx3")
                self.engine = pyttsx3.init()
                if not self.engine:
                    raise RuntimeError("pyttsx3.init() returned None")
                
                # Get and log available voices
                voices = self.engine.getProperty('voices')
                logger.debug("Available voices: %s", [v.name for v in voices])
                
                # Configure engine properties
                rate = self.engine.getProperty('rate')
                logger.debug("Default speech rate: %d", rate)
                
                # Set a reasonable default rate if current rate is too fast/slow
                if rate > 200 or rate < 100:
                    self.engine.setProperty('rate', 150)
                    logger.debug("Set speech rate to 150")
                
                # Connect signals if available
                if hasattr(self.engine, 'connect'):
                    logger.debug("Connecting to pyttsx3 signals")
                    self.engine.connect('started-utterance', self.on_speech_started)
                    self.engine.connect('finished-utterance', self.on_speech_finished)
                
                # Test the engine with a simple phrase
                try:
                    self.engine.say("Screen reader initialized")
                    self.engine.runAndWait()
                    logger.info("pyttsx3 engine test successful")
                except Exception as e:
                    logger.warning("pyttsx3 test speech failed: %s", str(e))
                
                return
                
            except Exception as e:
                logger.error("Failed to initialize pyttsx3: %s", str(e), exc_info=True)
                self.engine = None
        
        # Fallback to espeak on Linux if available
        if TTS_ENGINE == 'espeak':
            logger.info("Attempting to use espeak for text-to-speech")
            try:
                import subprocess
                # Test espeak installation
                subprocess.run(['espeak', '--version'], 
                             capture_output=True, 
                             check=True)
                self.engine = 'espeak'
                logger.info("espeak initialized successfully")
                return
            except Exception as e:
                logger.error("Failed to initialize espeak: %s", str(e))
                self.engine = None
            
        logger.warning("No text-to-speech engine could be initialized")
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the screen reader."""
        if enabled != self.enabled:
            self.enabled = enabled
            self.state_changed.emit(enabled)
            if enabled:
                self.speak("Screen reader enabled")
            else:
                self.stop()
    
    def is_enabled(self) -> bool:
        """Check if the screen reader is enabled."""
        return self.enabled and self.engine is not None
    
    def speak(self, text: str, interrupt: bool = False) -> None:
        """
        Speak the given text.
        
        Args:
            text: The text to speak
            interrupt: If True, clear the speech queue and speak immediately
        """
        if not self.enabled or not text or not text.strip():
            return
            
        try:
            if interrupt:
                self.speech_queue.clear()
                self.stop()
                
            self.speech_queue.append(str(text))
            self.process_queue()
        except Exception as e:
            logger.error("Error in speak(): %s", str(e))
            logger.debug("Traceback: %s", traceback.format_exc())
            self.stop()
        
        self.speech_queue.append(text)
        self.process_queue()
    
    def process_queue(self) -> None:
        """Process the speech queue."""
        if not self.is_speaking and self.speech_queue and self.engine:
            text = self.speech_queue.pop(0)
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                self.is_speaking = True
            except Exception as e:
                logging.error(f"Error in text-to-speech: {e}")
                self.is_speaking = False
    
    def stop(self) -> None:
        """Stop current speech and clear the queue."""
        if self.engine:
            try:
                self.engine.stop()
            except Exception as e:
                logging.error(f"Error stopping speech: {e}")
        self.speech_queue.clear()
        self.is_speaking = False
    
    def on_speech_started(self) -> None:
        """Handle speech started event."""
        self.is_speaking = True
    
    def on_speech_finished(self, *args) -> None:
        """Handle speech finished event."""
        self.is_speaking = False
        # Process next item in queue
        QTimer.singleShot(100, self.process_queue)
    
    def on_focus_changed(self, old: QWidget, new: QWidget) -> None:
        """Handle focus change events to read focused elements."""
        if not self.is_enabled() or not new:
            return
            
        # Get accessible text for the focused widget
        text = self.get_accessible_text(new)
        if text:
            self.speak(text)
    
    def get_accessible_text(self, widget: QWidget) -> str:
        """Get accessible text for a widget."""
        if not widget:
            return ""
            
        # Try to get accessible name and description
        accessible = QAccessible.queryAccessibleInterface(widget)
        if not accessible:
            return ""
            
        name = accessible.text(QAccessible.Text.Name)
        description = accessible.text(QAccessible.Text.Description)
        
        # If no accessible name, try to get text from common properties
        if not name and hasattr(widget, 'text'):
            name = str(widget.text())
        
        # Combine name and description if both exist
        if name and description:
            return f"{name}. {description}"
        return name or description or ""
    
    def set_rate(self, rate: float) -> None:
        """Set the speech rate."""
        if self.engine:
            try:
                self.engine.setProperty('rate', rate * 100)  # Convert to engine's scale
            except Exception as e:
                logging.error(f"Error setting speech rate: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop()
        if self.engine:
            try:
                self.engine.endLoop()
            except:
                pass
            self.engine = None
