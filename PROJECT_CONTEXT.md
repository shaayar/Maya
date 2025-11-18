# Maya AI Chatbot - Project Context

## Project Overview
Maya is a modern, modular AI chatbot interface built with Python and PyQt6. It provides a feature-rich desktop application for interacting with AI models, with a focus on accessibility and user experience.

## Core Features
- **Modern UI**: Clean, responsive interface with smooth animations
- **Modular Design**: Extensible architecture with separate modules for different functionalities
- **AI Integration**: Supports various AI models through the Model Control Protocol (MCP)
- **Voice Control**: Built-in voice commands and wake word detection
- **To-Do List**: Integrated task management system
- **Screen Capture & OCR**: Built-in screen capture and text recognition
- **Theming**: Support for dark/light themes
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Technical Stack
- **Frontend**: PyQt6 for the desktop interface
- **AI Integration**: Groq SDK for AI model interaction
- **Voice Processing**: pyttsx3 and SpeechRecognition
- **Image Processing**: OpenCV, Tesseract OCR
- **Build System**: Custom build.py script
- **Containerization**: Docker support available

## Project Structure
```
Maya/
├── .dockerignore
├── .env
├── .gitignore
├── Dockerfile
├── README.md
├── FEATURES.md
├── INSTALL.md
├── USER_GUIDE.md
├── RELEASE_NOTES.md
├── main.py                 # Application entry point
├── config.json             # Main configuration
├── requirements.txt        # Python dependencies
├── build.py                # Build script
├── maya_web_interface/     # Web interface components
├── modules/                # Core application modules
│   ├── __init__.py
│   ├── chatbot.py          # Main chatbot logic
│   ├── gui.py              # Main GUI components
│   ├── voice.py            # Voice command processing
│   ├── todo.py             # To-do list functionality
│   ├── mcp_client.py       # Model Control Protocol client
│   └── ... (other modules)
├── themes/                 # UI themes
└── tests/                  # Test files
```

## Dependencies
- Python 3.8+
- PyQt6
- Groq SDK
- Various Python packages (see requirements.txt)
- Tesseract OCR for text recognition
- System audio for voice features

## Development Setup
1. Clone the repository
2. Install Python 3.8 or higher
3. Install Tesseract OCR
4. Install Python dependencies: `pip install -r requirements.txt`
5. Run with: `python main.py`

## Recent Updates
- Added Model Control Protocol (MCP) support
- Enhanced voice command system
- Improved UI/UX with theming support
- Added screen capture and OCR capabilities
- Integrated to-do list management

## Known Issues
- Screen reader support is currently disabled (planned for future release)
- Some voice features may require additional system configuration

## Future Roadmap
- [ ] Implement screen reader support
- [ ] Add more AI model integrations
- [ ] Enhance accessibility features
- [ ] Expand test coverage
- [ ] Add plugin system for extensibility

## Contact
- **Developer**: Shubham Dave
- **GitHub**: [shaayar](https://github.com/shaayar)

## License
MIT License (see LICENSE file)
