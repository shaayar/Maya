"""
Screen Capture Dialog for MAYA AI Chatbot.
Provides a user interface for capturing and manipulating screen regions.
"""
import os
import logging
from typing import Optional, Tuple, Callable, Dict, Any

from enum import Enum, auto
import math

from PyQt6.QtCore import Qt, QRect, QPoint, QPointF, QSize, QDateTime, pyqtSignal, QRectF, QTimer
from PyQt6.QtGui import (
    QGuiApplication, QPixmap, QPainter, QPen, QColor, QBrush, QImage,
    QScreen, QRegion, QPainterPath, QPolygonF, QKeyEvent
)
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QSizePolicy,
    QApplication, QMessageBox, QFileDialog, QSpinBox, QCheckBox,
    QDockWidget, QWidget, QToolBar, QStatusBar, QMainWindow, QColorDialog,
    QTextEdit, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QComboBox
)

from .screen_manipulation import ScreenRegion, ScreenCapture
from .ocr_processor import OCRProcessor, install_tesseract_windows, install_tesseract_macos, install_tesseract_linux
import platform
import sys


class ToolType(Enum):
    """Enumeration of available annotation tools."""
    SELECT = auto()
    RECTANGLE = auto()
    ELLIPSE = auto()
    ARROW = auto()
    LINE = auto()
    FREEHAND = auto()
    TEXT = auto()
    HIGHLIGHT = auto()
    BLUR = auto()
    CROP = auto()

logger = logging.getLogger(__name__)

class ScreenCaptureDialog(QMainWindow):
    """Dialog for capturing screen regions with interactive selection."""
    
    capture_completed = pyqtSignal(QPixmap, dict)  # pixmap, metadata
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the screen capture dialog."""
        super().__init__(parent, Qt.WindowType.WindowStaysOnTopHint)
        
        self.setWindowTitle("Screen Capture")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # Set window flags to make it frameless and always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.X11BypassWindowManagerHint
        )
        
        # Make the window transparent for click-through
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Initialize screen capture
        self.screen_capture = ScreenCapture()
        
        # Selection state
        self.selection_start = QPoint()
        self.selection_end = QPoint()
        self.is_selecting = False
        self.selection_rect = QRect()
        
        # Annotation state
        self.annotation_mode = False
        self.current_annotation = None
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # UI components
        self.init_ui()
        
        # Capture the entire screen as background
        self.background_pixmap = None
        self.capture_full_screen()
        
        # Set window size to match primary screen
        screen = QGuiApplication.primaryScreen()
        self.setGeometry(screen.availableGeometry())
        
        # Initialize the current annotation dictionary
        self.current_annotation: Dict[str, Any] = {}
    
    def init_ui(self):
        """Initialize the user interface."""
        # Create toolbar
        self.toolbar = self.addToolBar("Tools")
        self.toolbar.setMovable(False)
        
        # Add toolbar actions
        self.select_btn = self.toolbar.addAction("Select")
        self.rect_btn = self.toolbar.addAction("Rectangle")
        self.ellipse_btn = self.toolbar.addAction("Ellipse")
        self.arrow_btn = self.toolbar.addAction("Arrow")
        self.line_btn = self.toolbar.addAction("Line")
        self.text_btn = self.toolbar.addAction("Text")
        self.highlight_btn = self.toolbar.addAction("Highlight")
        
        self.toolbar.addSeparator()
        
        # Color button
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(24, 24)
        self.color_btn.setStyleSheet("background-color: red;")
        self.color_btn.clicked.connect(self.select_color)
        self.toolbar.addWidget(self.color_btn)
        
        # Line width
        self.toolbar.addWidget(QLabel("Width:"))
        self.line_width = QSpinBox()
        self.line_width.setRange(1, 20)
        self.line_width.setValue(2)
        self.toolbar.addWidget(self.line_width)
        
        # Fill checkbox
        self.fill_check = QCheckBox("Fill")
        self.toolbar.addWidget(self.fill_check)
        
        # Add stretch to push everything to the left
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar.addWidget(spacer)
        
        # Add OCR button
        self.ocr_btn = QPushButton("Extract Text")
        self.ocr_btn.clicked.connect(self.extract_text_from_selection)
        self.ocr_btn.setEnabled(False)
        self.toolbar.addWidget(self.ocr_btn)
        
        # Add language selector
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "eng")
        self.lang_combo.addItem("Spanish", "spa")
        self.lang_combo.addItem("French", "fra")
        self.lang_combo.addItem("German", "deu")
        self.toolbar.addWidget(QLabel("Language:"))
        self.toolbar.addWidget(self.lang_combo)
        
        # Add standard buttons
        self.capture_btn = QPushButton("Capture")
        self.capture_btn.clicked.connect(self.accept_capture)
        self.toolbar.addWidget(self.capture_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.toolbar.addWidget(self.cancel_btn)
        
        # Initialize OCR processor
        self.ocr_processor = OCRProcessor()
        
        # Check if Tesseract is installed
        try:
            import pytesseract
            self.tesseract_installed = True
        except ImportError:
            self.tesseract_installed = False
            self.ocr_btn.setToolTip("Tesseract OCR is not installed. Click for installation instructions.")
            self.ocr_btn.setEnabled(False)
        
        # Graphics view for displaying the screen and selection
        self.graphics_view = QGraphicsView(self)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_view.setFrameShape(QFrame.Shape.NoFrame)
        self.graphics_view.setMouseTracking(True)
        
        # Graphics scene
        self.scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)
        
        # Add to layout
        self.main_layout.addWidget(self.graphics_view)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Set window opacity for better visibility
        self.setWindowOpacity(0.9)
        
        # Connect signals
        self.select_btn.triggered.connect(lambda: self.set_annotation_mode(False))
        self.rect_btn.triggered.connect(lambda: self.start_annotation(ToolType.RECTANGLE))
        self.ellipse_btn.triggered.connect(lambda: self.start_annotation(ToolType.ELLIPSE))
        self.arrow_btn.triggered.connect(lambda: self.start_annotation(ToolType.ARROW))
        self.line_btn.triggered.connect(lambda: self.start_annotation(ToolType.LINE))
        self.text_btn.triggered.connect(lambda: self.start_annotation(ToolType.TEXT))
        self.highlight_btn.triggered.connect(lambda: self.start_annotation(ToolType.HIGHLIGHT))
    
    def capture_full_screen(self):
        """Capture the full screen and display it in the dialog."""
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            logger.error("Could not get primary screen")
            return
            
        self.background_pixmap = screen.grabWindow(0)
        self.update_display()
    
    def update_display(self):
        """Update the display with the current background, selection, and annotations."""
        # Enable/disable OCR button based on selection
        self.ocr_btn.setEnabled(not self.selection_rect.isNull() and self.tesseract_installed)
        if self.background_pixmap is None:
            return
            
        # Create a copy of the background
        display_pixmap = self.background_pixmap.copy()
        painter = QPainter(display_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw semi-transparent overlay (only outside selection in non-annotation mode)
        if not self.annotation_mode and (self.is_selecting or not self.selection_rect.isNull()):
            overlay = QPixmap(display_pixmap.size())
            overlay.fill(Qt.GlobalColor.black)
            overlay.setAlpha(128)  # 50% transparency
            
            # Create a path that covers the entire image except the selection
            path = QPainterPath()
            path.addRect(display_pixmap.rect())
            if not self.selection_rect.isNull():
                path.addRect(self.selection_rect.normalized())
            
            # Draw the overlay with the path as a mask
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, overlay)
            painter.setClipping(False)
            
            # Draw selection rectangle
            painter.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.selection_rect.normalized())
        
        # Draw current annotation in progress
        if self.annotation_mode and self.current_annotation and self.current_annotation['start_pos']:
            self._draw_annotation(painter, self.current_annotation)
        
        # Draw size info for selection
        if not self.selection_rect.isNull():
            rect = self.selection_rect.normalized()
            size_text = f"{rect.width()} x {rect.height()}"
            
            # Draw text with background for better visibility
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            
            text_rect = painter.boundingRect(rect, Qt.AlignmentFlag.AlignCenter, size_text)
            text_rect.moveBottomLeft(rect.bottomLeft() + QPoint(0, 20))
            
            # Ensure text is visible
            text_rect.adjust(-2, -2, 2, 2)
            painter.fillRect(text_rect, QColor(0, 0, 0, 180))
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, size_text)
        
        painter.end()
        
        # Update the scene
        self.scene.clear()
        self.scene.addPixmap(display_pixmap)
        self.graphics_view.setSceneRect(display_pixmap.rect())
    
    def _draw_annotation(self, painter: QPainter, annotation: dict):
        """Draw an annotation on the painter."""
        if not annotation or 'start_pos' not in annotation or 'end_pos' not in annotation:
            return
        
        # Set up pen and brush
        pen = QPen(annotation.get('color', Qt.GlobalColor.red))
        pen.setWidth(annotation.get('line_width', 2))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        
        painter.setPen(pen)
        
        if annotation.get('filled', False):
            painter.setBrush(QBrush(annotation['color']))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Draw based on annotation type
        tool_type = annotation.get('type', ToolType.RECTANGLE)
        start = annotation['start_pos']
        end = annotation['end_pos']
        
        if tool_type == ToolType.RECTANGLE:
            painter.drawRect(QRectF(start, end).normalized())
        elif tool_type == ToolType.ELLIPSE:
            painter.drawEllipse(QRectF(start, end).normalized())
        elif tool_type == ToolType.ARROW:
            self._draw_arrow(painter, start, end, pen)
        elif tool_type == ToolType.LINE:
            painter.drawLine(start, end)
        elif tool_type == ToolType.HIGHLIGHT:
            self._draw_highlight(painter, start, end, pen)
    
    def _draw_arrow(self, painter: QPainter, start: QPointF, end: QPointF, pen: QPen):
        """Draw an arrow from start to end."""
        # Draw the line
        painter.drawLine(start, end)
        
        # Draw arrow head
        arrow_size = pen.width() * 4
        angle = (end - start).angle() * 3.14159 / 180.0
        
        p1 = end - QPointF(
            arrow_size * 0.8 * (math.cos(angle + 0.3)),
            arrow_size * 0.8 * (math.sin(angle + 0.3))
        )
        p2 = end - QPointF(
            arrow_size * 0.8 * (math.cos(angle - 0.3)),
            arrow_size * 0.8 * (math.sin(angle - 0.3))
        )
        
        arrow_head = QPolygonF([end, p1, p2])
        painter.setBrush(QBrush(pen.color()))
        painter.drawPolygon(arrow_head)
    
    def _draw_highlight(self, painter: QPainter, start: QPointF, end: QPointF, pen: QPen):
        """Draw a highlight rectangle."""
        # Save the current pen and brush
        old_pen = painter.pen()
        old_brush = painter.brush()
        
        # Set highlight style
        highlight_color = QColor(255, 255, 0, 128)  # Yellow with transparency
        painter.setPen(QPen(highlight_color, pen.width()))
        painter.setBrush(highlight_color)
        
        # Draw the highlight
        painter.drawRect(QRectF(start, end).normalized())
        
        # Restore the pen and brush
        painter.setPen(old_pen)
        painter.setBrush(old_brush)
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.annotation_mode and self.current_annotation:
                # Start a new annotation
                self.current_annotation['start_pos'] = event.pos()
                self.current_annotation['end_pos'] = event.pos()
            else:
                # Start selection
                self.selection_start = event.pos()
                self.selection_end = event.pos()
                self.selection_rect = QRect(self.selection_start, self.selection_end)
                self.is_selecting = True
                self.update_display()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.is_selecting:
            self.selection_end = event.pos()
            self.selection_rect = QRect(self.selection_start, self.selection_end)
            self.update_display()
        elif self.annotation_mode and self.current_annotation and self.current_annotation['start_pos']:
            # Update annotation end position
            self.current_annotation['end_pos'] = event.pos()
            self.update_display()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_selecting:
                self.selection_end = event.pos()
                self.selection_rect = QRect(self.selection_start, self.selection_end).normalized()
                self.is_selecting = False
                
                # Ensure minimum size
                if self.selection_rect.width() < 10 or self.selection_rect.height() < 10:
                    self.selection_rect = QRect()
                
                self.update_display()
            elif self.annotation_mode and self.current_annotation and self.current_annotation['start_pos']:
                # Finish the current annotation
                self.current_annotation['end_pos'] = event.pos()
                
                # Add to annotations list or process as needed
                # For now, just reset the current annotation
                self.current_annotation = None
                self.update_display()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.accept_capture()
        else:
            super().keyPressEvent(event)
    
    def set_annotation_mode(self, enabled: bool):
        """Enable or disable annotation mode."""
        self.annotation_mode = enabled
        self.status_bar.showMessage("Annotation mode: " + ("On" if enabled else "Off"), 2000)
    
    def start_annotation(self, tool_type: ToolType):
        """Start a new annotation with the specified tool."""
        self.set_annotation_mode(True)
        self.current_annotation = {
            'type': tool_type,
            'start_pos': None,
            'end_pos': None,
            'color': QColor(self.color_btn.styleSheet().split(':')[1].strip(';')),
            'line_width': self.line_width.value(),
            'filled': self.fill_check.isChecked()
        }
        self.status_bar.showMessage(f"Drawing {tool_type.name.lower()}", 2000)
    
    def select_color(self):
        """Show color selection dialog."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def extract_text_from_selection(self):
        """Extract text from the selected region using OCR."""
        if self.selection_rect.isNull() or self.background_pixmap is None:
            return
        
        # Create and show loading dialog
        loading_dialog = QDialog(self)
        loading_dialog.setWindowTitle("Extracting Text...")
        loading_dialog.setFixedSize(300, 100)
        loading_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        layout = QVBoxLayout(loading_dialog)
        layout.addWidget(QLabel("Extracting text, please wait..."))
        
        # Add a cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(loading_dialog.reject)
        layout.addWidget(cancel_btn)
        
        # Show the dialog immediately
        loading_dialog.show()
        QApplication.processEvents()
        
        # Flag to track if operation was cancelled
        self.ocr_cancelled = False
        
        def run_ocr():
            try:
                # Extract the selected region
                selected_region = self.background_pixmap.copy(self.selection_rect)
                
                # Convert QPixmap to PIL Image
                qimage = selected_region.toImage()
                buffer = qimage.bits().asstring(qimage.sizeInBytes())
                pil_image = Image.frombytes(
                    'RGBA', 
                    (qimage.width(), qimage.height()), 
                    buffer, 
                    'raw', 'RGBA'
                )
                
                # Get selected language
                lang = self.lang_combo.currentData()
                
                # Check if dialog was closed
                if not loading_dialog.isVisible():
                    return
                
                # Extract text using OCR
                text, metadata = self.ocr_processor.extract_text(
                    pil_image,
                    config={
                        'lang': lang,
                        'preprocess': True,
                        'contrast_factor': 1.5,
                        'sharpen': True,
                        'denoise': True,
                        'threshold': True
                    }
                )
                
                # Check if dialog was closed
                if not loading_dialog.isVisible():
                    return
                
                # Show the extracted text in a dialog
                self.show_ocr_result(text, metadata)
                
            except pytesseract.TesseractNotFoundError:
                if loading_dialog.isVisible():
                    loading_dialog.reject()
                self.show_ocr_install_instructions()
                
            except Exception as e:
                if loading_dialog.isVisible():
                    loading_dialog.reject()
                QMessageBox.critical(
                    self, 
                    "OCR Error", 
                    f"Error extracting text: {str(e)}\n\n"
                    "Please check that Tesseract OCR is properly installed and in your system PATH."
                )
                logger.error(f"OCR extraction failed: {str(e)}", exc_info=True)
                
            finally:
                if loading_dialog.isVisible():
                    loading_dialog.accept()
        
        # Run OCR in a separate thread to keep the UI responsive
        from PyQt6.QtCore import QThread, pyqtSignal
        
        class OCRThread(QThread):
            finished = pyqtSignal()
            
            def run(self):
                run_ocr()
                self.finished.emit()
        
        self.ocr_thread = OCRThread()
        self.ocr_thread.finished.connect(loading_dialog.accept)
        self.ocr_thread.start()
        
        # Show the dialog and wait for it to be closed
        if loading_dialog.exec() == QDialog.DialogCode.Rejected:
            self.ocr_cancelled = True
            self.ocr_thread.terminate()
            self.ocr_thread.wait()
    
    def show_ocr_result(self, text: str, metadata: dict):
        """Display the OCR results in a dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Extracted Text")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Add text area
        text_edit = QTextEdit()
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        # Add confidence info
        confidence = metadata.get('confidence', 0)
        info_label = QLabel(f"Confidence: {confidence:.1f}%")
        layout.addWidget(info_label)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                    QDialogButtonBox.StandardButton.Copy |
                                    QDialogButtonBox.StandardButton.Save)
        
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # Connect copy button
        copy_btn = button_box.button(QDialogButtonBox.StandardButton.Copy)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(text))
        
        # Connect save button
        save_btn = button_box.button(QDialogButtonBox.StandardButton.Save)
        save_btn.clicked.connect(lambda: self.save_ocr_result(text))
        
        layout.addWidget(button_box)
        
        # Show the dialog
        dialog.exec()
    
    def save_ocr_result(self, text: str):
        """Save the extracted text to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Extracted Text",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                QMessageBox.information(
                    self,
                    "Save Successful",
                    f"Text successfully saved to {file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Save Error",
                    f"Error saving file: {str(e)}"
                )
    
    def show_ocr_install_instructions(self):
        """Show installation instructions for Tesseract OCR."""
        system = platform.system().lower()
        
        if 'windows' in system:
            instructions = install_tesseract_windows()
            download_url = "https://github.com/UB-Mannheim/tesseract/wiki"
        elif 'darwin' in system:
            instructions = install_tesseract_macos()
            download_url = "https://formulae.brew.sh/formula/tesseract"
        else:  # Linux and others
            instructions = install_tesseract_linux()
            if 'ubuntu' in platform.version().lower() or 'debian' in platform.version().lower():
                download_url = "https://tesseract-ocr.github.io/tessdoc/Installation.html#linux"
            else:
                download_url = "https://tesseract-ocr.github.io/tessdoc/Home.html"
        
        # Show instructions in a dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Install Tesseract OCR")
        dialog.setMinimumSize(650, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Add header
        header = QLabel("<h3>Tesseract OCR Installation Required</h3>")
        header.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(header)
        
        # Add description
        description = QLabel(
            "Tesseract OCR is required for text recognition. Please install it using the instructions below:"
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add download button
        download_btn = QPushButton(f"Download Tesseract for {platform.system()}")
        download_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(download_url)))
        layout.addWidget(download_btn)
        
        # Add instructions in a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Add instructions with monospace font
        text_edit = QTextEdit()
        text_edit.setFontFamily("Courier")
        text_edit.setPlainText(instructions)
        text_edit.setReadOnly(True)
        scroll_layout.addWidget(text_edit)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Add buttons
        button_box = QDialogButtonBox()
        close_btn = button_box.addButton(QDialogButtonBox.StandardButton.Close)
        copy_btn = button_box.addButton("Copy Instructions", QDialogButtonBox.ButtonRole.ActionRole)
        
        def copy_instructions():
            QApplication.clipboard().setText(instructions)
            QMessageBox.information(dialog, "Copied", "Installation instructions copied to clipboard.")
            
        copy_btn.clicked.connect(copy_instructions)
        close_btn.clicked.connect(dialog.reject)
        
        layout.addWidget(button_box)
        
        # Show the dialog
        dialog.exec()
    
    def accept_capture(self):
        """Accept the current selection and emit the captured region."""
        if self.selection_rect.isNull() or self.background_pixmap is None:
            QMessageBox.warning(self, "No Selection", "Please select an area of the screen to capture.")
            return
        
        # Extract the selected region
        captured = self.background_pixmap.copy(self.selection_rect)
        
        # Create metadata
        metadata = {
            'region': {
                'x': self.selection_rect.x(),
                'y': self.selection_rect.y(),
                'width': self.selection_rect.width(),
                'height': self.selection_rect.height()
            },
            'timestamp': QDateTime.currentDateTime().toString(Qt.DateFormat.ISODate),
            'annotations': []
        }
        
        # Emit signal and close
        self.capture_completed.emit(captured, metadata)
        self.accept()


class ScreenCaptureToolbar(QWidget):
    """Toolbar for screen capture with additional options."""
    
    capture_requested = pyqtSignal()
    save_requested = pyqtSignal()
    copy_requested = pyqtSignal()
    ocr_requested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the toolbar."""
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Capture button
        self.capture_btn = QPushButton("New Capture", self)
        self.capture_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DesktopIcon))
        self.capture_btn.clicked.connect(self.capture_requested)
        
        # Save button
        self.save_btn = QPushButton("Save", self)
        self.save_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.save_btn.clicked.connect(self.save_requested)
        
        # Copy button
        self.copy_btn = QPushButton("Copy", self)
        self.copy_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.copy_btn.clicked.connect(self.copy_requested)
        
        # OCR button
        self.ocr_btn = QPushButton("Extract Text", self)
        self.ocr_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self.ocr_btn.clicked.connect(self.ocr_requested)
        
        # Add widgets to layout
        layout.addWidget(self.capture_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.copy_btn)
        layout.addWidget(self.ocr_btn)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setFixedHeight(40)


# Example usage
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    def on_capture_completed(pixmap, metadata):
        print(f"Capture completed: {metadata}")
        
        # Show the captured image in a new window
        window = QDialog()
        window.setWindowTitle("Captured Image")
        window.resize(800, 600)
        
        layout = QVBoxLayout()
        
        # Image label
        label = QLabel()
        label.setPixmap(pixmap.scaled(780, 500, Qt.AspectRatioMode.KeepAspectRatio))
        
        # Toolbar
        toolbar = ScreenCaptureToolbar()
        
        layout.addWidget(label)
        layout.addWidget(toolbar)
        
        window.setLayout(layout)
        window.exec()
    
    # Create and show the capture dialog
    dialog = ScreenCaptureDialog()
    dialog.capture_completed.connect(on_capture_completed)
    dialog.show()
    
    sys.exit(app.exec())
