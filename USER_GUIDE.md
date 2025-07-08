# MAYA AI Assistant - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Voice Features](#voice-features)
3. [File Operations](#file-operations)
4. [VS Code Integration](#vs-code-integration)
5. [To-Do List](#to-do-list)
6. [Screen Capture](#screen-capture)
7. [Accessibility Features](#accessibility-features)
8. [Settings](#settings)
9. [Troubleshooting](#troubleshooting)

## Getting Started

### Launching MAYA
1. Ensure you have Python 3.8+ installed
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

### Basic Navigation
- **Chat Interface**: Type your message and press Enter to send
- **Menu Bar**: Access all features through the top menu
- **Status Bar**: View current status and notifications at the bottom

## Voice Control & Customization

MAYA's voice features allow for natural interaction through speech. You can customize the voice, speech rate, and wake word to suit your preferences.

### Basic Voice Commands
- **Enable/Disable Voice Control**: Go to **Settings** > **Voice** and toggle the switch
- **Wake Word**: Say "Hey MAYA" to activate voice commands (configurable)
- **Available Commands**:
  - "Search for [query]" - Perform a web search
  - "Open [file/folder]" - Open a file or folder
  - "Create a new file" - Create a new file
  - "Send message" - Send the current message
  - "Clear chat" - Clear the chat history

### Voice Customization

#### Changing the Voice
MAYA supports multiple system voices. To change the voice:
1. Go to **Settings** > **Voice Settings**
2. Select your preferred voice from the dropdown menu
3. Click "Save" to apply changes

#### Adjusting Speech Rate
Control how fast or slow MAYA speaks:
1. Go to **Settings** > **Voice Settings**
2. Use the slider to adjust the speech rate (100-300% of normal speed)
3. Click "Save" to apply changes

#### Customizing the Wake Word
To change the wake word from "Hey MAYA":
1. Open the configuration file (`config.json` in the application directory)
2. Locate the `wake_word` setting
3. Change it to your preferred phrase (e.g., "computer", "assistant")
4. Save the file and restart MAYA

### Voice Settings Persistence
Your voice settings are automatically saved and will persist between sessions. The following preferences are saved:
- Selected voice
- Speech rate
- Voice control enabled/disabled state
- Wake word (if changed in config)

### Troubleshooting Voice Issues

#### Voice Not Working
1. Check that your microphone is properly connected and enabled
2. Ensure MAYA has microphone permissions in your system settings
3. Try selecting a different input device in your system sound settings

#### Wake Word Not Detected
1. Speak clearly and at a normal volume
2. Reduce background noise
3. Ensure your microphone is not muted
4. Try moving closer to your microphone

#### Voice Sounds Robotic or Unnatural
1. Try selecting a different voice
2. Adjust the speech rate to a more natural speed
3. Ensure you have the latest audio drivers installed

### Advanced Voice Features

#### Voice Command Shortcuts
You can create custom voice command shortcuts:
1. Go to **Settings** > **Voice Shortcuts**
2. Click "Add Shortcut"
3. Enter the phrase to recognize and the action to perform
4. Click "Save"

#### Voice Profiles
MAYA supports multiple voice profiles for different users:
1. Go to **Settings** > **Voice Profiles**
2. Click "Create New Profile"
3. Configure voice and recognition settings
4. Switch between profiles as needed

#### Voice Training
For better recognition accuracy:
1. Go to **Settings** > **Voice Training**
2. Follow the on-screen instructions to read sample text
3. Repeat the process to improve recognition over time
3. Adjust speech rate using the slider
4. Click **Save**

## File Operations

### Opening Files
1. Click **File** > **Open** or press `Ctrl+O`
2. Navigate to your file and click **Open**

### Creating New Files
1. Click **File** > **New** or press `Ctrl+N`
2. Enter a filename with extension
3. The file will be created in your default documents folder

### Searching Files
1. Click **Edit** > **Find in Files** or press `Ctrl+Shift+F`
2. Enter your search term
3. Results will appear in a new panel

## VS Code Integration

MAYA provides seamless integration with Visual Studio Code, allowing you to work with your code directly from the chat interface.

### Requirements
- VS Code must be installed on your system
- The `code` command must be in your system PATH
  - On Windows: Add VS Code to your PATH during installation or add it manually
  - On macOS: Install the 'code' command in PATH from the Command Palette (Cmd+Shift+P > "Shell Command: Install 'code' command in PATH")
  - On Linux: The 'code' command should be available after installation

### Getting Started

#### Connecting to VS Code
1. Ensure VS Code is installed and the 'code' command is in your PATH
2. Open MAYA and go to **Tools** > **VS Code** > **Check Connection**
3. If successful, you'll see a confirmation message

### Features

#### Open Files in VS Code
1. Right-click any file in the file explorer
2. Select **Open in VS Code**
   - Or use the keyboard shortcut `Ctrl+Alt+O` (Windows/Linux) or `Cmd+Alt+O` (macOS)

#### Open Folders in VS Code
1. Right-click any folder in the file explorer
2. Select **Open Folder in VS Code**
   - This will open the folder as a workspace in VS Code

#### Command Palette Integration
1. Go to **Tools** > **VS Code** > **Command Palette** or press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
2. Start typing any VS Code command
3. Select the command from the dropdown
4. The command will be executed in the active VS Code window

#### Extension Management
1. Go to **Tools** > **VS Code** > **Manage Extensions**
2. In the extensions panel:
   - Search for extensions
   - Install/Uninstall extensions
   - Enable/Disable extensions
   - Update extensions

#### List Installed Extensions
1. Go to **Tools** > **VS Code** > **List Extensions**
2. A list of all installed extensions will be displayed
3. Click on any extension to view its details

### Advanced Usage

#### Keyboard Shortcuts
- `Ctrl+Alt+O` / `Cmd+Alt+O`: Open current file in VS Code
- `Ctrl+Shift+P` / `Cmd+Shift+P`: Open VS Code Command Palette
- `Ctrl+Shift+E` / `Cmd+Shift+E`: Open VS Code Explorer

#### Command Line Integration
MAYA can execute VS Code commands directly from the chat:
```
/vscode command [arguments]
```

Examples:
- Open a file: `/vscode open file.txt`
- Open a folder: `/vscode open-folder /path/to/folder`
- Run a command: `/vscode command workbench.action.terminal.new`

### Troubleshooting

#### VS Code Not Found
1. Ensure VS Code is installed
2. Verify the 'code' command is in your system PATH
3. Restart MAYA after installing VS Code

#### Command Not Working
1. Check if VS Code is running
2. Try restarting VS Code
3. Verify the command syntax is correct

#### Extension Installation Fails
1. Check your internet connection
2. Ensure you have write permissions for the VS Code extensions directory
3. Try installing the extension manually from VS Code

### Tips
- Use the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) to access all VS Code features
- You can open multiple files/folders in a single VS Code window
- Customize keyboard shortcuts in VS Code to match your workflow
- Use the integrated terminal in VS Code for running commands

### Features
- **Open File in VS Code**: Right-click any file and select "Open in VS Code"
- **Open Folder in VS Code**: Open entire project folders
- **Command Palette**: Access VS Code commands directly from MAYA
- **Extension Management**: Install and manage VS Code extensions

## To-Do List

### Adding Tasks
1. Click **View** > **Show To-Do List**
2. Click the **+** button
3. Enter task details and set a due date if needed
4. Click **Add**

### Managing Tasks
- **Complete**: Check the checkbox
- **Edit**: Double-click the task
- **Delete**: Click the trash icon
- **Filter**: Use the filter dropdown to view tasks by category

## Screen Capture and Manipulation

### Taking Screenshots
1. Click **Tools** > **Screen Capture** or press `Ctrl+Shift+S`
2. Select an area of your screen by clicking and dragging
3. Release the mouse to capture the selected area
4. Use the annotation tools to mark up the screenshot:
   - **Draw**: Freehand drawing with selected color and thickness
   - **Rectangle**: Draw rectangles (hold Shift for squares)
   - **Ellipse**: Draw ellipses (hold Shift for circles)
   - **Arrow**: Add arrows to point at important elements
   - **Text**: Add text labels
   - **Blur**: Redact sensitive information
   - **Color Picker**: Select colors for drawing
   - **Undo/Redo**: Fix mistakes easily
5. Save or share your screenshot:
   - Click **Save** to save to a file (PNG/JPEG)
   - Click **Copy** to copy to clipboard
   - Click **Share** to quickly share (if configured)

### Advanced Features

#### OCR (Optical Character Recognition)
1. Take a screenshot or open an existing image
2. Click the **Extract Text** button
3. The extracted text will appear in a new window
4. Use the **Copy** button to copy all text to clipboard
5. Select specific text in the preview to copy just that portion

#### Batch Processing
1. Click **Tools** > **Batch Capture**
2. Select multiple regions to capture in sequence
3. Each capture will be added to the editor
4. Annotate and save all captures at once

#### Active Window Capture
1. Click **Capture** > **Active Window** or press `Alt+Print Screen`
2. The currently active window will be captured automatically
3. The screenshot will open in the editor for annotation

#### Scrolling Screenshot (for web pages)
1. Click **Capture** > **Scrolling Screenshot**
2. Select the area you want to capture
3. The screen will automatically scroll and capture the entire page
4. The full screenshot will open in the editor

### Settings
Access screen capture settings via **Tools** > **Options** > **Capture**:
- Default save location
- Image format (PNG/JPEG)
- Capture hotkeys
- Auto-save options
- OCR language selection
- Annotation defaults (colors, line thickness, etc.)

### Tips
- Use `Esc` to cancel a capture in progress
- Hold `Shift` while resizing to maintain aspect ratio
- Right-click on any annotation to change its properties
- Use the number keys (1-9) to quickly switch between tools

## Accessibility Features

### Screen Reader
- **Enable/Disable**: Click **View** > **Accessibility** > **Toggle Screen Reader**
- **Text Size**: Adjust using **View** > **Accessibility** > **Increase/Decrease Text Size**

### Keyboard Navigation
- **Tab**: Navigate between interactive elements
- **Enter**: Activate selected element
- **Escape**: Close dialogs and menus

## Settings

### Available Settings
- **API Settings**: Configure your Groq API key
- **Voice Settings**: Change voice and speech rate
- **Appearance**: Select theme and adjust UI scaling

### Saving Settings
- Click **Save** to apply changes
- Click **Cancel** to discard changes

## Troubleshooting

### Common Issues
1. **Voice not working**
   - Check your microphone permissions
   - Ensure no other application is using the microphone

2. **VS Code integration not working**
   - Verify VS Code is installed
   - Make sure `code` command is in your system PATH

3. **Missing dependencies**
   - Run `pip install -r requirements.txt`
   - Ensure all required system libraries are installed

### Getting Help
For additional support, please open an issue on our GitHub repository or contact our support team.

---
*Last Updated: July 2024*
