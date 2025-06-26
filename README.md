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
- **Feature Roadmap**: Clear visibility into upcoming features and improvements

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/maya-ai-chatbot.git
   cd maya-ai-chatbot
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Create a `.env` file in the project root
   - Add your Groq API key:
     ```
     GROQ_API_KEY=your_api_key_here
     ```

### Resources

MAYA loads all resources (icons, images, etc.) directly from the filesystem. The application looks for resources in the following locations:

- Icons: `resources/icons/`
  - `mic_on.png` - Microphone icon (active)
  - `mic_off.png` - Microphone icon (inactive)
  - `app_icon.png` - Application icon

You can customize these icons by replacing the files in the respective directories. The application will automatically detect and use the new files without requiring a rebuild.

### Running the Application

```bash
python main.py
```

## 🛠️ Configuration

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

### Project Structure

```
maya-ai-chatbot/
├── modules/               # Application modules
│   ├── __init__.py
│   ├── chatbot.py         # Chatbot logic
│   ├── config.py          # Configuration loader
│   ├── gui.py             # Main GUI application
│   ├── settings_dialog.py # Settings UI
│   └── styles.py          # UI styles and themes
├── resources/             # Application resources (icons, etc.)
│   └── icons/             # Application icons
├── .env                   # Environment variables
├── config.json            # Application configuration
├── main.py                # Entry point
└── requirements.txt       # Dependencies
```

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