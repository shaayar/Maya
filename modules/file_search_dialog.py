"""
File Search Dialog for MAYA AI Chatbot.
Provides a powerful file search interface with preview capabilities.
"""

import os
from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QPushButton,
    QLabel, QComboBox, QCheckBox, QSplitter, QTextEdit, QFileIconProvider,
    QTreeView, QAbstractItemView, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QSize, QDir, QModelIndex, pyqtSignal
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtGui import QIcon, QTextCursor, QTextCharFormat, QTextFormat, QColor, QPixmap

from .file_operations import FileManager
from .styles import get_styles


class FileSearchDialog(QDialog):
    """Dialog for searching and selecting files in the project."""
    
    file_selected = pyqtSignal(str)  # Signal emitted when a file is selected
    
    def __init__(self, parent=None, initial_dir: str = None):
        """Initialize the file search dialog.
        
        Args:
            parent: Parent widget
            initial_dir: Initial directory to search in (defaults to current directory)
        """
        super().__init__(parent)
        self.setWindowTitle("Find in Files")
        self.setMinimumSize(800, 600)
        
        self.initial_dir = initial_dir or os.getcwd()
        self.current_file = None
        self.search_results = []
        self.icon_provider = QFileIconProvider()
        
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Search controls
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files...")
        self.search_input.returnPressed.connect(self.perform_search)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        
        search_layout.addWidget(self.search_input, 4)
        search_layout.addWidget(self.search_button, 1)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItem("All Files", "*")
        self.file_type_combo.addItem("Python Files", ".py")
        self.file_type_combo.addItem("Text Files", ".txt")
        self.file_type_combo.addItem("Markdown", ".md")
        self.file_type_combo.addItem("HTML", ".html")
        self.file_type_combo.addItem("JavaScript", ".js")
        self.file_type_combo.addItem("CSS", ".css")
        
        self.search_content_check = QCheckBox("Search in file contents")
        self.case_sensitive_check = QCheckBox("Case sensitive")
        
        filter_layout.addWidget(QLabel("File Type:"))
        filter_layout.addWidget(self.file_type_combo)
        filter_layout.addWidget(self.search_content_check)
        filter_layout.addWidget(self.case_sensitive_check)
        filter_layout.addStretch()
        
        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - File explorer
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(self.initial_dir)
        self.file_system_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
        
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_system_model)
        self.file_tree.setRootIndex(self.file_system_model.index(self.initial_dir))
        self.file_tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.file_tree.setAnimated(False)
        self.file_tree.setIndentation(20)
        self.file_tree.setSortingEnabled(True)
        self.file_tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.file_tree.setColumnWidth(0, 250)
        self.file_tree.doubleClicked.connect(self.on_file_double_clicked)
        
        # Right panel - Search results and preview
        right_panel = QVBoxLayout()
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemSelectionChanged.connect(self.on_result_selected)
        self.results_list.itemDoubleClicked.connect(self.open_selected_file)
        
        # Preview area
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Add to right panel
        right_panel.addWidget(QLabel("Search Results:"))
        right_panel.addWidget(self.results_list, 2)
        right_panel.addWidget(QLabel("Preview:"))
        right_panel.addWidget(self.preview_area, 1)
        
        # Create a widget to hold the right panel layout
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        # Add widgets to splitter
        splitter.addWidget(self.file_tree)
        splitter.addWidget(right_widget)
        splitter.setSizes([200, 600])  # Initial sizes
        
        # Buttons
        button_layout = QHBoxLayout()
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.open_selected_file)
        self.open_button.setEnabled(False)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.cancel_button)
        
        # Assemble main layout
        main_layout.addLayout(search_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(splitter, 1)
        main_layout.addLayout(button_layout)
        
        # Set focus to search input
        self.search_input.setFocus()
    
    def apply_styles(self):
        """Apply styles to the dialog."""
        self.setStyleSheet(get_styles())
        
        # Additional styling specific to the file search dialog
        self.search_button.setStyleSheet(
            "QPushButton { padding: 5px 15px; }"
        )
        
        self.results_list.setStyleSheet(
            "QListWidget { border: 1px solid #444; border-radius: 4px; }"
            "QListWidget::item { padding: 4px; }"
            "QListWidget::item:selected { background-color: #2a82da; color: white; }"
        )
        
        self.preview_area.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #a9b7c6;
                border: 1px solid #444;
                border-radius: 4px;
                font-family: 'Consolas', 'Monospace';
            }
        """)
    
    def perform_search(self):
        """Perform a file search based on the current filters."""
        search_text = self.search_input.text().strip()
        if not search_text and not self.search_content_check.isChecked():
            return
        
        self.results_list.clear()
        self.search_results = []
        
        # Get search parameters
        file_type = self.file_type_combo.currentData()
        search_in_content = self.search_content_check.isChecked()
        case_sensitive = self.case_sensitive_check.isChecked()
        
        # Determine search directory from the file tree selection
        selected_indexes = self.file_tree.selectedIndexes()
        if selected_indexes:
            search_dir = self.file_system_model.filePath(selected_indexes[0])
            if not os.path.isdir(search_dir):
                search_dir = os.path.dirname(search_dir)
        else:
            search_dir = self.initial_dir
        
        # Prepare file filters
        file_types = [file_type] if file_type != "*" else None
        
        # Perform the search
        results = FileManager.find_files(
            root_dir=search_dir,
            pattern=f"*{search_text}*" if not search_in_content else "*",
            content_search=search_text if search_in_content else None,
            file_types=file_types,
            max_depth=10
        )
        
        # Display results
        for file_info in results:
            self.search_results.append(file_info)
            
            # Create a list item with icon and text
            item_text = f"{os.path.basename(file_info['path'])} - {os.path.dirname(file_info['path'])}"
            self.results_list.addItem(item_text)
            
            # Set icon based on file type
            icon = self.icon_provider.icon(file_info['path'])
            self.results_list.item(self.results_list.count() - 1).setIcon(icon)
        
        # Update status
        status = f"Found {len(self.search_results)} results"
        self.statusBar().showMessage(status) if hasattr(self, 'statusBar') else None
    
    def on_result_selected(self):
        """Handle selection of a search result."""
        selected_items = self.results_list.selectedItems()
        if not selected_items:
            self.open_button.setEnabled(False)
            return
        
        self.open_button.setEnabled(True)
        self.current_file = self.search_results[self.results_list.row(selected_items[0])]['path']
        self.update_preview()
    
    def on_file_double_clicked(self, index):
        """Handle double-click on a file in the file tree."""
        file_path = self.file_system_model.filePath(index)
        if os.path.isfile(file_path):
            self.current_file = file_path
            self.accept()
    
    def update_preview(self):
        """Update the preview area with the selected file's content."""
        if not self.current_file or not os.path.isfile(self.current_file):
            self.preview_area.clear()
            return
        
        try:
            with open(self.current_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Simple syntax highlighting for common file types
                self.preview_area.clear()
                
                # For now, just show plain text
                # In a real implementation, you'd want to add syntax highlighting here
                self.preview_area.setPlainText(content)
                
                # Highlight search term if there is one
                search_text = self.search_input.text().strip()
                if search_text:
                    self.highlight_text(search_text)
                    
        except Exception as e:
            self.preview_area.setPlainText(f"Error reading file: {str(e)}")
    
    def highlight_text(self, text):
        """Highlight all occurrences of the given text in the preview."""
        if not text:
            return
            
        cursor = self.preview_area.document().find(text, 0)
        
        # Highlight all occurrences
        format_ = QTextCharFormat()
        format_.setBackground(QColor(255, 255, 0, 100))  # Yellow highlight
        
        while not cursor.isNull():
            # Highlight the match
            cursor.mergeCharFormat(format_)
            # Move to next occurrence
            cursor = self.preview_area.document().find(text, cursor)
    
    def open_selected_file(self):
        """Open the selected file and close the dialog."""
        if self.current_file and os.path.isfile(self.current_file):
            self.file_selected.emit(self.current_file)
            self.accept()
    
    def get_selected_file(self) -> Optional[str]:
        """Get the currently selected file path."""
        return self.current_file


if __name__ == "__main__":
    # For testing the dialog
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = FileSearchDialog(initial_dir=os.getcwd())
    if dialog.exec() == QDialog.DialogCode.Accepted:
        print("Selected file:", dialog.get_selected_file())
    sys.exit()
