"""
MCP (Model Control Protocol) Settings Dialog

This module provides a settings dialog for configuring MCP connections.
"""
from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QDoubleSpinBox, QCheckBox, QDialogButtonBox,
    QComboBox, QFormLayout, QGroupBox, QMessageBox, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread, pyqtSlot

from .mcp_client import MCPClient
import asyncio
import aiohttp
import logging

logger = logging.getLogger(__name__)

class MCPWorker(QObject):
    """Worker for async MCP operations."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    models_loaded = pyqtSignal(list)
    
    def __init__(self, base_url: str, timeout: float, max_retries: int):
        super().__init__()
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
    
    async def get_models_async(self):
        """Fetch available models from MCP server."""
        try:
            async with MCPClient(
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=self.max_retries
            ) as client:
                models = await client.get_models()
                self.models_loaded.emit([model['id'] for model in models if 'id' in model])
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class MCPSettingsDialog(QDialog):
    """Dialog for configuring MCP connection settings."""
    
    settings_updated = pyqtSignal(dict)
    
    def __init__(self, config: Dict[str, Any], parent=None):
        """Initialize the MCP settings dialog.
        
        Args:
            config: Current configuration dictionary
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.mcp_config = config.get('mcp', {})
        self.available_models: List[str] = []
        
        self.setWindowTitle("MCP Settings")
        self.setMinimumWidth(500)
        
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Enable MCP
        self.enable_checkbox = QCheckBox("Enable MCP")
        self.enable_checkbox.toggled.connect(self._on_enable_toggled)
        layout.addWidget(self.enable_checkbox)
        
        # Connection group
        conn_group = QGroupBox("Connection Settings")
        conn_layout = QFormLayout()
        
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setPlaceholderText("http://localhost:8080")
        conn_layout.addRow("Base URL:", self.base_url_edit)
        
        self.timeout_spin = QDoubleSpinBox()
        self.timeout_spin.setRange(1.0, 300.0)
        self.timeout_spin.setSuffix(" s")
        conn_layout.addRow("Timeout:", self.timeout_spin)
        
        self.retries_spin = QSpinBox()
        self.retries_spin.setRange(0, 10)
        conn_layout.addRow("Max Retries:", self.retries_spin)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # Model group
        model_group = QGroupBox("Model Settings")
        model_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        model_layout.addRow("Default Model:", self.model_combo)
        
        self.refresh_btn = QPushButton("Refresh Models")
        self.refresh_btn.clicked.connect(self._refresh_models)
        model_layout.addRow("", self.refresh_btn)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Reset
        )
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._apply_settings)
        button_box.button(QDialogButtonBox.StandardButton.Reset).clicked.connect(self._reset_to_defaults)
        
        layout.addWidget(button_box)
        
        # Set up worker thread
        self.thread = QThread()
        self.worker = None
    
    def _load_settings(self):
        """Load current settings into the UI."""
        # Connection settings
        self.enable_checkbox.setChecked(self.mcp_config.get('enabled', False))
        self.base_url_edit.setText(self.mcp_config.get('base_url', 'http://localhost:8080'))
        self.timeout_spin.setValue(float(self.mcp_config.get('timeout', 30.0)))
        self.retries_spin.setValue(int(self.mcp_config.get('max_retries', 3)))
        
        # Model settings
        default_model = self.mcp_config.get('default_model', 'gpt-3.5-turbo')
        self.model_combo.addItem(default_model)
        self.model_combo.setCurrentText(default_model)
        
        # Update UI state
        self._on_enable_toggled(self.enable_checkbox.isChecked())
    
    def _on_enable_toggled(self, enabled: bool):
        """Handle enable/disable of MCP settings."""
        for widget in [
            self.base_url_edit, self.timeout_spin, 
            self.retries_spin, self.model_combo, self.refresh_btn
        ]:
            widget.setEnabled(enabled)
    
    def _refresh_models(self):
        """Fetch available models from the MCP server."""
        base_url = self.base_url_edit.text().strip()
        if not base_url:
            QMessageBox.warning(self, "Error", "Please enter a valid base URL")
            return
            
        # Disable UI during operation
        self.setEnabled(False)
        self.refresh_btn.setText("Loading...")
        
        # Create worker and thread
        self.worker = MCPWorker(
            base_url=base_url,
            timeout=self.timeout_spin.value(),
            max_retries=self.retries_spin.value()
        )
        
        # Move worker to thread
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(
            lambda: asyncio.run(self.worker.get_models_async())
        )
        self.worker.finished.connect(self._on_models_loaded)
        self.worker.error.connect(self._on_models_error)
        self.worker.models_loaded.connect(self._update_models_list)
        
        # Start the thread
        self.thread.start()
    
    @pyqtSlot(list)
    def _update_models_list(self, models: List[str]):
        """Update the models dropdown with the fetched models."""
        self.available_models = models
        self.model_combo.clear()
        self.model_combo.addItems(models)
        
        # Try to select the previously selected model if it exists
        current_model = self.mcp_config.get('default_model')
        if current_model in models:
            self.model_combo.setCurrentText(current_model)
        
        QMessageBox.information(
            self, "Success", 
            f"Successfully loaded {len(models)} models from the server."
        )
    
    @pyqtSlot()
    def _on_models_loaded(self):
        """Clean up after models are loaded."""
        self.thread.quit()
        self.thread.wait()
        self.setEnabled(True)
        self.refresh_btn.setText("Refresh Models")
    
    @pyqtSlot(str)
    def _on_models_error(self, error: str):
        """Handle errors during model loading."""
        QMessageBox.critical(
            self, "Error", 
            f"Failed to fetch models: {error}"
        )
        self._on_models_loaded()  # Clean up
    
    def _get_settings(self) -> Dict[str, Any]:
        """Get the current settings from the UI."""
        return {
            'mcp': {
                'enabled': self.enable_checkbox.isChecked(),
                'base_url': self.base_url_edit.text().strip(),
                'timeout': self.timeout_spin.value(),
                'max_retries': self.retries_spin.value(),
                'default_model': self.model_combo.currentText(),
                'endpoints': self.mcp_config.get('endpoints', {
                    'completions': '/v1/completions',
                    'chat': '/v1/chat/completions',
                    'models': '/v1/models'
                })
            }
        }
    
    def _apply_settings(self):
        """Apply the current settings."""
        settings = self._get_settings()
        self.settings_updated.emit(settings)
        QMessageBox.information(self, "Success", "MCP settings saved successfully!")
    
    def _reset_to_defaults(self):
        """Reset settings to default values."""
        from .config import DEFAULT_CONFIG
        default_mcp = DEFAULT_CONFIG.get('mcp', {})
        
        self.enable_checkbox.setChecked(default_mcp.get('enabled', False))
        self.base_url_edit.setText(default_mcp.get('base_url', 'http://localhost:8080'))
        self.timeout_spin.setValue(float(default_mcp.get('timeout', 30.0)))
        self.retries_spin.setValue(int(default_mcp.get('max_retries', 3)))
        
        # Update model list
        self.model_combo.clear()
        default_model = default_mcp.get('default_model', 'gpt-3.5-turbo')
        self.model_combo.addItem(default_model)
        self.model_combo.setCurrentText(default_model)
    
    def accept(self):
        """Handle OK button click."""
        self._apply_settings()
        super().accept()
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.thread.quit()
        self.thread.wait()
        super().closeEvent(event)
