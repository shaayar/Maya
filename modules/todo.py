"""
To-Do List module for MAYA AI Chatbot.
Handles the creation, management, and persistence of to-do items.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QObject, QDateTime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QListWidgetItem, QLineEdit, QPushButton, QLabel,
                           QMessageBox, QDialog, QDialogButtonBox, QInputDialog,
                           QComboBox, QMenu, QStyledItemDelegate, QStyle, QStyleOptionButton, QApplication)
from PyQt6.QtGui import QShortcut, QPalette, QTextDocument, QTextCursor, QTextCharFormat, QTextFormat, QColor, QIcon, QPixmap
import html
from modules.notifier import Notifier
from modules.utils import get_time_until, format_date, format_time
from PyQt6.QtGui import QIcon, QPalette, QTextDocument, QTextCursor, QTextCharFormat, QTextFormat, QColor
import html
from modules.notifier import Notifier
from modules.utils import get_time_until, format_date, format_time

class TodoItem:
    """Represents a single to-do item with its properties and state."""
    
    PRIORITY_HIGH = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_LOW = 3
    
    PRIORITY_NAMES = {
        PRIORITY_HIGH: "High",
        PRIORITY_MEDIUM: "Medium",
        PRIORITY_LOW: "Low"
    }
    
    def __init__(self, title: str, description: str = "", due_date: str = "", 
                 priority: int = PRIORITY_MEDIUM, completed: bool = False, 
                 created_at: str = None, category: str = "General", 
                 reminder: str = ""):
        """
        Initialize a new to-do item.
        
        Args:
            title: The title of the to-do item
            description: Optional detailed description
            due_date: Due date in ISO format (YYYY-MM-DD)
            priority: Priority level (1=High, 2=Medium, 3=Low)
            completed: Whether the item is completed
            created_at: Creation timestamp in ISO format
            category: Category of the task (e.g., Work, Personal, Shopping)
            reminder: Reminder date/time in ISO format (YYYY-MM-DDTHH:MM)
        """
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.completed = completed
        self.category = category
        self.reminder = reminder
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = self.created_at
    
    @property
    def priority_name(self) -> str:
        """Get the priority level as a string."""
        return self.PRIORITY_NAMES.get(self.priority, "Medium")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the to-do item to a dictionary for serialization."""
        return {
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'priority': self.priority,
            'completed': self.completed,
            'category': self.category,
            'reminder': self.reminder,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TodoItem':
        """Create a TodoItem from a dictionary."""
        return cls(
            title=data.get('title', ''),
            description=data.get('description', ''),
            due_date=data.get('due_date', ''),
            priority=data.get('priority', cls.PRIORITY_MEDIUM),
            completed=data.get('completed', False),
            category=data.get('category', 'General'),
            reminder=data.get('reminder', ''),
            created_at=data.get('created_at')
        )
    
    def is_overdue(self) -> bool:
        """Check if the task is overdue."""
        if not self.due_date or self.completed:
            return False
        try:
            due = datetime.fromisoformat(self.due_date).date()
            return due < datetime.now().date()
        except (ValueError, TypeError):
            return False
    
    def needs_reminder(self) -> bool:
        """Check if a reminder should be shown for this task."""
        if not self.reminder or self.completed:
            return False
        try:
            reminder_time = datetime.fromisoformat(self.reminder)
            return reminder_time <= datetime.now()
        except (ValueError, TypeError):
            return False


class TodoList(QObject):
    """Manages a collection of to-do items with persistence."""
    
    data_changed = pyqtSignal()
    
    def __init__(self, storage_file: str = 'todos.json'):
        """
        Initialize the to-do list.
        
        Args:
            storage_file: Path to the JSON file for persistence
        """
        super().__init__()
        self.storage_file = storage_file
        self.todos: List[TodoItem] = []
        self.categories = set(['General', 'Work', 'Personal', 'Shopping'])
        self.load()
    
    def add(self, todo: TodoItem) -> None:
        """Add a new to-do item."""
        if todo.category and todo.category not in self.categories:
            self.categories.add(todo.category)
        self.todos.append(todo)
        self.save()
        self.data_changed.emit()
    
    def update(self, index: int, todo: TodoItem) -> None:
        """Update an existing to-do item."""
        if 0 <= index < len(self.todos):
            if todo.category and todo.category not in self.categories:
                self.categories.add(todo.category)
            todo.updated_at = datetime.now().isoformat()
            self.todos[index] = todo
            self.save()
            self.data_changed.emit()
    
    def delete(self, index: int) -> None:
        """Delete a to-do item by index."""
        if 0 <= index < len(self.todos):
            del self.todos[index]
            self.save()
            self.data_changed.emit()
    
    def get_categories(self) -> List[str]:
        """Get a sorted list of all categories."""
        return sorted(self.categories)
    
    def get_tasks_by_category(self, category: str = None) -> List[TodoItem]:
        """Get tasks filtered by category."""
        if not category:
            return self.todos
        return [todo for todo in self.todos if todo.category == category]
    
    def get_overdue_tasks(self) -> List[TodoItem]:
        """Get all overdue tasks."""
        return [todo for todo in self.todos if todo.is_overdue()]
    
    def get_tasks_due_today(self) -> List[TodoItem]:
        """Get all tasks due today."""
        today = datetime.now().date()
        today_tasks = []
        for todo in self.todos:
            if todo.due_date and not todo.completed:
                try:
                    due_date = datetime.fromisoformat(todo.due_date).date()
                    if due_date == today:
                        today_tasks.append(todo)
                except (ValueError, TypeError):
                    continue
        return today_tasks
    
    def get_upcoming_reminders(self) -> List[TodoItem]:
        """Get tasks with upcoming or active reminders."""
        now = datetime.now()
        upcoming = []
        for todo in self.todos:
            if todo.needs_reminder() and not todo.completed:
                upcoming.append(todo)
        return upcoming
    
    def toggle_complete(self, index: int) -> None:
        """Toggle the completion status of a to-do item."""
        if 0 <= index < len(self.todos):
            self.todos[index].completed = not self.todos[index].completed
            self.todos[index].updated_at = datetime.now().isoformat()
            self.save()
            self.data_changed.emit()
    
    def load(self) -> None:
        """Load to-do items from the storage file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'todos' in data:
                        # New format with metadata
                        self.todos = [TodoItem.from_dict(item) for item in data['todos']]
                        self.categories.update(data.get('categories', []))
                    else:
                        # Legacy format
                        self.todos = [TodoItem.from_dict(item) for item in data]
                        # Extract categories from existing todos
                        self.categories.update({todo.category for todo in self.todos if todo.category})
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading todos: {e}")
                self.todos = []
    
    def save(self) -> None:
        """Save to-do items to the storage file."""
        try:
            # Update categories from todos
            todo_categories = {todo.category for todo in self.todos if todo.category}
            self.categories.update(todo_categories)
            
            data = {
                'todos': [todo.to_dict() for todo in self.todos],
                'categories': list(self.categories),
                'saved_at': datetime.now().isoformat()
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error saving todos: {e}")


class TodoDialog(QDialog):
    """Dialog for adding or editing a to-do item."""
    
    def __init__(self, parent=None, todo: Optional[TodoItem] = None, categories: List[str] = None):
        """
        Initialize the dialog.
        
        Args:
            parent: Parent widget
            todo: Optional TodoItem to edit, or None to create a new one
            categories: List of available categories
        """
        super().__init__(parent)
        self.todo = todo or TodoItem("")
        self.categories = categories or ["General"]
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Add/Edit To-Do")
        layout = QVBoxLayout(self)
        
        # Form layout for better alignment
        form_layout = QFormLayout()
        
        # Title
        self.title_edit = QLineEdit(self.todo.title)
        form_layout.addRow("Title:", self.title_edit)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(self.categories)
        if self.todo.category and self.todo.category in self.categories:
            self.category_combo.setCurrentText(self.todo.category)
        form_layout.addRow("Category:", self.category_combo)
        
        # Due date
        self.date_edit = QLineEdit(self.todo.due_date)
        self.date_edit.setPlaceholderText("YYYY-MM-DD")
        form_layout.addRow("Due Date:", self.date_edit)
        
        # Reminder date/time
        self.reminder_edit = QLineEdit(self.todo.reminder)
        self.reminder_edit.setPlaceholderText("YYYY-MM-DD HH:MM")
        form_layout.addRow("Reminder:", self.reminder_edit)
        
        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItem("High", TodoItem.PRIORITY_HIGH)
        self.priority_combo.addItem("Medium", TodoItem.PRIORITY_MEDIUM)
        self.priority_combo.addItem("Low", TodoItem.PRIORITY_LOW)
        self.priority_combo.setCurrentIndex(self.priority_combo.findData(self.todo.priority))
        form_layout.addRow("Priority:", self.priority_combo)
        
        # Completed
        self.completed_check = QCheckBox()
        self.completed_check.setChecked(self.todo.completed)
        form_layout.addRow("Completed:", self.completed_check)
        
        # Description (takes more space)
        layout.addLayout(form_layout)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.desc_edit = QTextEdit(self.todo.description)
        self.desc_edit.setMaximumHeight(100)
        layout.addWidget(self.desc_edit)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add keyboard shortcuts
        self.title_edit.returnPressed.connect(self.accept)
        
        layout.addWidget(button_box)
    
    def get_todo(self):
        """
        Get the to-do item with updated values from the form.
        
        Returns:
            TodoItem: The updated to-do item
        """
        self.todo.title = self.title_edit.text().strip()
        self.todo.description = self.desc_edit.toPlainText().strip()
        self.todo.due_date = self.date_edit.text().strip()
        self.todo.reminder = self.reminder_edit.text().strip()
        self.todo.priority = self.priority_combo.currentData()
        self.todo.category = self.category_combo.currentText().strip() or "General"
        self.todo.completed = self.completed_check.isChecked()
        return self.todo


class TodoWidget(QWidget):
    """Widget that displays and manages the to-do list with filtering and sorting."""
    
    # Signal emitted when a reminder is triggered
    reminder_triggered = pyqtSignal(TodoItem)
    
    def __init__(self, todo_list: TodoList, parent=None):
        """
        Initialize the to-do widget.
        
        Args:
            todo_list: The TodoList instance to manage
            parent: Parent widget
        """
        super().__init__(parent)
        self.todo_list = todo_list
        self.current_filter = "all"  # all, active, completed, today, overdue
        self.current_category = None
        self.sort_by = "priority"  # priority, due_date, title
        self.sort_order = Qt.SortOrder.DescendingOrder  # Higher priority first
        
        # Initialize notifier
        self.notifier = Notifier()
        
        # Initialize UI components first
        self.setup_ui()
        
        # Connect signals after UI is set up
        self.todo_list.data_changed.connect(self.update_list)
        self.notifier.reminder_triggered.connect(self.handle_reminder)
        
        # Update the list after UI is fully initialized
        self.update_list()
        
        # Setup reminder timer
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(60000)  # Check every minute
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("<h2>To-Do List</h2>"))
        
        # Add button
        self.add_btn = QPushButton("Add Task")
        self.add_btn.clicked.connect(self.add_todo)
        header.addWidget(self.add_btn)
        
        layout.addLayout(header)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search tasks...")
        self.search_edit.textChanged.connect(self.update_list)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Filter and sort controls
        control_layout = QHBoxLayout()
        
        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Tasks", "Active", "Completed", "Due Today", "Overdue"])
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        control_layout.addWidget(QLabel("Filter:"))
        control_layout.addWidget(self.filter_combo)
        
        # Category filter
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        control_layout.addWidget(QLabel("Category:"))
        control_layout.addWidget(self.category_combo)
        
        # Sort dropdown
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Priority", "Due Date", "Title"])
        self.sort_combo.currentTextChanged.connect(self.on_sort_changed)
        control_layout.addWidget(QLabel("Sort by:"))
        control_layout.addWidget(self.sort_combo)
        
        layout.addLayout(control_layout)
        
        # Todo list
        self.todo_list_widget = QListWidget()
        self.todo_list_widget.itemDoubleClicked.connect(self.edit_todo)
        layout.addWidget(self.todo_list_widget)
        
        # Buttons for actions
        btn_layout = QHBoxLayout()
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_selected)
        
        self.toggle_btn = QPushButton("Toggle Complete")
        self.toggle_btn.clicked.connect(self.toggle_complete)
        
        # Add buttons to the button layout
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.toggle_btn)
        
        # Status bar at the bottom
        status_layout = QHBoxLayout()
        self.status_label = QLabel("No tasks")
        status_layout.addWidget(self.status_label)
        
        # Add stretch to push status to the right
        status_layout.addStretch()
        
        # Add all layouts to main layout
        layout.addLayout(btn_layout)
        layout.addLayout(status_layout)
    
    def get_filtered_tasks(self):
        """Get tasks filtered by current filter settings."""
        tasks = self.todo_list.todos
        
        # Apply status filter
        if self.current_filter == "active":
            tasks = [t for t in tasks if not t.completed]
        elif self.current_filter == "completed":
            tasks = [t for t in tasks if t.completed]
        elif self.current_filter == "today":
            today = datetime.now().date().isoformat()
            tasks = [t for t in tasks if t.due_date == today]
        elif self.current_filter == "overdue":
            tasks = [t for t in tasks if t.is_overdue() and not t.completed]
        
        # Apply category filter
        if self.current_category:
            tasks = [t for t in tasks if t.category == self.current_category]
        
        # Apply search filter
        search_text = self.search_edit.text().lower()
        if search_text:
            tasks = [t for t in tasks if 
                    search_text in t.title.lower() or 
                    (t.description and search_text in t.description.lower())]
        
        return tasks
    
    def sort_tasks(self, tasks):
        """Sort tasks based on current sort settings."""
        if self.sort_by == "priority":
            return sorted(tasks, 
                        key=lambda x: x.priority, 
                        reverse=(self.sort_order == Qt.SortOrder.DescendingOrder))
        elif self.sort_by == "due_date":
            return sorted(tasks, 
                        key=lambda x: (x.due_date or "9999-12-31", x.priority),
                        reverse=(self.sort_order == Qt.SortOrder.AscendingOrder))
        else:  # title
            return sorted(tasks, 
                        key=lambda x: x.title.lower(),
                        reverse=(self.sort_order == Qt.SortOrder.DescendingOrder))
    
    def update_list(self):
        """Update the list widget with filtered and sorted to-do items."""
        self.todo_list_widget.clear()
        
        # Get filtered tasks
        tasks = self.get_filtered_tasks()
        
        # Sort tasks
        tasks = self.sort_tasks(tasks)
        
        # Add tasks to the list
        for todo in tasks:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, todo)  # Store the todo object
            
            # Set tooltip with full details
            tooltip = self._get_todo_tooltip(todo)
            item.setToolTip(tooltip)
            
            # Format the display text
            status = "[✓]" if todo.completed else "[ ]"
            priority = ["🔴", "🟡", "🟢"][todo.priority - 1] if hasattr(todo, 'priority') and todo.priority else ""
            category = f"[{todo.category}] " if hasattr(todo, 'category') and todo.category else ""
            due_date = f" | 📅 {todo.due_date}" if hasattr(todo, 'due_date') and todo.due_date else ""
            
            # Add overdue indicator
            if hasattr(todo, 'is_overdue') and hasattr(todo, 'due_date') and todo.due_date and todo.is_overdue() and not todo.completed:
                due_date = f" | ⚠️ Overdue: {todo.due_date}"
            
            item.setText(f"{status} {priority} {category}{todo.title}{due_date}")
            
            # Styling
            font = item.font()
            if todo.completed:
                font.setStrikeOut(True)
                item.setForeground(Qt.GlobalColor.gray)
            elif hasattr(todo, 'is_overdue') and todo.is_overdue() and not todo.completed:
                font.setBold(True)
                item.setForeground(Qt.GlobalColor.red)
            
            item.setFont(font)
            self.todo_list_widget.addItem(item)
        
        # Update status bar
        total = len(self.todo_list.todos)
        shown = len(tasks)
        self.status_label.setText(f"Showing {shown} of {total} tasks")
    
    def _get_todo_tooltip(self, todo):
        """Generate a tooltip for a todo item."""
        lines = [f"<b>{todo.title}</b>"]
        
        if hasattr(todo, 'category') and todo.category:
            lines.append(f"Category: {todo.category}")
        
        if hasattr(todo, 'priority'):
            priority_names = {1: "High", 2: "Medium", 3: "Low"}
            lines.append(f"Priority: {priority_names.get(todo.priority, 'Medium')}")
        
        if hasattr(todo, 'due_date') and todo.due_date:
            status = "Overdue" if hasattr(todo, 'is_overdue') and todo.is_overdue() and not todo.completed else "Due"
            lines.append(f"{status}: {todo.due_date}")
        
        if hasattr(todo, 'reminder') and todo.reminder:
            lines.append(f"Reminder: {todo.reminder}")
        
        if hasattr(todo, 'description') and todo.description:
            lines.extend(["", todo.description])
        
        return "<br>".join(lines)
    
    def update_categories(self):
        """Update the category dropdown with current categories."""
        current = self.category_combo.currentData()
        self.category_combo.clear()
        self.category_combo.addItem("All Categories", None)
        
        # Get unique categories from todos
        categories = set()
        for todo in self.todo_list.todos:
            if hasattr(todo, 'category') and todo.category:
                categories.add(todo.category)
        
        # Add categories to dropdown
        for category in sorted(categories):
            self.category_combo.addItem(category, category)
        
        # Restore selection if possible
        if current in categories:
            idx = self.category_combo.findText(current)
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
    
    def on_filter_changed(self, text):
        """Handle filter selection change."""
        self.current_filter = text.lower().replace(" ", "")
        self.update_list()
    
    def on_category_changed(self, index):
        """Handle category filter change."""
        self.current_category = self.category_combo.currentData()
        self.update_list()
    
    def on_sort_changed(self, text):
        """Handle sort selection change."""
        self.sort_by = text.lower().replace(" ", "_")
        self.update_list()
    
    def add_todo(self):
        """Show dialog to add a new to-do item."""
        dialog = TodoDialog(self, categories=self.todo_list.get_categories())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            todo = dialog.get_todo()
            if todo.title:  # Don't add empty titles
                self.todo_list.add(todo)
                # Update categories in case a new one was added
                self.update_categories()
    
    def show_context_menu(self, position):
        """Show context menu for the selected task."""
        item = self.todo_list_widget.itemAt(position)
        if not item:
            return
            
        todo = item.data(Qt.ItemDataRole.UserRole)
        if not todo:
            return
            
        menu = QMenu(self)
        
        # Toggle complete action
        status = "Mark Complete" if not todo.completed else "Mark Incomplete"
        toggle_action = menu.addAction(status)
        toggle_action.triggered.connect(self.toggle_complete)
        
        # Edit action
        edit_action = menu.addAction("Edit")
        edit_action.triggered.connect(lambda: self.edit_todo(item))
        
        # Delete action
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(self.delete_selected)
        
        menu.addSeparator()
        
        # Priority submenu
        priority_menu = menu.addMenu("Set Priority")
        
        high_action = priority_menu.addAction("High")
        high_action.triggered.connect(lambda: self.set_priority(todo, 1))
        
        medium_action = priority_menu.addAction("Medium")
        medium_action.triggered.connect(lambda: self.set_priority(todo, 2))
        
        low_action = priority_menu.addAction("Low")
        low_action.triggered.connect(lambda: self.set_priority(todo, 3))
        
        menu.exec(self.todo_list_widget.viewport().mapToGlobal(position))
    
    def set_priority(self, todo, priority):
        """Set the priority of a task."""
        if todo in self.todo_list.todos:
            index = self.todo_list.todos.index(todo)
            todo.priority = priority
            self.todo_list.update(index, todo)
    
    def handle_reminder(self, todo_data: dict):
        """Handle a reminder notification.
        
        Args:
            todo_data: Dictionary containing todo item data
        """
        # Find the corresponding TodoItem
        todo = None
        for t in self.todo_list.todos:
            if (t.title == todo_data.get("title") and 
                t.due_date == todo_data.get("due_date") and 
                t.reminder == todo_data.get("reminder")):
                todo = t
                break
                
        if todo:
            # Show a message box for the reminder
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Reminder")
            msg.setText(f"Reminder: {todo.title}")
            
            # Add more details to the message
            details = []
            if todo.due_date:
                details.append(f"Due: {todo.due_date}")
            if todo.description:
                details.append(f"Description: {todo.description}")
                
            if details:
                msg.setInformativeText("\n".join(details))
                
            # Add buttons
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Snooze)
            msg.setDefaultButton(QMessageBox.StandardButton.Ok)
            
            # Show the message box
            result = msg.exec()
            
            # Handle snooze if needed
            if result == QMessageBox.StandardButton.Snooze:
                # Implement snooze logic here if needed
                pass
    
    def check_reminders(self):
        """Check for tasks with upcoming reminders and trigger notifications."""
        # This method is called periodically by the reminder_timer
        # It checks for tasks that need reminders and triggers notifications
        upcoming = self.todo_list.get_upcoming_reminders()
        for todo in upcoming:
            # Create a todo_data dictionary for the handle_reminder method
            todo_data = {
                "title": todo.title,
                "due_date": todo.due_date,
                "reminder": todo.reminder,
                "description": todo.description,
                "priority": todo.priority,
                "category": todo.category,
                "completed": todo.completed
            }
            # Trigger the reminder
            self.handle_reminder(todo_data)
        
        if todo:
            # Emit our own signal for UI updates
            self.reminder_triggered.emit(todo)
            
            # Optionally show a message box
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("MAYA Reminder")
            msg.setText(f"Reminder: {todo.title}")
            
            if todo.due_date:
                msg.setInformativeText(f"Due: {format_date(todo.due_date)}")
            
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
    
    def edit_todo(self, item):
        """Edit the selected to-do item."""
        if not item:
            return
            
        todo = item.data(Qt.ItemDataRole.UserRole)
        if todo in self.todo_list.todos:
            index = self.todo_list.todos.index(todo)
            dialog = TodoDialog(self, todo, self.todo_list.get_categories())
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_todo = dialog.get_todo()
                if updated_todo.title:  # Don't update with empty title
                    self.todo_list.update(index, updated_todo)
                    # Update categories in case a new one was added
                    self.update_categories()
    
    def delete_selected(self):
        """Delete the selected to-do item."""
        current_row = self.todo_list_widget.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self, 
                'Delete Task', 
                'Are you sure you want to delete this task?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.todo_list.delete(current_row)
    
    def toggle_complete(self):
        """Toggle the completion status of the selected to-do item."""
        current_row = self.todo_list_widget.currentRow()
        if current_row >= 0:
            self.todo_list.toggle_complete(current_row)
