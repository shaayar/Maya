import os
import logging
from PyQt6.QtWidgets import (QWidget, QMainWindow, QMenuBar, QMenu, QStatusBar,
                            QVBoxLayout, QTextBrowser, QTextEdit, QPushButton,
                            QMessageBox, QProgressBar, QHBoxLayout, QFileDialog,
                            QInputDialog, QComboBox, QDialog, QGridLayout, QDockWidget,
                            QLabel, QVBoxLayout, QHBoxLayout)
from PyQt6.QtCore import Qt, QEvent, pyqtSignal, QUrl, QCoreApplication, QPropertyAnimation, QAbstractAnimation, QTimer
from PyQt6.QtGui import QDesktopServices, QAction, QIcon, QPixmap, QKeySequence
from typing import Optional, Tuple, Dict, Any, List
import os
import sys

from .file_manager import FileManager
from .web_browser import WebBrowser
from .settings_dialog import SettingsDialog
from .config import load_config
from .styles import get_styles
from .utils import get_greeting
from .todo import TodoList, TodoWidget
from .voice import VoiceAssistant
from .file_search_dialog import FileSearchDialog

class ChatWindow(QMainWindow):
    """Main chat window UI."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chatbot = None
        self.file_manager = FileManager()
        self.web_browser = WebBrowser()
        self.current_file = None
        self.config = load_config()
        
        # Initialize instance variables
        self.api_key = os.getenv('GROQ_API_KEY')  # Get API key from environment
        
        # Configure main window properties
        self.setWindowTitle("MAYA")  # Window title
        self.setGeometry(100, 100, 600, 700)  # x, y, width, height
        
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
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
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
        self.input_box = QTextEdit()
        self.input_box.setMaximumHeight(100)
        input_layout.addWidget(self.input_box)
        
        # Buttons
        button_layout = QVBoxLayout()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)
        
        self.save_button = QPushButton("Save Chat")
        self.save_button.clicked.connect(self.save_chat)
        button_layout.addWidget(self.save_button)
        
        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open_file)
        button_layout.addWidget(self.open_button)
        
        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.clicked.connect(self.clear_chat)
        button_layout.addWidget(self.clear_button)
        
        self.web_search_button = QPushButton("Web Search")
        self.web_search_button.clicked.connect(self.web_search)
        button_layout.addWidget(self.web_search_button)
        
        input_layout.addLayout(button_layout)
        layout.addLayout(input_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
    def create_menu_bar(self):
        """
        Create and configure the application's menu bar.
        Adds File menu with Search, Settings, and Exit options.
        """
        # Get the main menu bar from the main window
        menubar = self.menuBar()
        
        # Create File menu with keyboard shortcut (Alt+F)
        file_menu = menubar.addMenu('&File')
        
        # Add File Search option
        search_action = QAction('&Search Files...', self)
        search_action.setShortcut(QKeySequence('Ctrl+Shift+F'))
        search_action.triggered.connect(self.show_file_search)
        search_action.setStatusTip('Search for files in your project')
        file_menu.addAction(search_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Add Settings option to File menu
        settings_action = QAction('&Settings', self)  # & indicates keyboard shortcut (Alt+S)
        settings_action.triggered.connect(self.show_settings)  # Connect to settings handler
        settings_action.setStatusTip('Configure application settings')  # Tooltip
        file_menu.addAction(settings_action)
        
        # Add To-Do List toggle
        self.todo_action = QAction('Show &To-Do List', self, checkable=True)
        self.todo_action.triggered.connect(self.toggle_todo_list)
        self.todo_action.setStatusTip('Show/Hide the To-Do List')
        file_menu.addAction(self.todo_action)
        
        # Voice menu
        voice_menu = menubar.addMenu('&Voice')
        
        # Toggle voice listening
        self.toggle_voice_action = QAction('Enable Voice Control', self, checkable=True, checked=True)
        self.toggle_voice_action.triggered.connect(self.toggle_voice_control)
        voice_menu.addAction(self.toggle_voice_action)
        
        # Add Help menu
        help_menu = menubar.addMenu('&Help')
        
        # Add Features option to Help menu
        features_action = QAction('&Features', self)
        features_action.triggered.connect(self.show_features)
        features_action.setStatusTip('View features and roadmap')
        help_menu.addAction(features_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Add Exit option to File menu with keyboard shortcut
        exit_action = QAction('E&xit', self)  # Alt+X shortcut
        exit_action.setShortcut('Ctrl+Q')  # Additional shortcut
        exit_action.triggered.connect(self.close)  # Connect to close handler
        exit_action.setStatusTip('Exit the application')  # Tooltip
        file_menu.addAction(exit_action)
    
    def check_api_key(self) -> bool:
        """
        Check if the Groq API key is set and valid.
        
        Returns:
            bool: True if API key exists and is not empty, False otherwise
        """
        api_key = os.getenv('GROQ_API_KEY')
        return bool(api_key and api_key.strip())  # Check if key exists and is not just whitespace
    
    def show_settings(self):
        """
        Display the settings dialog and handle the result.
        If settings are accepted and API key is valid, (re)initialize the chatbot.
        """
        dialog = SettingsDialog(self, self.voice_assistant)
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
            self.chat_display.append(f"<b>AI:</b> {response}")
            
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
        
        # Set column stretch factors
        main_grid.setColumnStretch(0, 1)  # Chat and input expand
        main_grid.setColumnStretch(1, 1)  # Chat and input expand
        main_grid.setColumnStretch(2, 0)  # Buttons fixed width
        
        # Apply styles and animations
        self.apply_styles()
        
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Settings action
        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def check_api_key(self) -> bool:
        """Check if API key is set and valid."""
        from groq import Groq
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return False
        
        try:
            # Test the API key with a simple request
            client = Groq(api_key=api_key)
            client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model="llama-3.3-70b-versatile",
                max_tokens=1
            )
            return True
        except Exception:
            return False
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if self.check_api_key():
                self.init_chatbot()
            else:
                QMessageBox.warning(self, "Error", "Invalid API key. Please check your settings.")
    
    def closeEvent(self, event):
        """Handle window close event."""
        reply = QMessageBox.question(
            self,
            "Exit MAYA",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()