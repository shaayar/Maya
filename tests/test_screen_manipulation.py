"""Tests for the screen manipulation module."""
import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add the modules directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.screen_manipulation import ScreenRegion, ScreenCapture
from PyQt6.QtGui import QPixmap, QImage

class TestScreenRegion:
    """Tests for the ScreenRegion class."""
    
    def test_initialization(self):
        """Test ScreenRegion initialization with default values."""
        region = ScreenRegion()
        assert region.x == 0
        assert region.y == 0
        assert region.width == 0
        assert region.height == 0
    
    def test_initialization_with_values(self):
        """Test ScreenRegion initialization with specific values."""
        region = ScreenRegion(10, 20, 100, 200)
        assert region.x == 10
        assert region.y == 20
        assert region.width == 100
        assert region.height == 200
    
    def test_rect_property(self):
        """Test the rect property returns a QRect with correct values."""
        region = ScreenRegion(10, 20, 100, 200)
        rect = region.rect
        assert rect.x() == 10
        assert rect.y() == 20
        assert rect.width() == 100
        assert rect.height() == 200
    
    def test_from_rect_classmethod(self):
        """Test creating a ScreenRegion from a QRect."""
        from PyQt6.QtCore import QRect
        qrect = QRect(10, 20, 100, 200)
        region = ScreenRegion.from_rect(qrect)
        assert region.x == 10
        assert region.y == 20
        assert region.width == 100
        assert region.height == 200
    
    def test_to_dict(self):
        """Test converting ScreenRegion to dictionary."""
        region = ScreenRegion(10, 20, 100, 200)
        region_dict = region.to_dict()
        assert region_dict == {
            'x': 10,
            'y': 20,
            'width': 100,
            'height': 200
        }

class TestScreenCapture:
    """Tests for the ScreenCapture class."""
    
    @pytest.fixture
    def screen_capture(self, qtbot):
        """Fixture that provides a ScreenCapture instance for testing."""
        with patch('modules.screen_manipulation.SCREEN_CAPTURE_AVAILABLE', True):
            with patch('modules.screen_manipulation.mss.mss') as mock_mss:
                # Create a mock for the mss instance
                mock_mss.return_value = MagicMock()
                capture = ScreenCapture()
                yield capture
                # Cleanup if needed
                if hasattr(capture, 'sct') and capture.sct:
                    capture.sct.close()
    
    def test_initialization(self, screen_capture):
        """Test ScreenCapture initialization."""
        assert screen_capture.sct is not None
        assert screen_capture.last_capture is None
        assert screen_capture.last_region is None
    
    @patch('modules.screen_manipulation.QPixmap.fromImage')
    @patch('PyQt6.QtGui.QImage.fromData')
    @patch('modules.screen_manipulation.mss.mss')
    def test_capture_screen(self, mock_mss, mock_from_data, mock_from_pixmap, screen_capture, qtbot):
        """Test capturing the screen."""
        # Setup mocks
        mock_sct = MagicMock()
        mock_monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
        mock_sct.monitors = [mock_monitor]
        mock_sct.grab.return_value = MagicMock()
        mock_sct.grab.return_value.rgb = b'\x00' * (1920 * 1080 * 3)  # Mock RGB data
        mock_mss.return_value = mock_sct
        
        # Mock QImage.fromData
        mock_image = MagicMock(spec=QImage)
        mock_from_data.return_value = mock_image
        
        # Mock QPixmap.fromImage
        mock_pixmap = MagicMock(spec=QPixmap)
        mock_from_pixmap.return_value = mock_pixmap
        
        # Connect to the signal
        with qtbot.waitSignal(screen_capture.capture_completed, timeout=1000) as blocker:
            # Test capturing the entire screen
            result = screen_capture.capture_screen()
            
            # Verify the result
            assert result is not None
            assert screen_capture.last_capture is not None
            assert screen_capture.last_region is not None
            
        # Verify the signal was emitted with the correct arguments
        assert blocker.args == [mock_pixmap, mock_monitor]
    
    @patch('modules.screen_manipulation.QPixmap.fromImage')
    @patch('PyQt6.QtGui.QImage.fromData')
    @patch('modules.screen_manipulation.mss.mss')
    def test_capture_region(self, mock_mss, mock_from_data, mock_from_pixmap, screen_capture, qtbot):
        """Test capturing a specific region of the screen."""
        # Setup mocks
        mock_sct = MagicMock()
        mock_sct.grab.return_value = MagicMock()
        mock_sct.grab.return_value.rgb = b'\x00' * (100 * 100 * 3)  # Mock RGB data for 100x100 region
        mock_mss.return_value = mock_sct
        
        # Mock QImage.fromData
        mock_image = MagicMock(spec=QImage)
        mock_from_data.return_value = mock_image
        
        # Mock QPixmap.fromImage
        mock_pixmap = MagicMock(spec=QPixmap)
        mock_from_pixmap.return_value = mock_pixmap
        
        # Create a test region
        region = ScreenRegion(10, 20, 100, 100)
        
        # Connect to the signal
        with qtbot.waitSignal(screen_capture.capture_completed, timeout=1000):
            # Test capturing the region
            result = screen_capture.capture_screen(region)
            
            # Verify the result
            assert result is not None
            assert screen_capture.last_capture is not None
            assert screen_capture.last_region == region
            
            # Verify the mss.grab was called with the correct region
            mock_sct.grab.assert_called_once_with({
                'top': region.y,
                'left': region.x,
                'width': region.width,
                'height': region.height,
                'mon': 1  # Default monitor
            })
    
    @patch('modules.screen_manipulation.os.path.exists')
    @patch('modules.screen_manipulation.QPixmap.save')
    def test_save_screenshot(self, mock_save, mock_exists, screen_capture):
        """Test saving a screenshot to a file."""
        # Setup mocks
        mock_exists.return_value = True
        mock_save.return_value = True
        
        # Create a mock pixmap
        mock_pixmap = MagicMock(spec=QPixmap)
        
        # Test saving the screenshot
        result = screen_capture.save_screenshot('test.png', mock_pixmap)
        
        # Verify the result
        assert result is True
        mock_save.assert_called_once_with('test.png')
    
    @patch('modules.screen_manipulation.pytesseract')
    @patch('modules.screen_manipulation.cv2')
    def test_ocr_text(self, mock_cv2, mock_pytesseract, screen_capture):
        """Test extracting text from a screenshot using OCR."""
        # Setup mocks
        mock_pytesseract.image_to_string.return_value = 'Test text'
        
        # Create a mock pixmap
        mock_pixmap = MagicMock(spec=QPixmap)
        mock_image = MagicMock()
        mock_pixmap.toImage.return_value = mock_image
        
        # Mock QImage to numpy array conversion
        mock_image.bits.return_value = b'\x00' * (100 * 100 * 4)  # Mock RGBA data
        mock_image.width.return_value = 100
        mock_image.height.return_value = 100
        mock_image.bytesPerLine.return_value = 100 * 4
        mock_image.format.return_value = QImage.Format.Format_RGBA8888
        
        # Test OCR
        result = screen_capture.ocr_text(mock_pixmap)
        
        # Verify the result
        assert result == 'Test text'
        mock_pytesseract.image_to_string.assert_called_once()

# Run the tests
if __name__ == '__main__':
    pytest.main(['-v', __file__])
