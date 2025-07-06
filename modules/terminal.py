"""
Terminal emulator module for MAYA AI Chatbot.
Provides an embedded terminal interface within the application.
"""
import os
import sys
import subprocess
from typing import Optional, Tuple

from PyQt6.QtCore import QProcess, QProcessEnvironment, QSize, Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QKeySequence, QTextCursor, QTextCharFormat
from PyQt6.QtWidgets import (QPlainTextEdit, QVBoxLayout, QWidget, QMenu,
                           QApplication, QStyle, QStyleFactory, QMessageBox)


class TerminalEmulator(QWidget):
    """A terminal emulator widget that provides shell access."""
    
    # Signal emitted when a command completes
    command_finished = pyqtSignal(int)  # exit_code
    
    def __init__(self, parent=None, shell: str = None, working_dir: str = None):
        """
        Initialize the terminal emulator.
        
        Args:
            parent: Parent widget
            shell: Path to shell executable (default: system default)
            working_dir: Initial working directory (default: user home)
        """
        super().__init__(parent)
        self.shell = shell or self._get_default_shell()
        self.working_dir = working_dir or os.path.expanduser("~")
        self.process = None
        self.command_history = []
        self.history_index = -1
        self.current_command = ""
        self.command_start_pos = 0
        
        self.setup_ui()
        self.start_shell()
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Terminal display
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setUndoRedoEnabled(False)
        self.terminal.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.terminal.customContextMenuRequested.connect(self.show_context_menu)
        
        # Set monospace font
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(10)
        self.terminal.setFont(font)
        
        # Set dark theme colors
        palette = self.terminal.palette()
        palette.setColor(palette.ColorRole.Base, QColor(30, 30, 30))
        palette.setColor(palette.ColorRole.Text, QColor(220, 220, 220))
        self.terminal.setPalette(palette)
        
        layout.addWidget(self.terminal)
    
    def start_shell(self):
        """Start the shell process."""
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            return
            
        self.process = QProcess(self)
        self.process.setWorkingDirectory(self.working_dir)
        
        # Set up environment
        env = QProcessEnvironment.systemEnvironment()
        self.process.setProcessEnvironment(env)
        
        # Connect signals
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.process_finished)
        
        # Start the shell
        self.process.start(self.shell, [])
        if not self.process.waitForStarted():
            self.append_text(f"Failed to start shell: {self.shell}")
            return
        
        # Initial prompt
        self.append_text(f"MAYA Terminal - {self.shell} (type 'exit' to quit)\r\n> ")
        self.command_start_pos = self.terminal.textCursor().position()
    
    def read_stdout(self):
        """Read and display standard output from the process."""
        if not self.process:
            return
            
        data = bytes(self.process.readAllStandardOutput())
        try:
            text = data.decode('utf-8')
            self.append_text(text)
        except UnicodeDecodeError:
            # Fallback for non-UTF-8 output
            self.append_text(str(data))
    
    def read_stderr(self):
        """Read and display standard error from the process."""
        if not self.process:
            return
            
        data = bytes(self.process.readAllStandardError())
        try:
            text = data.decode('utf-8')
            # Format error output in red
            self.append_text(text, QColor(255, 100, 100))
        except UnicodeDecodeError:
            self.append_text(str(data), QColor(255, 100, 100))
    
    def process_finished(self, exit_code, exit_status):
        """Handle process completion."""
        self.command_finished.emit(exit_code)
        if exit_code != 0:
            self.append_text(f"\r\nProcess finished with exit code {exit_code}", QColor(255, 100, 100))
    
    def append_text(self, text: str, color: QColor = None):
        """Append text to the terminal with optional color."""
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if color:
            format = QTextCharFormat()
            format.setForeground(color)
            cursor.setCharFormat(format)
        
        cursor.insertText(text)
        self.terminal.ensureCursorVisible()
    
    def keyPressEvent(self, event):
        """Handle key press events for command input."""
        if not self.process or self.process.state() != QProcess.ProcessState.Running:
            return
            
        cursor = self.terminal.textCursor()
        
        # Handle special keys
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self._handle_enter()
        elif event.key() == Qt.Key.Key_Backspace:
            if cursor.position() > self.command_start_pos:
                cursor.deletePreviousChar()
        elif event.key() == Qt.Key.Key_Up:
            self._navigate_history(-1)
        elif event.key() == Qt.Key.Key_Down:
            self._navigate_history(1)
        else:
            # Insert the typed character
            if event.text() and event.text().isprintable():
                cursor.insertText(event.text())
    
    def _handle_enter(self):
        """Handle Enter key press to execute command."""
        cursor = self.terminal.textCursor()
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        command = cursor.selectedText().strip()
        
        # Move to end of line and add newline
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText("\r\n")
        
        # Execute the command
        if command and command.lower() != 'exit':
            self.process.write(f"{command}\n".encode('utf-8'))
            self.command_history.append(command)
            self.history_index = len(self.command_history)
        elif command.lower() == 'exit':
            self.process.terminate()
        
        self.command_start_pos = self.terminal.textCursor().position()
    
    def _navigate_history(self, direction: int):
        """Navigate through command history."""
        if not self.command_history:
            return
            
        cursor = self.terminal.textCursor()
        
        # Move to the end of the current line
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
        
        # Clear the current line
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        
        # Navigate history
        self.history_index = max(0, min(self.history_index + direction, len(self.command_history)))
        
        # Set the command from history
        if 0 <= self.history_index < len(self.command_history):
            command = self.command_history[self.history_index]
            cursor.insertText(command)
    
    def show_context_menu(self, pos):
        """Show the context menu."""
        menu = self.terminal.createStandardContextMenu()
        
        # Add custom actions
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self.terminal.copy)
        
        paste_action = menu.addAction("Paste")
        paste_action.triggered.connect(self._paste_from_clipboard)
        
        menu.addSeparator()
        
        clear_action = menu.addAction("Clear Terminal")
        clear_action.triggered.connect(self.terminal.clear)
        
        menu.exec(self.terminal.mapToGlobal(pos))
    
    def _paste_from_clipboard(self):
        """Paste text from clipboard into the terminal."""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            cursor = self.terminal.textCursor()
            cursor.insertText(text)
    
    def _get_default_shell(self) -> str:
        """Get the default shell for the current platform."""
        if sys.platform == 'win32':
            return os.environ.get('COMSPEC', 'cmd.exe')
        else:
            return os.environ.get('SHELL', '/bin/bash')
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
        event.accept()


if __name__ == "__main__":
    # For testing the terminal standalone
    app = QApplication(sys.argv)
    
    # Set Fusion style for better look
    app.setStyle(QStyleFactory.create("Fusion"))
    
    terminal = TerminalEmulator()
    terminal.setWindowTitle("MAYA Terminal")
    terminal.resize(800, 500)
    terminal.show()
    
    sys.exit(app.exec())
