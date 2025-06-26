import sys
import os
import unittest
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication
from modules.todo import TodoItem, TodoList, TodoWidget, TodoDialog

# Initialize QApplication for testing
app = QApplication(sys.argv)

class TestTodoItem(unittest.TestCase):
    def test_todo_creation(self):
        """Test creating a new todo item."""
        todo = TodoItem("Test Task", "Test Description", "2023-01-01")
        self.assertEqual(todo.title, "Test Task")
        self.assertEqual(todo.description, "Test Description")
        self.assertEqual(todo.due_date, "2023-01-01")
        self.assertFalse(todo.completed)

    def test_is_overdue(self):
        """Test overdue status calculation."""
        # Create a task that's due yesterday
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        todo = TodoItem("Overdue Task", "", yesterday)
        self.assertTrue(todo.is_overdue())
        
        # Completed tasks shouldn't be overdue
        todo.completed = True
        self.assertFalse(todo.is_overdue())

class TestTodoList(unittest.TestCase):
    def setUp(self):
        """Set up a clean TodoList for each test."""
        self.todo_list = TodoList(":memory:")
        
    def test_add_todo(self):
        """Test adding a todo to the list."""
        initial_count = len(self.todo_list.todos)
        todo = TodoItem("New Task")
        self.todo_list.add(todo)
        self.assertEqual(len(self.todo_list.todos), initial_count + 1)
        
    def test_toggle_complete(self):
        """Test toggling todo completion status."""
        todo = TodoItem("Task to Toggle")
        self.todo_list.add(todo)
        self.assertFalse(self.todo_list.todos[0].completed)
        self.todo_list.toggle_complete(0)
        self.assertTrue(self.todo_list.todos[0].completed)
        
    def test_get_categories(self):
        """Test getting unique categories."""
        self.todo_list.add(TodoItem("Task 1", category="Work"))
        self.todo_list.add(TodoItem("Task 2", category="Personal"))
        self.todo_list.add(TodoItem("Task 3", category="Work"))
        
        categories = self.todo_list.get_categories()
        # Check that we have at least the expected categories
        self.assertIn("Work", categories)
        self.assertIn("Personal", categories)
        self.assertIn("General", categories)
        self.assertIn("Shopping", categories)  # Default category from TodoList.__init__

class TestTodoWidget(unittest.TestCase):
    def setUp(self):
        """Set up a clean TodoWidget for each test."""
        self.todo_list = TodoList(":memory:")
        self.widget = TodoWidget(self.todo_list)
        self.widget.show()
        
    def test_initial_state(self):
        """Test the initial state of the widget."""
        self.assertEqual(self.widget.current_filter, "all")
        self.assertIsNone(self.widget.current_category)
        self.assertEqual(self.widget.sort_by, "priority")
        
    def test_add_and_display_task(self):
        """Test adding and displaying a task."""
        # Add a test task
        test_task = TodoItem("Test Task", "Test Description", "2023-01-01")
        self.todo_list.add(test_task)
        
        # Force UI update
        self.widget.update_list()
        
        # Check if task is displayed
        self.assertEqual(self.widget.todo_list_widget.count(), 1)
        
    def test_filtering(self):
        """Test task filtering functionality."""
        # Add test tasks
        self.todo_list.add(TodoItem("Task 1", completed=True))
        self.todo_list.add(TodoItem("Task 2", completed=False))
        
        # Test active filter
        self.widget.on_filter_changed("Active")
        self.assertEqual(len(self.widget.get_filtered_tasks()), 1)
        
        # Test completed filter
        self.widget.on_filter_changed("Completed")
        self.assertEqual(len(self.widget.get_filtered_tasks()), 1)

if __name__ == "__main__":
    unittest.main()
