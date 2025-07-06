"""
Screen Manipulation Module for MAYA AI Chatbot.
Provides functionality for capturing and manipulating screen content.
"""
import os
import logging
import numpy as np
from typing import Optional, Tuple, Union, List
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QGuiApplication
from PyQt6.QtWidgets import QApplication, QWidget, QGraphicsPixmapItem, QGraphicsScene

try:
    import mss
    import mss.tools
    from PIL import Image, ImageGrab, ImageQt
    import cv2
    import pytesseract
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError:
    SCREEN_CAPTURE_AVAILABLE = False
    logging.warning("Screen capture dependencies not available. Install with: pip install mss opencv-python-headless pillow pytesseract")

logger = logging.getLogger(__name__)

@dataclass
class ScreenRegion:
    """Represents a region of the screen with coordinates and dimensions."""
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    
    @property
    def rect(self) -> QRect:
        """Convert to QRect."""
        return QRect(self.x, self.y, self.width, self.height)
    
    @classmethod
    def from_rect(cls, rect: QRect) -> 'ScreenRegion':
        """Create from QRect."""
        return cls(rect.x(), rect.y(), rect.width(), rect.height())
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }

class ScreenCapture(QObject):
    """Handles screen capture and manipulation functionality."""
    capture_completed = pyqtSignal(QPixmap, dict)  # pixmap, metadata
    error_occurred = pyqtSignal(str)  # error message
    
    def __init__(self, parent: Optional[QObject] = None):
        """Initialize the screen capture utility."""
        super().__init__(parent)
        self.sct = None
        self.last_capture: Optional[QPixmap] = None
        self.last_region: Optional[ScreenRegion] = None
        
        if SCREEN_CAPTURE_AVAILABLE:
            try:
                self.sct = mss.mss()
                logger.info("Screen capture initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize screen capture: {e}")
        else:
            logger.warning("Screen capture dependencies not available")
    
    def capture_screen(self, region: Optional[ScreenRegion] = None) -> Optional[QPixmap]:
        """
        Capture a screenshot of the specified region or entire screen.
        
        Args:
            region: Optional ScreenRegion to capture. If None, captures entire screen.
            
        Returns:
            QPixmap of the captured screen or None if failed.
        """
        try:
            if not SCREEN_CAPTURE_AVAILABLE:
                self.error_occurred.emit("Screen capture dependencies not available")
                return None
            
            if region is None:
                # Capture primary screen
                screen = QGuiApplication.primaryScreen()
                if screen is None:
                    raise RuntimeError("Could not get primary screen")
                
                screenshot = screen.grabWindow(0)
                region = ScreenRegion(0, 0, screenshot.width(), screenshot.height())
            else:
                # Capture specific region using mss for better performance
                monitor = {
                    "top": region.y,
                    "left": region.x,
                    "width": region.width,
                    "height": region.height,
                }
                
                # Capture with mss and convert to QPixmap
                with mss.mss() as sct:
                    sct_img = sct.grab(monitor)
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    qim = ImageQt.ImageQt(img)
                    screenshot = QPixmap.fromImage(qim)
            
            self.last_capture = screenshot
            self.last_region = region
            
            # Emit signal with capture data
            metadata = {
                'region': region.to_dict() if region else None,
                'timestamp': QDateTime.currentDateTime().toString(Qt.DateFormat.ISODate),
                'size': f"{screenshot.width()}x{screenshot.height()}"
            }
            self.capture_completed.emit(screenshot, metadata)
            
            return screenshot
            
        except Exception as e:
            error_msg = f"Screen capture failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return None
    
    def capture_active_window(self) -> Optional[QPixmap]:
        """Capture the currently active window."""
        try:
            # This is a placeholder - implementation depends on platform
            # On Windows, we can use win32gui
            if os.name == 'nt':
                import win32gui
                import win32ui
                import win32con
                
                window = win32gui.GetForegroundWindow()
                rect = win32gui.GetWindowRect(window)
                
                # Create region from window rect
                region = ScreenRegion(
                    rect[0], rect[1],
                    rect[2] - rect[0],
                    rect[3] - rect[1]
                )
                
                return self.capture_screen(region)
            else:
                # Fallback to primary screen on other platforms
                return self.capture_screen()
                
        except Exception as e:
            error_msg = f"Failed to capture active window: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return None
    
    def save_screenshot(self, filepath: str, pixmap: Optional[QPixmap] = None) -> bool:
        """
        Save screenshot to file.
        
        Args:
            filepath: Path to save the screenshot
            pixmap: Optional pixmap to save. If None, uses last capture.
            
        Returns:
            bool: True if save was successful, False otherwise.
        """
        try:
            target = pixmap if pixmap is not None else self.last_capture
            if target is None:
                raise ValueError("No screenshot available to save")
                
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            
            # Save with appropriate format based on extension
            if filepath.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                return target.save(filepath)
            else:
                # Default to PNG if extension not recognized
                return target.save(filepath + '.png', 'PNG')
                
        except Exception as e:
            error_msg = f"Failed to save screenshot: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return False
    
    def ocr_text(self, pixmap: Optional[QPixmap] = None) -> str:
        """
        Extract text from a screenshot using OCR.
        
        Args:
            pixmap: Optional pixmap to process. If None, uses last capture.
            
        Returns:
            Extracted text as string.
        """
        try:
            if not SCREEN_CAPTURE_AVAILABLE:
                raise RuntimeError("OCR dependencies not available")
                
            target = pixmap if pixmap is not None else self.last_capture
            if target is None:
                raise ValueError("No screenshot available for OCR")
                
            # Convert QPixmap to PIL Image
            qimage = target.toImage()
            width, height = qimage.width(), qimage.height()
            
            # Convert to format suitable for OpenCV
            ptr = qimage.constBits()
            ptr.setsize(height * width * 4)
            arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
            
            # Convert to RGB (OpenCV uses BGR by default)
            rgb_image = cv2.cvtColor(arr, cv2.COLOR_BGRA2RGB)
            
            # Use Tesseract to do OCR on the image
            text = pytesseract.image_to_string(rgb_image)
            
            return text.strip()
            
        except Exception as e:
            error_msg = f"OCR failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return ""

# Example usage
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QLabel
    
    app = QApplication(sys.argv)
    
    # Create and configure screen capture
    screen_capture = ScreenCapture()
    
    # Example: Capture screen and display in a label
    def on_capture_complete(pixmap, metadata):
        print(f"Capture complete! Size: {metadata['size']}")
        
        # Create a simple window to display the capture
        window = QWidget()
        window.setWindowTitle("Screen Capture Preview")
        window.resize(800, 600)
        
        label = QLabel(window)
        label.setPixmap(pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio))
        
        # Save the screenshot
        save_path = os.path.join(os.path.expanduser("~"), "screenshot.png")
        if screen_capture.save_screenshot(save_path, pixmap):
            print(f"Screenshot saved to: {save_path}")
        
        # Extract text using OCR
        text = screen_capture.ocr_text(pixmap)
        if text:
            print("\nExtracted Text:")
            print("-" * 40)
            print(text)
            print("-" * 40)
        
        window.show()
    
    # Connect signals
    screen_capture.capture_completed.connect(on_capture_complete)
    
    # Capture the screen after a short delay
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(1000, screen_capture.capture_screen)
    
    sys.exit(app.exec())
