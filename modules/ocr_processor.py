"""
OCR (Optical Character Recognition) Processor for MAYA AI Chatbot.
Provides functionality to extract text from images using Tesseract OCR.
"""
import logging
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

logger = logging.getLogger(__name__)

class OCRProcessor:
    """Handles OCR (Optical Character Recognition) operations on images."""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """Initialize the OCR processor.
        
        Args:
            tesseract_path: Optional path to the Tesseract executable.
                           If not provided, the system PATH will be used.
        """
        self.tesseract_path = tesseract_path
        if self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        
        # Default OCR configuration
        self.default_config = {
            'lang': 'eng',
            'config': '--oem 3 --psm 6',  # OEM 3 = Default OCR engine, PSM 6 = Assume a single uniform block of text
            'preprocess': True,  # Enable image preprocessing by default
            'contrast_factor': 1.5,  # Increase contrast
            'sharpen': True,  # Apply sharpening
            'denoise': True,  # Apply denoising
            'threshold': True,  # Apply thresholding
            'dpi': 300  # Default DPI for better recognition
        }
    
    def preprocess_image(self, image: Image.Image, config: Dict[str, Any]) -> Image.Image:
        """Preprocess the image to improve OCR accuracy.
        
        Args:
            image: Input PIL Image
            config: Configuration dictionary
            
        Returns:
            Preprocessed PIL Image
        """
        if not config.get('preprocess', True):
            return image
        
        # Convert to grayscale
        img = image.convert('L')
        
        # Convert to numpy array for OpenCV processing
        img_np = np.array(img)
        
        # Apply denoising
        if config.get('denoise', True):
            img_np = cv2.fastNlMeansDenoising(img_np, None, h=10, templateWindowSize=7, searchWindowSize=21)
        
        # Apply adaptive thresholding
        if config.get('threshold', True):
            img_np = cv2.adaptiveThreshold(
                img_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
        
        # Convert back to PIL Image
        img = Image.fromarray(img_np)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(config.get('contrast_factor', 1.5))
        
        # Sharpen the image
        if config.get('sharpen', True):
            img = img.filter(ImageFilter.SHARPEN)
        
        return img
    
    def extract_text(self, image: Image.Image, config: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
        """Extract text from an image using OCR.
        
        Args:
            image: PIL Image containing text to recognize
            config: Optional configuration dictionary. If None, default settings are used.
                   Possible keys: lang, config, preprocess, contrast_factor, sharpen, denoise, threshold, dpi
                   
        Returns:
            Tuple of (extracted_text, metadata)
        """
        if config is None:
            config = {}
        
        # Merge with default config
        merged_config = {**self.default_config, **config}
        
        # Preprocess the image
        processed_img = self.preprocess_image(image, merged_config)
        
        # Create a temporary file for debugging if needed
        debug = config.get('debug', False)
        if debug:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                processed_img.save(tmp.name)
                logger.debug(f"Saved preprocessed image to {tmp.name}")
        
        try:
            # Set DPI if specified
            dpi = merged_config.get('dpi')
            if dpi:
                processed_img.info['dpi'] = (dpi, dpi)
            
            # Perform OCR
            text = pytesseract.image_to_string(
                processed_img,
                lang=merged_config.get('lang'),
                config=merged_config.get('config', '')
            )
            
            # Get additional data if needed
            data = pytesseract.image_to_data(
                processed_img,
                lang=merged_config.get('lang'),
                config=merged_config.get('config', ''),
                output_type=pytesseract.Output.DICT
            )
            
            # Prepare metadata
            metadata = {
                'confidence': float(np.mean([float(x) for x in data['conf'] if float(x) > 0])) if data['conf'] else 0.0,
                'word_count': len(data['text']),
                'config': merged_config
            }
            
            return text.strip(), metadata
            
        except Exception as e:
            logger.error(f"Error during OCR processing: {str(e)}")
            return "", {'error': str(e), 'config': merged_config}
    
    def extract_text_from_region(self, image: Image.Image, region: Tuple[int, int, int, int], 
                               config: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
        """Extract text from a specific region of an image.
        
        Args:
            image: PIL Image
            region: Tuple of (left, top, right, bottom) coordinates
            config: Optional configuration dictionary
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        # Crop the image to the specified region
        cropped = image.crop(region)
        return self.extract_text(cropped, config)
    
    def get_available_languages(self) -> list:
        """Get a list of available Tesseract languages.
        
        Returns:
            List of language codes (e.g., ['eng', 'fra', 'spa'])
        """
        try:
            langs = pytesseract.get_languages(config='')
            return langs
        except Exception as e:
            logger.error(f"Error getting available languages: {str(e)}")
            return ['eng']  # Default to English if there's an error


def install_tesseract_windows():
    """Provide instructions for installing Tesseract OCR on Windows."""
    return """
    To install Tesseract OCR on Windows:
    
    1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
    2. Run the installer (e.g., tesseract-ocr-w64-setup-5.3.0.20221222.exe)
    3. During installation, make sure to check "Add to PATH"
    4. After installation, restart your terminal/IDE
    5. Verify installation by running in command prompt: tesseract --version
    6. Install additional language packs if needed
    
    Note: You may need to set the path to tesseract.exe in the application settings.
    """


def install_tesseract_macos():
    """Provide instructions for installing Tesseract OCR on macOS."""
    return """
    To install Tesseract OCR on macOS:
    
    1. Install Homebrew if you don't have it:
       /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    2. Install Tesseract:
       brew install tesseract
    
    3. Install language data (optional):
       brew install tesseract-lang
    
    4. Verify installation:
       tesseract --version
    
    Note: The path to tesseract should be automatically detected.
    """


def install_tesseract_linux():
    """Provide instructions for installing Tesseract OCR on Linux."""
    return """
    To install Tesseract OCR on Linux:
    
    For Debian/Ubuntu:
    sudo apt update
    sudo apt install tesseract-ocr
    
    For additional languages (e.g., Spanish, French):
    sudo apt install tesseract-ocr-eng tesseract-ocr-spa tesseract-ocr-fra
    
    For Fedora:
    sudo dnf install tesseract
    
    For Arch Linux:
    sudo pacman -S tesseract tesseract-data-eng
    
    Verify installation:
    tesseract --version
    """
