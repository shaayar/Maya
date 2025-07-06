import os
import logging
import sys
from PyQt6.QtWidgets import (QWidget, QMainWindow, QMenuBar, QMenu, QStatusBar,
                            QVBoxLayout, QTextBrowser, QTextEdit, QPushButton,
                            QMessageBox, QProgressBar, QHBoxLayout, QFileDialog,
                            QInputDialog, QComboBox, QDialog, QGridLayout, QDockWidget,
                            QLabel, QVBoxLayout, QHBoxLayout, QApplication, QTabWidget)
from PyQt6.QtCore import Qt, QEvent, pyqtSignal, QUrl, QCoreApplication, QPropertyAnimation, QAbstractAnimation, QTimer, QObject
from PyQt6.QtGui import (QDesktopServices, QAction, QIcon, QPixmap, QKeySequence,
                        QKeyEvent, QTextCursor)
from typing import Optional, Tuple, Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .screen_reader import ScreenReader

# Local imports
from .file_manager import FileManager
from .web_browser import WebBrowser
from .settings_dialog import SettingsDialog
from .config import load_config
from .styles import get_styles
from .utils import get_greeting
from .todo import TodoList, TodoWidget
from .voice import VoiceAssistant
from .file_search_dialog import FileSearchDialog
from .terminal import TerminalEmulator
from .screen_manipulation import ScreenCapture
from .screen_capture_dialog import ScreenCaptureDialog, ScreenCaptureToolbar

from .file_manager import FileManager
from .web_browser import WebBrowser
from .settings_dialog import SettingsDialog
from .config import load_config
from .styles import get_styles
from .utils import get_greeting
from .todo import TodoList, TodoWidget
from .voice import VoiceAssistant
from .file_search_dialog import FileSearchDialog

class CustomTextEdit(QTextEdit):
    """Custom QTextEdit that sends message on Enter and inserts newline on Shift+Enter."""
    
    returnPressed = pyqtSignal()
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events for custom Enter/Shift+Enter behavior."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                # Shift+Enter: Insert newline
                self.insertPlainText("\n")
            else:
                # Enter: Emit returnPressed signal and accept the event
                self.returnPressed.emit()
                event.accept()
        else:
            # Handle all other key events normally
            super().keyPressEvent(event)


class ChatWindow(QMainWindow):
    """Main chat window UI."""
    
    def __init__(self, parent=None, screen_reader: Optional['ScreenReader'] = None):
        super().__init__(parent)
        self.chatbot = None
        self.file_manager = FileManager()
        self.web_browser = WebBrowser()
        self.current_file = None
        self.config = load_config()
        self.screen_reader = screen_reader
        
        # Initialize instance variables
        self.api_key = os.getenv('GROQ_API_KEY')  # Get API key from environment
        
        # Initialize screen capture
        self.screen_capture = ScreenCapture()
        self.last_capture = None
        
        # Set up accessibility
        self.setObjectName("chatWindow")  # For accessibility
        self.setAccessibleDescription("Main application window for MAYA AI chatbot")
        # Note: setAccessible() was removed in PyQt6 as all widgets are accessible by default
        
        # Configure main window properties
        self.setWindowTitle("MAYA")  # Window title
        self.setGeometry(100, 100, 600, 700)  # x, y, width, height
        
        # Initialize zoom level
        self.current_zoom = 1.0
        
        # Set up the user interface
        self.init_ui()
        
        # Check for API key and initialize chatbot if available
        if self.check_api_key():
            self.init_chatbot()
        else:
            # If no API key, prompt user to enter it in settings
            self.show_settings()
    
    def init_ui(self):
        """
        Initialize the main window UI.
        
        This method sets up the central widget, layout, menu bar, status bar, 
        chat display, input area, buttons, and progress bar.
        """
        # Create central widget and tab widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create chat tab
        self.chat_tab = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_tab)
        self.tab_widget.addTab(self.chat_tab, "Chat")
        
        # Create terminal tab
        self.terminal_tab = QWidget()
        self.terminal_layout = QVBoxLayout(self.terminal_tab)
        self.terminal = TerminalEmulator()
        self.terminal_layout.addWidget(self.terminal)
        self.tab_widget.addTab(self.terminal_tab, "Terminal")
        
        # Set layout for the chat tab
        layout = self.chat_layout
        
        # Initialize Todo List
        self.todo_list = TodoList()
        
        # Initialize Voice Assistant
        self.voice_assistant = VoiceAssistant(wake_word="hey maya")
        self.voice_assistant.wake_word_detected.connect(self.on_wake_word_detected)
        self.voice_assistant.speech_recognized.connect(self.on_speech_recognized)
        self.voice_assistant.error_occurred.connect(self.on_voice_error)
        self.voice_assistant.listening_changed.connect(self.on_listening_changed)
        self.voice_assistant.listen_in_background()
        
        # Create menu bar and status bar
        self.create_menu_bar()
        self.statusBar().showMessage("Ready")
        
        # Voice status indicator
        self.voice_status_label = QLabel()
        self.voice_status_label.setFixedSize(16, 16)
        self.voice_status_label.setToolTip("Voice status")
        self.update_voice_status(False)
        
        # Add voice status to status bar
        self.statusBar().addPermanentWidget(self.voice_status_label)
        
        # Chat display area (takes most of the space)
        self.chat_display = QTextBrowser()
        self.chat_display.setObjectName("chatDisplay")  # For accessibility
        self.chat_display.setAccessibleDescription("Displays the conversation history")
        self.chat_display.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        layout.addWidget(self.chat_display)
        
        # Create Todo Dock Widget
        self.todo_dock = QDockWidget("To-Do List", self)
        self.todo_dock.setWidget(TodoWidget(self.todo_list))
        self.todo_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | 
                                  QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.todo_dock)
        self.todo_dock.setVisible(False)  # Hidden by default
        
        # Input area
        input_layout = QHBoxLayout()
        self.input_box = CustomTextEdit()
        self.input_box.setMaximumHeight(100)
        self.input_box.returnPressed.connect(self.send_message)
        self.input_box.setObjectName("messageInput")  # For accessibility
        self.input_box.setAccessibleDescription("Type your message here")
        self.input_box.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        input_layout.addWidget(self.input_box)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        # Configure buttons with accessibility and keyboard navigation
        def create_button(text, slot, shortcut=None, tooltip=None):
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            if shortcut:
                btn.setShortcut(shortcut)
            if tooltip:
                btn.setToolTip(f"{tooltip} ({shortcut.toString() if shortcut else 'No shortcut'})")
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            return btn
        
        # Create buttons with consistent styling and keyboard shortcuts
        self.send_button = create_button("&Send", self.send_message, 
                                       QKeySequence("Ctrl+Return"), "Send message")
        self.save_button = create_button("&Save Chat", self.save_chat, 
                                       QKeySequence("Ctrl+S"), "Save chat to file")
        self.open_button = create_button("&Open File", self.open_file, 
                                       QKeySequence("Ctrl+O"), "Open chat file")
        self.clear_button = create_button("C&lear Chat", self.clear_chat, 
                                        QKeySequence("Ctrl+L"), "Clear chat history")
        self.web_search_button = create_button("&Web Search", self.web_search, 
                                              QKeySequence("Ctrl+W"), "Search the web")
        
        # Add buttons to layout
        for btn in [self.send_button, self.save_button, self.open_button, 
                   self.clear_button, self.web_search_button]:
            button_layout.addWidget(btn)
            
        # Set tab order for keyboard navigation
        self.setTabOrder(self.input_box, self.send_button)
        self.setTabOrder(self.send_button, self.save_button)
        self.setTabOrder(self.save_button, self.open_button)
        self.setTabOrder(self.open_button, self.clear_button)
        self.setTabOrder(self.clear_button, self.web_search_button)
        self.setTabOrder(self.web_search_button, self.chat_display)
        
        input_layout.addLayout(button_layout)
        layout.addLayout(input_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setObjectName("progressBar")  # For accessibility
        self.progress_bar.setAccessibleDescription("Shows operation progress")
        layout.addWidget(self.progress_bar)
        
        # Set focus to input box by default
        self.input_box.setFocus()
        
        # Install event filter for focus tracking
        self.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        """Handle focus change events for screen reader announcements."""
        if event.type() == QEvent.Type.FocusIn and self.screen_reader and self.screen_reader.is_enabled():
            widget = QApplication.focusWidget()
            if widget:
                name = widget.accessibleName() or widget.whatsThis() or widget.toolTip()
                if name:
                    self.screen_reader.speak(name)
        return super().eventFilter(obj, event)
        
    def create_menu_bar(self):
        """
        Create and configure the application's menu bar.
        Adds File, Voice, Accessibility, and Help menus with various options.
        """
        # Get the main menu bar from the main window
        menubar = self.menuBar()
        menubar.setObjectName("menuBar")  # For accessibility
        
        # Create File menu with keyboard shortcut (Alt+F)
        file_menu = menubar.addMenu('&File')
        file_menu.setObjectName("fileMenu")  # For accessibility
        
        # Add File Search option
        search_action = QAction('&Search Files...', self)
        search_action.setShortcut(QKeySequence('Ctrl+Shift+F'))
        search_action.triggered.connect(self.show_file_search)
        search_action.setStatusTip('Search for files in your project')
        search_action.setObjectName("searchFilesAction")  # For accessibility
        search_action.setToolTip('Search for files in your project')
        file_menu.addAction(search_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Add Settings option to File menu
        settings_action = QAction('&Settings', self)  # & indicates keyboard shortcut (Alt+S)
        settings_action.triggered.connect(self.show_settings)
        settings_action.setStatusTip('Configure application settings')
        settings_action.setShortcut(',')
        settings_action.setObjectName("settingsAction")  # For accessibility
        settings_action.setToolTip('Configure application settings')
        file_menu.addAction(settings_action)
        
        # Add To-Do List toggle
        self.todo_action = QAction('Show &To-Do List', self, checkable=True)
        self.todo_action.triggered.connect(self.toggle_todo_list)
        self.todo_action.setStatusTip('Show/Hide the To-Do List')
        self.todo_action.setObjectName("todoAction")  # For accessibility
        self.todo_action.setToolTip("Toggle To-Do List")
        file_menu.addAction(self.todo_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Add Exit option to File menu with keyboard shortcut
        exit_action = QAction('E&xit', self)  # Alt+X shortcut
        exit_action.setShortcut('Ctrl+Q')  # Additional shortcut
        exit_action.triggered.connect(self.close)  # Connect to close handler
        exit_action.setStatusTip('Exit the application')  # Tooltip
        exit_action.setObjectName("exitAction")  # For accessibility
        exit_action.setToolTip("Exit Application")
        file_menu.addAction(exit_action)
        
        # Voice menu
        voice_menu = menubar.addMenu('&Voice')
        voice_menu.setObjectName("voiceMenu")  # For accessibility
        
        # Toggle voice listening
        self.toggle_voice_action = QAction('Enable Voice Control', self, checkable=True, checked=True)
        self.toggle_voice_action.triggered.connect(self.toggle_voice_control)
        self.toggle_voice_action.setShortcut('Ctrl+Shift+V')
        self.toggle_voice_action.setObjectName("toggleVoiceAction")  # For accessibility
        self.toggle_voice_action.setToolTip("Toggle Voice Control")
        voice_menu.addAction(self.toggle_voice_action)
        
        # Add Accessibility menu if screen reader is available
        if self.screen_reader:
            self.create_accessibility_menu(menubar)
        
        # Add Help menu
        help_menu = menubar.addMenu('&Help')
        help_menu.setObjectName("helpMenu")  # For accessibility
        
        # Add Features option to Help menu
        features_action = QAction('&Features', self)
        features_action.triggered.connect(self.show_features)
        features_action.setStatusTip('View features and roadmap')
        features_action.setObjectName("featuresAction")  # For accessibility
        features_action.setToolTip("View features and roadmap")
        help_menu.addAction(features_action)
        
        # Add About option
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        about_action.setObjectName("aboutAction")  # For accessibility
        about_action.setToolTip("About MAYA AI Chatbot")
        help_menu.addAction(about_action)
    
    def check_api_key(self) -> bool:
        """
        Check if the Groq API key is set and valid.
        
        Returns:
            bool: True if API key exists and is not empty, False otherwise
        """
        api_key = os.getenv('GROQ_API_KEY')
        return bool(api_key and api_key.strip())  # Check if key exists and is not just whitespace
    
    def create_accessibility_menu(self, menubar):
        """Create the Accessibility menu with screen reader controls."""
        if not self.screen_reader:
            return
            
        accessibility_menu = menubar.addMenu('&Accessibility')
        accessibility_menu.setObjectName("accessibilityMenu")  # For accessibility
        
        # Screen reader toggle
        self.screen_reader_action = QAction('Enable &Screen Reader', self, checkable=True)
        self.screen_reader_action.setShortcut('Ctrl+Alt+R')
        self.screen_reader_action.toggled.connect(self.toggle_screen_reader)
        self.screen_reader_action.setChecked(self.screen_reader.is_enabled())
        self.screen_reader_action.setObjectName("screenReaderAction")  # For accessibility
        self.screen_reader_action.setToolTip("Toggle Screen Reader")
        accessibility_menu.addAction(self.screen_reader_action)
        
        # Read current element
        read_current_action = QAction('Read &Current Element', self)
        read_current_action.setShortcut('Ctrl+Alt+C')
        read_current_action.triggered.connect(self.read_current_element)
        read_current_action.setObjectName("readCurrentAction")  # For accessibility
        read_current_action.setToolTip("Read Current Element")
        accessibility_menu.addAction(read_current_action)
        
        # Read from cursor
        read_from_cursor_action = QAction('Read from Cu&rsor', self)
        read_from_cursor_action.setShortcut('Ctrl+Alt+Space')
        read_from_cursor_action.triggered.connect(self.read_from_cursor)
        read_from_cursor_action.setObjectName("readFromCursorAction")  # For accessibility
        read_from_cursor_action.setToolTip("Read from Cursor")
        accessibility_menu.addAction(read_from_cursor_action)
        
        # Add separator
        accessibility_menu.addSeparator()
        
        # Text size controls
        text_size_menu = accessibility_menu.addMenu('Text &Size')
        text_size_menu.setObjectName("textSizeMenu")  # For accessibility
        
        # Increase text size
        increase_text_action = QAction('Zoom &In', self)
        increase_text_action.setShortcut('Ctrl+Plus')
        increase_text_action.triggered.connect(self.increase_text_size)
        increase_text_action.setObjectName("increaseTextAction")  # For accessibility
        increase_text_action.setToolTip("Increase Text Size")
        text_size_menu.addAction(increase_text_action)
        
        # Decrease text size
        decrease_text_action = QAction('Zoom &Out', self)
        decrease_text_action.setShortcut('Ctrl+Minus')
        decrease_text_action.triggered.connect(self.decrease_text_size)
        decrease_text_action.setObjectName("decreaseTextAction")  # For accessibility
        decrease_text_action.setToolTip("Decrease Text Size")
        text_size_menu.addAction(decrease_text_action)
        
        # Reset zoom
        reset_zoom_action = QAction('&Reset Zoom', self)
        reset_zoom_action.setShortcut('Ctrl+0')
        reset_zoom_action.triggered.connect(self.reset_text_size)
        reset_zoom_action.setObjectName("resetZoomAction")  # For accessibility
        reset_zoom_action.setToolTip("Reset Text Size")
        text_size_menu.addAction(reset_zoom_action)
    
    def toggle_screen_reader(self, enabled: bool):
        """Toggle screen reader on/off."""
        if self.screen_reader:
            self.screen_reader.set_enabled(enabled)
            status = "enabled" if enabled else "disabled"
            self.statusBar().showMessage(f"Screen reader {status}", 3000)
    
    def read_current_element(self):
        """Read the currently focused element."""
        if not self.screen_reader or not self.screen_reader.is_enabled():
            return
            
        focused = QApplication.focusWidget()
        if focused:
            text = focused.accessibleName() or focused.accessibleDescription() or "No description available"
            self.screen_reader.speak(text)
    
    def read_from_cursor(self):
        """Read text from the cursor position."""
        if not self.screen_reader or not self.screen_reader.is_enabled():
            return
            
        focused = QApplication.focusWidget()
        if hasattr(focused, 'textCursor'):
            cursor = focused.textCursor()
            text = cursor.selectedText() or cursor.block().text()
            if text:
                self.screen_reader.speak(text)
    
    def increase_text_size(self):
        """Increase the text size for better readability."""
        self.adjust_text_size(1.1)
    
    def decrease_text_size(self):
        """Decrease the text size."""
        self.adjust_text_size(0.9)
    
    def reset_text_size(self):
        """Reset text size to default."""
        # Set default font sizes (12pt for chat, 10pt for input)
        chat_font = self.chat_display.font()
        input_font = self.input_box.font()
        
        chat_font.setPointSize(12)
        input_font.setPointSize(10)
        
        self.chat_display.setFont(chat_font)
        self.input_box.setFont(input_font)
        
        # Reset zoom factor
        self.current_zoom = 1.0
        
        # Update status bar
        self.statusBar().showMessage("Text size reset to default", 2000)
    
    def adjust_text_size(self, factor):
        """
        Adjust the text size by the given factor.
        
        Args:
            factor: Multiplier for the current font size (e.g., 1.1 for 10% larger)
        """
        # Get current font sizes or use defaults
        chat_font = self.chat_display.font()
        input_font = self.input_box.font()
        
        # Calculate new sizes
        new_chat_size = max(8, min(72, int(chat_font.pointSizeF() * factor)))
        new_input_size = max(8, min(72, int(input_font.pointSizeF() * factor)))
        
        # Apply new sizes
        chat_font.setPointSizeF(new_chat_size)
        input_font.setPointSizeF(new_input_size)
        
        self.chat_display.setFont(chat_font)
        self.input_box.setFont(input_font)
        
        # Save the current zoom factor
        self.current_zoom = factor
        
        # Update status bar with new size
        self.statusBar().showMessage(f"Text size: {new_chat_size}pt", 2000)
    
    def show_file_search(self):
        """Show the file search dialog."""
        try:
            dialog = FileSearchDialog(self, os.getcwd())
            dialog.file_selected.connect(self.open_file_from_search)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open file search: {str(e)}"
            )
            logger.error(f"Error in show_file_search: {str(e)}")
    
    def open_file_from_search(self, file_path):
        """Open a file that was selected from the file search dialog."""
        try:
            if os.path.isfile(file_path):
                self.current_file = file_path
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.chat_display.append(f"<b>File: {os.path.basename(file_path)}</b>\n{content}")
                self.statusBar().showMessage(f"Opened: {file_path}", 3000)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open file: {str(e)}"
            )
            logger.error(f"Error opening file from search: {str(e)}")
    
    def show_features(self):
        """Show the features dialog with current and planned features."""
        features_text = """
        <h2>MAYA AI Features</h2>
        
        <h3>Current Features:</h3>
        <ul>
            <li>AI-Powered Chat Interface</li>
            <li>File Search and Preview</li>
            <li>Screen Capture with OCR</li>
            <li>Voice Control (Wake Word: "Hey Maya")</li>
            <li>To-Do List with Reminders</li>
            <li>Accessibility Features (Screen Reader, Text Size)</li>
            <li>Web Search</li>
            <li>Terminal Access</li>
        </ul>
        
        <h3>Planned Features:</h3>
        <ul>
            <li>VS Code Integration</li>
            <li>Enhanced File Management</li>
            <li>Code Generation and Analysis</li>
            <li>Customizable Themes</li>
            <li>Plugin System</li>
        </ul>
        
        <p>For more details, check our documentation.</p>
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("MAYA AI Features")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(features_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def show_about(self):
        """Show the about dialog."""
        about_text = """
        <h2>MAYA AI Chatbot</h2>
        <p>Version 1.0.0</p>
        <p>An intelligent chatbot with accessibility features.</p>
        <p>© 2025 MAYA AI. All rights reserved.</p>
        """
        QMessageBox.about(self, "About MAYA AI", about_text)
    
    def show_settings(self):
        """
        Display the settings dialog and handle the result.
        If settings are accepted and API key is valid, (re)initialize the chatbot.
        """
        dialog = SettingsDialog(self, self.voice_assistant, self.screen_reader)
        dialog.settings_updated.connect(self.on_settings_updated)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if self.check_api_key():
                # Reinitialize chatbot if API key is valid
                self.init_chatbot()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Invalid API key. Please check your settings.")
    
    def on_settings_updated(self, settings):
        """Handle settings updates from the settings dialog."""
        # Voice settings are already applied in the dialog
        pass
    
    def init_chatbot(self):
        """
        Initialize the chatbot with the current configuration.
        Shows an error message if initialization fails.
        """
        try:
            from .chatbot import Chatbot
            self.chatbot = Chatbot(self.config)  # Initialize chatbot with config
            self.show_greeting()  # Show welcome message
            self.statusBar().showMessage("Connected to Groq API")  # Update status
        except Exception as e:
            # Show error if chatbot initialization fails
            error_msg = f"Failed to initialize chatbot: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
    
    def show_greeting(self):
        """
        Display a greeting message with the current time in the chat display.
        The greeting is formatted in bold for better visibility.
        """
        greeting = get_greeting()  # Get formatted greeting with time
        self.chat_display.append(f"<b>{greeting}</b>")  # Display in bold
    
    def send_message(self):
        """
        Process and send the user's message to the chatbot.
        Handles input validation, displays the message, and shows the response.
        """
        # Check if chatbot is properly initialized
        if not self.chatbot:
            QMessageBox.warning(
                self,
                "Error",
                "Chatbot not initialized. Please check your API key."
            )
            return
        
        # Get and validate user input
        user_input = self.input_box.toPlainText().strip()
        if not user_input:
            QMessageBox.warning(
                self,
                "Empty Message",
                "Please enter a message."
            )
            return
            
        # Replace 'AI' with 'Maya' in the user input
        user_input = user_input.replace('AI', 'Maya')
        
        # Check message length against config limit
        max_length = self.config.get('max_tokens', 2000)  # Default to 2000 if not set
        if len(user_input) > max_length:
            QMessageBox.warning(
                self,
                "Message Too Long",
                f"Message exceeds maximum length of {max_length} characters."
            )
            return
        
        try:
            # Display user's message in the chat
            self.chat_display.append(f"<b>You:</b> {user_input}")
            self.input_box.clear()  # Clear input field
            
            # Disable send button and show progress bar
            self.send_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            
            # Process the message (this might take some time)
            QCoreApplication.processEvents()  # Update UI
            
            # Get and display the AI's response
            response = self.chatbot.get_response(user_input)
            self.chat_display.append(f"<b>Maya:</b> {response}")
            
            # Auto-scroll to the latest message
            self.chat_display.verticalScrollBar().setValue(
                self.chat_display.verticalScrollBar().maximum()
            )
            
        except Exception as e:
            # Show error in status bar and message box
            error_msg = f"Error: {str(e)}"
            self.statusBar().showMessage(error_msg)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to get response: {str(e)}"
            )
        finally:
            # Re-enable the send button and hide progress bar
            self.send_button.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.input_box.setFocus()  # Return focus to input field
    
    def save_chat(self):
        """
        Save the current chat conversation to a text file.
        Prompts the user to choose a save location and handles file operations.
        """
        # Check if there's any content to save
        if not self.chat_display.toPlainText().strip():
            QMessageBox.warning(
                self,
                "Empty Chat",
                "No chat content to save."
            )
            return
        
        # Show file save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,  # Parent window
            "Save Chat",  # Dialog title
            "",  # Start directory (empty for default)
            "Text Files (*.txt);;All Files (*)"  # File filters
        )
        
        # If user selected a file path
        if file_path:
            try:
                # Ensure .txt extension if not provided
                if not file_path.lower().endswith('.txt'):
                    file_path += '.txt'
                
                # Write chat content to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.chat_display.toPlainText())
                
                # Confirm save to user
                self.statusBar().showMessage(f"Chat saved to {file_path}")
                
            except Exception as e:
                # Handle file operation errors
                error_msg = f"Failed to save chat: {str(e)}"
                QMessageBox.critical(self, "Error", error_msg)
    
    def open_file(self):
        """
        Open and display a chat file in the chat window.
        Supports plain text files and preserves formatting.
        """
        # Show file open dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,  # Parent window
            "Open Chat File",  # Dialog title
            "",  # Start directory (empty for default)
            "Text Files (*.txt);;All Files (*)"  # File filters
        )
        
        # If user selected a file
        if file_path:
            try:
                # Read file content with UTF-8 encoding
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Display file content in chat display
                self.chat_display.setPlainText(content)
                
                # Update status bar
                self.statusBar().showMessage(f"Opened {file_path}")
                
            except Exception as e:
                # Handle file operation errors
                error_msg = f"Failed to open file: {str(e)}"
                QMessageBox.critical(self, "Error", error_msg)

    # Screen Capture Methods
    def capture_full_screen(self):
        """Capture the entire screen."""
        try:
            self.last_capture = self.screen_capture.capture_screen()
            if self.last_capture:
                self.show_capture_result(self.last_capture)
        except Exception as e:
            QMessageBox.critical(self, "Capture Error", f"Failed to capture screen: {str(e)}")
            logger.error(f"Screen capture failed: {str(e)}")
    
    def capture_region(self):
        """Open region selection dialog for screen capture."""
        try:
            dialog = ScreenCaptureDialog(self)
            dialog.capture_completed.connect(self.on_capture_completed)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Capture Error", f"Failed to capture region: {str(e)}")
            logger.error(f"Region capture failed: {str(e)}")
    
    def capture_active_window(self):
        """Capture the currently active window."""
        try:
            self.last_capture = self.screen_capture.capture_active_window()
            if self.last_capture:
                self.show_capture_result(self.last_capture)
        except Exception as e:
            QMessageBox.critical(self, "Capture Error", f"Failed to capture active window: {str(e)}")
            logger.error(f"Active window capture failed: {str(e)}")
    
    def on_capture_completed(self, pixmap, metadata):
        """Handle completed screen capture."""
        self.last_capture = pixmap
        self.show_capture_result(pixmap, metadata)
    
    def show_capture_result(self, pixmap, metadata=None):
        """Show the captured screenshot in a dialog."""
        try:
            # Create a dialog to show the captured image
            dialog = QDialog(self)
            dialog.setWindowTitle("Screenshot")
            dialog.setMinimumSize(800, 600)
            
            layout = QVBoxLayout()
            
            # Image label
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setPixmap(pixmap.scaled(780, 500, 
                                             Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation))
            
            # Toolbar
            toolbar = ScreenCaptureToolbar()
            toolbar.capture_requested.connect(self.capture_region)
            toolbar.save_requested.connect(lambda: self.save_screenshot(pixmap))
            toolbar.copy_requested.connect(lambda: self.copy_to_clipboard(pixmap))
            toolbar.ocr_requested.connect(lambda: self.extract_text_from_image(pixmap))
            
            # Add widgets to layout
            layout.addWidget(image_label)
            layout.addWidget(toolbar)
            
            # Set layout and show dialog
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display capture: {str(e)}")
            logger.error(f"Error showing capture result: {str(e)}")
    
    def save_screenshot(self, pixmap):
        """Save the screenshot to a file."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Screenshot",
                "",
                "PNG (*.png);;JPEG (*.jpg *.jpeg);;All Files (*)"
            )
            
            if file_path:
                if not file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_path += '.png'
                    
                if pixmap.save(file_path):
                    QMessageBox.information(self, "Success", f"Screenshot saved to {file_path}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save screenshot")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save screenshot: {str(e)}")
            logger.error(f"Screenshot save failed: {str(e)}")
    
    def copy_to_clipboard(self, pixmap):
        """Copy the screenshot to the clipboard."""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(pixmap)
            self.statusBar().showMessage("Screenshot copied to clipboard", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy to clipboard: {str(e)}")
            logger.error(f"Clipboard copy failed: {str(e)}")
    
    def extract_text_from_image(self, pixmap):
        """Extract text from the screenshot using OCR."""
        try:
            text = self.screen_capture.ocr_text(pixmap)
            if text:
                # Show extracted text in a dialog
                dialog = QDialog(self)
                dialog.setWindowTitle("Extracted Text")
                dialog.resize(600, 400)
                
                layout = QVBoxLayout()
                
                # Text edit for extracted text
                text_edit = QTextEdit()
                text_edit.setPlainText(text)
                text_edit.setReadOnly(True)
                
                # Buttons
                button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                            QDialogButtonBox.StandardButton.Copy)
                button_box.accepted.connect(dialog.accept)
                button_box.button(QDialogButtonBox.StandardButton.Copy).clicked.connect(
                    lambda: self.copy_to_clipboard_text(text))
                
                # Add widgets to layout
                layout.addWidget(text_edit)
                layout.addWidget(button_box)
                
                dialog.setLayout(layout)
                dialog.exec()
            else:
                QMessageBox.information(self, "No Text Found", 
                                     "No text could be extracted from the image.")
        except Exception as e:
            QMessageBox.critical(self, "OCR Error", 
                               f"Failed to extract text: {str(e)}")
            logger.error(f"OCR extraction failed: {str(e)}")
    
    def copy_to_clipboard_text(self, text):
        """Copy text to the clipboard."""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.statusBar().showMessage("Text copied to clipboard", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy text: {str(e)}")
            logger.error(f"Text copy failed: {str(e)}")

    def clear_chat(self):
        """
        Clear the chat display after user confirmation.
        Preserves the greeting message after clearing.
        """
        # Ask for confirmation before clearing
        reply = QMessageBox.question(
            self,  # Parent window
            "Clear Chat",  # Dialog title
            "Are you sure you want to clear the chat?",  # Message
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # Buttons
            QMessageBox.StandardButton.No  # Default button
        )
        
        # Clear only if user confirms
        if reply == QMessageBox.StandardButton.Yes:
            self.chat_display.clear()  # Clear the display
            self.show_greeting()  # Show fresh greeting
    
    def web_search(self):
        """
        Perform a web search using the current input text.
        Shows a dialog to select the search engine and executes the search.
        """
        # Get and validate user input
        user_input = self.input_box.toPlainText().strip()
        if not user_input:
            QMessageBox.warning(self, "Empty Query", "Please enter a search query.")
            return
        
        # Define available search engines and show selection dialog
        engines = ['Google', 'Bing', 'DuckDuckGo', 'YouTube']
        engine, ok = QInputDialog.getItem(
            self,                           # Parent widget
            "Select Search Engine",         # Dialog title
            "Choose your preferred search engine:",  # Dialog message
            engines,                        # List of items to show
            0,                              # Default selected index
            False                           # Not editable
        )
        
        # If user selected an engine and clicked OK
        if ok and engine:
            try:
                # Perform the search using the selected engine
                self.web_browser.search(user_input, engine)
                # Clear the input box after successful search
                self.input_box.clear()
            except Exception as e:
                # Show error message if search fails
                error_msg = f"Failed to perform search: {str(e)}"
                QMessageBox.critical(self, "Error", error_msg)
    
    def toggle_todo_list(self, checked):
        """
        Toggle the visibility of the To-Do List dock widget.
        
        Args:
            checked: Whether the action is checked
        """
        self.todo_dock.setVisible(checked)
        self.todo_action.setText('Hide &To-Do List' if checked else 'Show &To-Do List')
    
    # Voice Assistant Methods
    def on_wake_word_detected(self):
        """Handle wake word detection."""
        self.statusBar().showMessage("Wake word detected! How can I help you?", 3000)
        self.update_voice_status(True)
        
    def on_speech_recognized(self, text):
        """Handle recognized speech."""
        self.statusBar().showMessage(f"Recognized: {text}", 3000)
        self.input_box.setPlainText(text)
        self.send_message()
        
    def on_voice_error(self, error_msg):
        """Handle voice assistant errors."""
        self.statusBar().showMessage(error_msg, 5000)
    
    def on_listening_changed(self, is_listening):
        """Update UI when listening state changes."""
        self.update_voice_status(is_listening)
    
    def update_voice_status(self, is_listening):
        """Update the voice status indicator."""
        if is_listening:
            self.voice_status_label.setPixmap(QPixmap("resources/icons/mic_on.png"))
            self.voice_status_label.setToolTip("Voice control active")
        else:
            self.voice_status_label.setPixmap(QPixmap("resources/icons/mic_off.png"))
            self.voice_status_label.setToolTip("Voice control inactive")
            self.voice_status_label.setToolTip("Voice control inactive")
    
    def toggle_voice_control(self, enabled):
        """Enable or disable voice control."""
        if enabled:
            self.voice_assistant.listen_in_background()
            self.statusBar().showMessage("Voice control enabled", 2000)
        else:
            self.voice_assistant.stop()
            self.statusBar().showMessage("Voice control disabled", 2000)
    
    def closeEvent(self, event):
        """
        Handle the window close event.
        Shows a confirmation dialog before closing the application.
        
        Args:
            event: The close event
        """
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,                           # Parent widget
            "Exit MAYA",                    # Dialog title
            "Are you sure you want to exit?",  # Dialog message
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # Buttons
            QMessageBox.StandardButton.No  # Default button
        )
        
        # Process user's choice
        if reply == QMessageBox.StandardButton.Yes:
            # Save todo list before closing
            if hasattr(self, 'todo_list'):
                self.todo_list.save()
            # Stop voice assistant
            if hasattr(self, 'voice_assistant'):
                self.voice_assistant.stop()
            # Close the application
            event.accept()
        else:
            # Cancel the close event
            event.ignore()
    
    def apply_styles(self):
        """
        Apply CSS styles and animations to all UI components.
        Loads styles from the styles module and sets up button hover effects.
        """
        # Apply the combined CSS styles from the styles module
        self.setStyleSheet(get_styles())
        
        # Add hover effects to all buttons in the window
        for btn in self.findChildren(QPushButton):
            # Set up enter and leave event handlers for hover effect
            btn.enterEvent = lambda e, b=btn: self.animate_button(b, True)
            btn.leaveEvent = lambda e, b=btn: self.animate_button(b, False)
    
    def animate_button(self, button, hover):
        """
        Create a hover animation effect for buttons.
        
        Args:
            button: The button widget to animate
            hover: Boolean indicating if the mouse is entering (True) or leaving (False) the button
        """
        # Create a property animation for the button's geometry
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(150)  # Animation duration in milliseconds
        
        # Adjust button size based on hover state
        if hover:
            # Expand button slightly on hover
            animation.setEndValue(button.geometry().adjusted(-2, -2, 2, 2))
        else:
            # Return to original size when not hovering
            animation.setEndValue(button.geometry().adjusted(2, 2, -2, -2))
        
        # Start the animation and clean up when done
        animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        # Buttons in a horizontal layout below the input box
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Create and add buttons to the horizontal layout
        buttons = [
            ("Send", self.send_message, 100),
            ("Save Chat", self.save_chat, 100),
            ("Open File", self.open_file, 100),
            ("Clear Chat", self.clear_chat, 100),
            ("Web Search", self.web_search, 100)
        ]
        
        for text, handler, width in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            if width:
                button.setMinimumWidth(width)
            button_layout.addWidget(button)
        
        # Add stretch to distribute buttons evenly
        button_layout.addStretch()
        
        # Create a container widget for the button layout
        button_container = QWidget()
        button_container.setLayout(button_layout)
        
        # Add button container to grid (below input box, full width)
        main_grid.addWidget(button_container, 2, 0, 1, 3)  # Row 2, Column 0-2, spans 3 columns
        
        # Progress bar at the bottom
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_grid.addWidget(self.progress_bar, 3, 0, 1, 3)  # Row 3, Column 0-2, spans 3 columns
        
        # Set stretch factors
        main_grid.setRowStretch(0, 1)  # Chat display expands
        main_grid.setRowStretch(1, 0)  # Input area fixed height
        main_grid.setRowStretch(2, 0)  # Input area fixed height
        main_grid.setRowStretch(3, 0)  # Progress bar fixed height
        
        # Settings action
        settings_action = QAction('&Settings', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)

        # Toggle Todo List action
        self.toggle_todo_action = QAction('Show &To-Do List', self, checkable=True)
        self.toggle_todo_action.setShortcut('Ctrl+T')
        self.toggle_todo_action.toggled.connect(self.toggle_todo_list)
        file_menu.addAction(self.toggle_todo_action)

        # Screen Capture menu
        capture_menu = menubar.addMenu('&Capture')
        
        # Full screen capture
        full_screen_action = QAction('Capture &Full Screen', self)
        full_screen_action.setShortcut('Ctrl+Shift+F')
        full_screen_action.triggered.connect(self.capture_full_screen)
        capture_menu.addAction(full_screen_action)
        
        # Region capture
        region_action = QAction('Capture &Region', self)
        region_action.setShortcut('Ctrl+Shift+R')
        region_action.triggered.connect(self.capture_region)
        capture_menu.addAction(region_action)
        
        # Active window capture
        window_action = QAction('Capture &Active Window', self)
        window_action.setShortcut('Ctrl+Shift+W')
        window_action.triggered.connect(self.capture_active_window)
        capture_menu.addAction(window_action)
        
        capture_menu.addSeparator()
        
        # Terminal menu
        terminal_menu = menubar.addMenu('&Terminal')

        # New terminal tab action
        new_terminal_action = QAction('&New Terminal', self)
        new_terminal_action.setShortcut('Ctrl+Shift+T')
        new_terminal_action.triggered.connect(self.add_terminal_tab)
        terminal_menu.addAction(new_terminal_action)

        # Close terminal tab action
        close_terminal_action = QAction('&Close Terminal', self)
        close_terminal_action.setShortcut('Ctrl+W')
        close_terminal_action.triggered.connect(self.close_terminal_tab)
        terminal_menu.addAction(close_terminal_action)

        # Voice control toggle
        self.voice_control_action = QAction('Enable &Voice Control', self, checkable=True)
        self.voice_control_action.setShortcut('Ctrl+Shift+V')
        self.voice_control_action.toggled.connect(self.toggle_voice_control)
        file_menu.addAction(self.voice_control_action)

        # Exit action