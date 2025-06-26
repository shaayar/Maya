"""
Notification module for the MAYA AI Chatbot.
Handles system notifications and reminders for the To-Do List.
"""

import sys
import os
import json
from pathlib import Path
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtWidgets import QMessageBox, QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon


class Notifier(QObject):
    """
    Handles system notifications and reminders for the To-Do List.
    """
    reminder_triggered = pyqtSignal(dict)  # Signal for when a reminder is triggered

    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = QApplication.instance()
        self.tray_icon = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(60000)  # Check every minute

    def init_tray_icon(self):
        """Initialize the system tray icon."""
        if not self.tray_icon:
            self.tray_icon = QSystemTrayIcon()
            
            # Load icon from filesystem
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'app_icon.png')
            if os.path.exists(icon_path):
                self.tray_icon.setIcon(QIcon(icon_path))
            else:
                # Fallback to system icon if file not found
                self.tray_icon.setIcon(QApplication.windowIcon())
            
            # Create the system tray menu
            menu = QMenu()
            show_action = menu.addAction("Show MAYA")
            quit_action = menu.addAction("Quit")
            
            show_action.triggered.connect(self.show_main_window)
            quit_action.triggered.connect(self.quit_app)
            
            self.tray_icon.setContextMenu(menu)
            self.tray_icon.show()

    def show_main_window(self):
        """Show the main application window."""
        if self.app:
            for window in self.app.topLevelWidgets():
                if isinstance(window, QMainWindow):
                    window.show()
                    window.activateWindow()
                    break

    def quit_app(self):
        """Quit the application."""
        if self.app:
            self.app.quit()

    def check_reminders(self):
        """Check for upcoming reminders and show notifications."""
        # Get current time
        now = datetime.now()
        
        # Load todos from file
        todos = self.load_todos()
        if not todos:
            return

        # Check each todo for reminders
        for todo in todos.get("todos", []):
            if self.should_notify(todo, now):
                self.show_notification(todo)

    def should_notify(self, todo: dict, now: datetime) -> bool:
        """
        Determine if a notification should be shown for a todo item.
        
        Args:
            todo: The todo item to check
            now: Current datetime
            
        Returns:
            bool: True if notification should be shown, False otherwise
        """
        # Don't notify for completed tasks
        if todo.get("completed", False):
            return False

        # Check for due date reminder
        due_date = todo.get("due_date")
        if due_date:
            try:
                due = datetime.fromisoformat(due_date)
                # Notify if due within next hour and not notified yet
                if (due - now) <= timedelta(hours=1) and not todo.get("notified", False):
                    return True
            except ValueError:
                pass

        # Check for specific reminder time
        reminder = todo.get("reminder")
        if reminder:
            try:
                reminder_time = datetime.fromisoformat(reminder)
                if reminder_time <= now and not todo.get("notified", False):
                    return True
            except ValueError:
                pass

        return False

    def show_notification(self, todo: dict):
        """
        Show a system notification for a todo item.
        
        Args:
            todo: The todo item to notify about
        """
        title = todo.get("title", "Untitled Task")
        message = f"Reminder: {title}"
        
        if todo.get("due_date"):
            message += f"\nDue: {todo['due_date']}"
        
        # Update the todo as notified
        todos = self.load_todos()
        if todos:
            todos["todos"] = [self.mark_notified(t, todo) for t in todos["todos"]]
            self.save_todos(todos)

        # Show notification
        if self.tray_icon:
            self.tray_icon.showMessage(
                "MAYA Reminder",
                message,
                QSystemTrayIcon.MessageIcon.Information,
                5000  # 5 seconds
            )
        else:
            QMessageBox.information(
                None,
                "MAYA Reminder",
                message
            )

    def mark_notified(self, todo: dict, target: dict) -> dict:
        """
        Mark a todo item as notified if it matches the target.
        
        Args:
            todo: Todo item to check
            target: Target todo item to match
            
        Returns:
            dict: Updated todo item
        """
        if todo.get("title") == target.get("title") and \
           todo.get("due_date") == target.get("due_date") and \
           todo.get("reminder") == target.get("reminder"):
            todo["notified"] = True
        return todo

    def load_todos(self) -> Optional[Dict[str, Any]]:
        """
        Load todo list data from file.
        
        Returns:
            dict: Todo list data or None if error
        """
        try:
            from modules.file_manager import FileManager
            file_manager = FileManager()
            return file_manager.load_todos()
        except Exception as e:
            print(f"Error loading todos: {e}")
            return None

    def save_todos(self, data: Dict[str, Any]) -> bool:
        """
        Save todo list data to file.
        
        Args:
            data: Todo list data to save
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            from modules.file_manager import FileManager
            file_manager = FileManager()
            return file_manager.save_todos(data)
        except Exception as e:
            print(f"Error saving todos: {e}")
            return False
