import os
import logging
from PyQt6.QtWidgets import (QWidget, QMainWindow, QMenuBar, QMenu, QStatusBar,
                            QVBoxLayout, QTextBrowser, QTextEdit, QPushButton,
                            QMessageBox, QProgressBar, QHBoxLayout, QFileDialog,
                            QInputDialog, QComboBox, QDialog, QGridLayout)
from PyQt6.QtCore import Qt, QEvent, pyqtSignal, QUrl, QCoreApplication, QPropertyAnimation, QAbstractAnimation
from PyQt6.QtGui import QDesktopServices, QAction
from typing import Optional, Tuple, Dict, Any

from .datetime_utils import get_greeting
from .file_operations import FileManager
from .web_browser import WebBrowser
from .settings_dialog import SettingsDialog
from .config import load_config
from .styles import get_styles

# Update the ChatWindow class to inherit from QMainWindow
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
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Chat display
        self.chat_display = QTextBrowser()
        layout.addWidget(self.chat_display)
        
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
        Adds File menu with Settings and Exit options.
        """
        # Get the main menu bar from the main window
        menubar = self.menuBar()
        
        # Create File menu with keyboard shortcut (Alt+F)
        file_menu = menubar.addMenu('&File')
        
        # Add Settings option to File menu
        settings_action = QAction('&Settings', self)  # & indicates keyboard shortcut (Alt+S)
        settings_action.triggered.connect(self.show_settings)  # Connect to settings handler
        settings_action.setStatusTip('Configure application settings')  # Tooltip
        file_menu.addAction(settings_action)
        
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
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if self.check_api_key():
                # Reinitialize chatbot if API key is valid
                self.init_chatbot()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Invalid API key. Please check your settings."
                )
    
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
        animation.start(QAbstractAnimation.DeleteWhenStopped)
    
    def init_ui(self):
        """
        Initialize the main window's user interface with a grid layout.
        Sets up all UI components including chat display, input area, and buttons.
        """
        # Create and set up the central widget that will contain all UI elements
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Configure the main grid layout with consistent spacing and margins
        main_grid = QGridLayout(central_widget)
        main_grid.setSpacing(10)  # Space between widgets
        main_grid.setContentsMargins(10, 10, 10, 10)  # Margins around the grid (left, top, right, bottom)
        
        # Create menu bar and status bar
        self.create_menu_bar()
        self.statusBar().showMessage("Ready")
        
        # Chat display area (takes most of the space)
        self.chat_display = QTextBrowser()
        main_grid.addWidget(self.chat_display, 0, 0, 1, 3)  # Row 0, Column 0-2, spans 3 columns
        
        # Input area
        self.input_box = QTextEdit()
        self.input_box.setMaximumHeight(100)
        main_grid.addWidget(self.input_box, 1, 0, 2, 2)  # Row 1-2, Column 0-1, spans 2 rows and 2 columns
        
        # Buttons in a vertical layout on the right
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)
        
        # Save button
        self.save_button = QPushButton("Save Chat")
        self.save_button.clicked.connect(self.save_chat)
        button_layout.addWidget(self.save_button)
        
        # Open button
        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open_file)
        button_layout.addWidget(self.open_button)
        
        # Clear button
        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.clicked.connect(self.clear_chat)
        button_layout.addWidget(self.clear_button)
        
        # Web search button
        self.web_search_button = QPushButton("Web Search")
        self.web_search_button.clicked.connect(self.web_search)
        button_layout.addWidget(self.web_search_button)
        
        # Add stretch to push buttons to the top
        button_layout.addStretch()
        
        # Add button layout to grid
        main_grid.addLayout(button_layout, 1, 2, 2, 1)  # Row 1-2, Column 2, spans 2 rows
        
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