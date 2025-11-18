<div align="center">
  <h1>MAYA AI Chatbot</h1>
  <p>A modern, modular AI chatbot interface built with Python and PyQt6</p>
  
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)](https://pypi.org/project/PyQt6/)
</div>

## 🌟 Features

- **Modern UI**: Clean, responsive interface with smooth animations
- **Modular Design**: Easy to extend and customize
- **Web Search**: Built-in web search functionality
- **Chat Management**: Save, load, and clear conversations
- **Dark/Light Theme**: Built-in theme support
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **To-Do List**: Integrated task management with categories, priorities, and reminders
- **Voice Commands**: Control the app using voice commands with wake word detection
- **Customizable AI**: Configure AI model and behavior through settings
- **Model Control Protocol (MCP)**: Connect to MCP-compatible AI models for enhanced capabilities
- **Feature Roadmap**: Clear visibility into upcoming features and improvements
- **Accessibility**: Basic keyboard navigation and text size adjustment (Note: Screen reader support is currently disabled but planned for a future release)

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR (for text recognition)
- Microphone (for voice features)

## 🐳 Docker Installation (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- X11 server (for GUI on Linux/Windows/macOS)
- Audio system (for voice features)

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/maya-chatbot.git
   cd maya-chatbot
   ```

2. Build and run with Docker Compose:
   ```bash
   # Allow local connections to X server (Linux/macOS)
   xhost +local:docker
   
   # Build and start the container
   docker-compose up --build
   ```

3. On first run, the application will create necessary configuration files in the mounted volumes.

### Windows Users

1. Install X11 server (e.g., VcXsrv or X410)
2. Run these commands in PowerShell:
   ```powershell
   # Allow connections from Docker
   Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Ranges" -Name "172.16.0.0" -Type DWord -Value 0x21
   
   # Set display environment variable (update IP if needed)
   $env:DISPLAY = "host.docker.internal:0.0"
   
   # Build and run
   docker-compose up --build
   ```

### Volume Mounts
- `./resources` - Application resources (themes, icons, etc.)
- `maya-config` - Persistent configuration (Docker volume)
- `maya-data` - Application data (Docker volume)

## 🔌 MCP Integration

MAYA supports integration with Model Control Protocol (MCP) compatible AI models. This allows you to connect to various AI providers and leverage their capabilities directly within the application.

### Configuration

1. Open the settings dialog (⚙️) and navigate to the "MCP" tab
2. Configure the following settings:
   - **MCP Endpoint**: URL of your MCP-compatible server (e.g., `http://localhost:8000`)
   - **API Key**: Your authentication token (if required)
   - **Default Model**: Preferred model to use for responses
   - **Temperature**: Controls randomness in responses (0.0 to 1.0)
   - **Max Tokens**: Maximum length of generated responses

### Usage

1. Ensure your MCP server is running and accessible
2. Configure the MCP settings as described above
3. Start a new chat or continue an existing one
4. Your messages will be sent to the configured MCP endpoint
5. Responses will be streamed in real-time as they're generated

### Troubleshooting

- **Connection Issues**: Verify the MCP endpoint URL and ensure the server is running
- **Authentication Errors**: Double-check your API key and permissions
- **Slow Responses**: Try reducing the max tokens or check server load
- **Formatting Issues**: Ensure your MCP server follows the expected response format

## 🚀 Manual Installation

### Prerequisites
- Python 3.8 or higher
- Tesseract OCR (for text recognition)
- PortAudio (for voice features)
- System dependencies (see Dockerfile for reference)

### Using pip
```bash
# Clone the repository
git clone https://github.com/yourusername/maya-chatbot.git
cd maya-chatbot

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
python main.py
```

## 🔧 Configuration

### Docker Configuration

Edit `docker-compose.yml` to customize:
- Volume mounts
- Environment variables
- Device passthrough (for audio/video)

Example environment variables:
```yaml
environment:
  - DISPLAY=${DISPLAY}
  - PYTHONUNBUFFERED=1
  - ENABLE_VOICE=true
```

### Application Configuration

Edit the `config.json` file to customize application settings. Here's the default configuration with all available options:

```json
{
    "model": "llama-3.3-70b-versatile",
    "max_tokens": 2000,
    "max_messages": 20,
    "temperature": 0.7,
    "messages": [
        {
            "role": "system",
            "content": "You are MAYA, a helpful AI assistant. Keep your responses concise and to the point."
        }
    ]
}
```

### Configuration Options

- `model`: The AI model to use for generating responses (default: "llama-3.3-70b-versatile")
- `max_tokens`: Maximum number of tokens in the AI's response (default: 2000)
- `max_messages`: Maximum number of messages to keep in conversation history (default: 20)
- `temperature`: Controls randomness in AI responses (0.0 to 1.0, default: 0.7)
- `messages`: List of system messages that define the AI's behavior and personality

## 🔍 Troubleshooting

### Common Issues

#### No Display in Docker
```bash
# On Linux/macOS
export DISPLAY=:0
xhost +local:docker

# On Windows
# Make sure X server is running and accessible
```

#### Audio Not Working
- Ensure PulseAudio is running (Linux)
- Check Docker has access to audio devices
- Verify volume levels and default audio device

#### Performance Issues
- Allocate more resources to Docker
- Disable unused features in settings
- Check system resource usage

## 📝 To-Do List Features

The integrated To-Do List helps you manage tasks with the following features:

- Create, edit, and delete tasks
- Set due dates and reminders
- Categorize tasks (Work, Personal, Shopping, etc.)
- Set task priorities (High, Medium, Low)
- Mark tasks as complete
- Filter and search tasks
- Sort tasks by priority, due date, or title
- Get notifications for upcoming tasks

### Keyboard Shortcuts

- `Ctrl+N`: Add new task
- `Delete`: Delete selected task
- `Space`: Toggle task completion
- `Ctrl+F`: Focus search box
- `Esc`: Clear search/filter

## 🎙️ Voice Commands

MAYA supports voice interaction with the following features:

- Wake word: "Hey Maya" to activate voice commands
- Voice-controlled task management
- Speech-to-text for chat input
- Configurable voice settings
- Visual feedback for voice activity

## 🖥️ User Interface

![MAYA Chatbot Interface](screenshots/interface.png)

### Main Components

1. **Chat Display**: Shows the conversation history
2. **Input Box**: Type your messages here
3. **Action Buttons**:
   - Send: Send your message
   - Save Chat: Save the current conversation
   - Open File: Load a saved conversation
   - Clear Chat: Start a new conversation
   - Web Search: Perform a web search
   - Microphone: Enable voice input
4. **To-Do List Panel**: Manage your tasks (toggle with View > To-Do List)
5. **Status Bar**: Shows connection status and active features

## 📚 Documentation

For a complete list of features, planned enhancements, and the development roadmap, check out our [Feature Roadmap](FEATURES.md).

## 🏗️ Project Structure

```
Maya/
│
├── maya_web_interface/       # Web interface components
│   ├── static/              # Static files (CSS, JS, images)
│   │   ├── css/            
│   │   │   ├── src/        # Source CSS with Tailwind directives
│   │   │   │   └── styles.css
│   │   │   └── styles.css  # Compiled CSS output
│   │   │
│   │   ├── js/             # JavaScript files
│   │   │   ├── app.js      # Main application logic
│   │   │   ├── api.js      # API communication
│   │   │   └── animations.js # GSAP animations
│   │   │
│   │   └── icons/          # Application icons
│   │
│   ├── templates/          # HTML templates
│   │   ├── index.html      # Main application interface
│   │   ├── 404.html        # 404 error page
│   │   └── 500.html        # 500 error page
│   │
│   ├── __init__.py         # Package initialization
│   ├── app.py              # Flask application
│   └── server.py           # Server configuration
│
├── modules/                # Core application modules
│   ├── __init__.py
│   ├── todo_manager.py     # To-do list functionality
│   ├── voice_assistant.py  # Voice command processing
│   ├── mcp_client.py       # Model Control Protocol client
│   └── mcp_settings.py     # MCP configuration
│
├── resources/              # Application resources
│   ├── icons/             # Application icons
│   ├── sounds/            # Sound effects
│   └── themes/            # UI themes
│
├── tests/                  # Test files
│   └── test_todo.py       # Unit tests
│
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── package.json           # Node.js dependencies
├── package-lock.json      # Lock file for npm
├── postcss.config.cjs     # PostCSS configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── requirements.txt       # Python dependencies
└── Dockerfile             # Docker configuration
```

### Key Files

- `maya_web_interface/app.py`: Main Flask application entry point
- `maya_web_interface/static/js/app.js`: Frontend application logic
- `maya_web_interface/static/css/src/styles.css`: Source CSS with Tailwind directives
- `tailwind.config.js`: Tailwind CSS configuration with custom theme
- `postcss.config.cjs`: PostCSS configuration for processing CSS
- `package.json`: Node.js project configuration and scripts

### Customization

#### Themes

Edit the `styles.py` file to customize the application's appearance:

```python
# Example theme customization
DARK_THEME = """
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}
"""
```

## 🧩 Module Usage

This section explains how to access and use different modules in the MAYA AI Chatbot codebase.

### Core Modules

#### 1. File Operations (`file_manager.py`, `file_operations.py`)
```python
# Import
from modules.file_manager import FileManager

# Initialize
file_manager = FileManager()

# Create a file
file_manager.create_file("example.txt", "Content")

# Read a file
content = file_manager.read_file("example.txt")
# Search files
results = file_manager.search_files("*.py", "/path/to/search")
```

#### 2. Voice Assistant (`voice.py`, `speech_recognition.py`)
```python
# From main GUI
self.voice_assistant.toggle_listening()  # Toggle voice input
self.voice_assistant.speak("Hello")     # Text-to-speech

# Check status
if self.voice_assistant.is_listening:
    print("Voice is active")

# Handle speech recognition
self.voice_assistant.speech_recognized.connect(self.handle_speech)
```

#### 3. Screen Reader (`screen_reader.py`)
```python
# Enable/disable
self.screen_reader.set_enabled(True)

# Speak text
self.screen_reader.speak("Screen reader is active")

# Check status
if self.screen_reader.is_enabled():
    print("Screen reader is on")
```

#### 4. Chatbot (`chatbot.py`)
```python
# Send message and get response
response = self.chatbot.generate_response("Hello")

# Get conversation history
history = self.chatbot.get_conversation_history()

# Clear history
self.chatbot.clear_history()
```

### Utility Modules

#### 1. Configuration (`config.py`)
```python
from modules.config import load_config, save_config

# Load config
config = load_config()

# Get/set values
model = config.get('model', 'default_model')
config['new_setting'] = 'value'

# Save changes
save_config(config)
```

#### 2. Web Browser (`web_browser.py`)
```python
from modules.web_browser import WebBrowser

browser = WebBrowser()
browser.open_url("https://example.com")
title = browser.get_page_title()
```

### Common Patterns

#### Sending Messages
```python
# Get input
message = self.input_box.toPlainText().strip()
if message:
    # Clear input
    self.input_box.clear()
    # Display in chat
    self.chat_display.append(f"You: {message}")
    # Process and get response
    response = self.chatbot.generate_response(message)
    self.chat_display.append(f"MAYA: {response}")
```

#### Error Handling
```python
try:
    # Operation that might fail
    result = self.file_manager.read_file("important.txt")
except Exception as e:
    # Show error to user
    self.statusBar().showMessage(f"Error: {str(e)}", 5000)
    # Speak error if screen reader is active
    if hasattr(self, 'screen_reader') and self.screen_reader.is_enabled():
        self.screen_reader.speak(f"Error: {str(e)}")
```

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Send Message | `Ctrl+Return` |
| Save Chat | `Ctrl+S` |
| Open File | `Ctrl+O` |
| Clear Chat | `Ctrl+L` |
| Web Search | `Ctrl+W` |
| Toggle Screen Reader | `Ctrl+Alt+R` |
| Read Current Element | `Ctrl+Alt+C` |
| Increase Text Size | `Ctrl++` |
| Decrease Text Size | `Ctrl+-` |
| Reset Text Size | `Ctrl+0` |

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - For the GUI framework
- [Groq](https://groq.com/) - For the AI API
- All contributors who have helped improve this project

---

<div align="center">
  Made with ❤️ by [Shubham Dave](https://github.com/shaayar)
</div>