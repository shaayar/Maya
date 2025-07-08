# MAYA AI Chatbot - Installation Guide

This guide provides step-by-step instructions for installing and setting up MAYA AI Chatbot on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for development installations)

## Installation Methods

### Method 1: Using pip (Recommended)

1. **Clone the repository** (or download the source code):
   ```bash
   git clone https://github.com/shaayare/maya-ai.git
   cd maya-ai
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR** (required for text recognition):
   - **Windows**: Download and install from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt install tesseract-ocr` (Debian/Ubuntu) or `sudo dnf install tesseract` (Fedora)

5. **Set up environment variables**:
   Create a `.env` file in the project root with your API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

### Method 2: Using setup.py

1. **Install MAYA globally**:
   ```bash
   python setup.py install
   ```

2. **Run MAYA**:
   ```bash
   maya-ai
   ```

## Platform-Specific Instructions

### Windows
1. Install Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. During installation, make sure to check "Add Python to PATH"
3. Open Command Prompt and follow the installation steps above

### macOS
1. Install Homebrew if not already installed:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python 3:
   ```bash
   brew install python
   ```
3. Follow the general installation steps above

### Linux (Ubuntu/Debian)
1. Update package list and install Python 3:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```
2. Follow the general installation steps above

## Running MAYA

1. **From source**:
   ```bash
   python main.py
   ```

2. **After installation**:
   ```bash
   maya-ai
   ```

## Troubleshooting

### Common Issues

#### Voice Recognition Not Working
- Ensure your microphone is properly connected and enabled
- Check if PyAudio is installed correctly
- On Linux, you might need to install `portaudio19-dev`:
  ```bash
  sudo apt install portaudio19-dev
  ```

#### Tesseract Not Found
- Make sure Tesseract is installed and added to your system PATH
- On Windows, the default installation path is `C:\Program Files\Tesseract-OCR\tesseract.exe`

#### Missing Dependencies
If you encounter missing module errors, try:
```bash
pip install -r requirements.txt --upgrade
```

## Updating MAYA

To update to the latest version:

1. **If installed via Git**:
   ```bash
   git pull origin main
   pip install -r requirements.txt --upgrade
   ```

2. **If installed via pip**:
   ```bash
   pip install --upgrade maya-ai
   ```

## Uninstalling

To uninstall MAYA:

```bash
pip uninstall maya-ai
```

## Support

For additional help, please open an issue on our [GitHub repository](https://github.com/yourusername/maya-ai/issues).
