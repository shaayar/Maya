"""
Annotation Tools for MAYA AI Chatbot.
Provides functionality for annotating screenshots with various drawing tools.
"""
from enum import Enum, auto
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtGui import (QPainter, QPen, QColor, QBrush, QPixmap, QPainterPath,
                        QFont, QFontMetrics, QKeyEvent, QMouseEvent, QPaintEvent)
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QColorDialog, QSpinBox, QLabel, QComboBox, QSizePolicy)


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


@dataclass
class Annotation:
    """Base class for all annotation types."""
    tool_type: ToolType
    start_pos: QPointF
    end_pos: QPointF
    color: QColor
    line_width: int = 2
    filled: bool = False
    text: str = ""
    
    @property
    def rect(self) -> QRectF:
        """Get the bounding rectangle of the annotation."""
        return QRectF(self.start_pos, self.end_pos).normalized()
    
    def contains(self, point: QPointF) -> bool:
        """Check if the annotation contains the given point."""
        return self.rect.contains(point)
    
    def paint(self, painter: QPainter):
        """Paint the annotation on the given painter."""
        pen = QPen(self.color, self.line_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        if self.filled:
            painter.setBrush(QBrush(self.color))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
        
        if self.tool_type == ToolType.RECTANGLE:
            painter.drawRect(self.rect)
        elif self.tool_type == ToolType.ELLIPSE:
            painter.drawEllipse(self.rect)
        elif self.tool_type in (ToolType.ARROW, ToolType.LINE):
            painter.drawLine(self.start_pos, self.end_pos)
            
            # Add arrow head for arrow tool
            if self.tool_type == ToolType.ARROW:
                self._draw_arrow_head(painter)
        
        # Draw text if this is a text annotation
        if self.tool_type == ToolType.TEXT and self.text:
            self._draw_text(painter)
    
    def _draw_arrow_head(self, painter: QPainter):
        """Draw an arrow head at the end of the line."""
        # Calculate arrow head points
        arrow_size = 10
        dx = self.end_pos.x() - self.start_pos.x()
        dy = self.end_pos.y() - self.start_pos.y()
        angle = (dx * dx + dy * dy) ** 0.5
        
        if angle == 0:
            return
            
        # Calculate arrow head points
        cos_angle = dx / angle
        sin_angle = dy / angle
        
        # Base of the arrow head
        base = QPointF(
            self.end_pos.x() - arrow_size * cos_angle,
            self.end_pos.y() - arrow_size * sin_angle
        )
        
        # Perpendicular points
        perp_x = -arrow_size * sin_angle / 2
        perp_y = arrow_size * cos_angle / 2
        
        # Create arrow head polygon
        arrow_head = [
            self.end_pos,
            QPointF(base.x() + perp_x, base.y() + perp_y),
            QPointF(base.x() - perp_x, base.y() - perp_y)
        ]
        
        # Draw arrow head
        painter.setBrush(QBrush(self.color))
        painter.drawPolygon(arrow_head)
    
    def _draw_text(self, painter: QPainter):
        """Draw text annotation."""
        font = QFont("Arial", 12)
        painter.setFont(font)
        
        # Set up text rectangle
        text_rect = QRectF(
            min(self.start_pos.x(), self.end_pos.x()),
            min(self.start_pos.y(), self.end_pos.y()),
            abs(self.end_pos.x() - self.start_pos.x()),
            abs(self.end_pos.y() - self.start_pos.y())
        )
        
        # Draw text
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self.text)


class AnnotationCanvas(QWidget):
    """Widget for drawing annotations on top of an image."""
    
    annotation_added = object()  # Signal for when an annotation is added
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Image being annotated
        self.original_pixmap = QPixmap()
        self.scaled_pixmap = QPixmap()
        self.scale_factor = 1.0
        
        # Annotation state
        self.annotations: List[Annotation] = []
        self.current_annotation: Optional[Annotation] = None
        self.selected_annotation: Optional[Annotation] = None
        self.dragging = False
        self.drag_start = QPointF()
        
        # Tool settings
        self.current_tool = ToolType.RECTANGLE
        self.current_color = QColor(255, 0, 0)  # Red
        self.line_width = 2
        self.fill_shape = False
        
        # Text input state
        self.text_input_active = False
        self.text_input_pos = QPointF()
        self.text_input = ""
        
        # Initialize UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setMinimumSize(400, 300)
    
    def set_pixmap(self, pixmap: QPixmap):
        """Set the image to be annotated."""
        self.original_pixmap = pixmap
        self.scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.update()
    
    def paintEvent(self, event: QPaintEvent):
        """Handle paint events."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw the background image
        if not self.scaled_pixmap.isNull():
            # Center the image
            x = (self.width() - self.scaled_pixmap.width()) // 2
            y = (self.height() - self.scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, self.scaled_pixmap)
            
            # Set the scale factor for mouse position mapping
            if not self.original_pixmap.isNull():
                self.scale_factor = min(
                    self.scaled_pixmap.width() / self.original_pixmap.width(),
                    self.scaled_pixmap.height() / self.original_pixmap.height()
                )
        
        # Draw all annotations
        for annotation in self.annotations:
            annotation.paint(painter)
        
        # Draw current annotation in progress
        if self.current_annotation:
            self.current_annotation.paint(painter)
        
        # Draw text input cursor if active
        if self.text_input_active:
            self._draw_text_cursor(painter)
    
    def _draw_text_cursor(self, painter: QPainter):
        """Draw the text input cursor."""
        font = QFont("Arial", 12)
        fm = QFontMetrics(font)
        cursor_x = self.text_input_pos.x() + fm.horizontalAdvance(self.text_input)
        cursor_rect = QRectF(cursor_x, self.text_input_pos.y(), 2, fm.height())
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawRect(cursor_rect)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self._map_to_image(event.pos())
            
            # Start a new annotation or select an existing one
            if self.current_tool == ToolType.SELECT:
                self._handle_selection(pos, event.modifiers())
            elif self.current_tool == ToolType.TEXT:
                self._start_text_input(pos)
            else:
                self._start_annotation(pos)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        pos = self._map_to_image(event.pos())
        
        # Update the current annotation or move the selected one
        if self.current_annotation and not self.text_input_active:
            self.current_annotation.end_pos = pos
            self.update()
        elif self.selected_annotation and self.dragging:
            # Move the selected annotation
            delta = pos - self.drag_start
            self.selected_annotation.start_pos += delta
            self.selected_annotation.end_pos += delta
            self.drag_start = pos
            self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton and self.current_annotation:
            # Add the completed annotation to the list
            if self.current_tool != ToolType.TEXT:  # Text is handled on key press
                self.annotations.append(self.current_annotation)
                self.annotation_added.emit()
            
            self.current_annotation = None
            self.dragging = False
            self.update()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if self.text_input_active:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                self._finish_text_input()
            elif event.key() == Qt.Key.Key_Escape:
                self._cancel_text_input()
            elif event.key() == Qt.Key.Key_Backspace:
                self.text_input = self.text_input[:-1]
                self.update()
            elif event.text() and len(event.text()) == 1:
                self.text_input += event.text()
                self.update()
        elif event.key() == Qt.Key.Key_Delete and self.selected_annotation:
            # Delete selected annotation
            if self.selected_annotation in self.annotations:
                self.annotations.remove(self.selected_annotation)
                self.selected_annotation = None
                self.update()
        elif event.key() == Qt.Key.Key_Escape:
            # Cancel current operation
            if self.current_annotation:
                self.current_annotation = None
                self.update()
            elif self.selected_annotation:
                self.selected_annotation = None
                self.update()
    
    def _map_to_image(self, pos: QPointF) -> QPointF:
        """Map screen coordinates to image coordinates."""
        if self.scaled_pixmap.isNull():
            return pos
            
        # Calculate the position relative to the centered image
        img_x = (self.width() - self.scaled_pixmap.width()) // 2
        img_y = (self.height() - self.scaled_pixmap.height()) // 2
        
        # Map to image coordinates
        x = (pos.x() - img_x) / self.scale_factor
        y = (pos.y() - img_y) / self.scale_factor
        
        return QPointF(max(0, min(x, self.original_pixmap.width())),
                      max(0, min(y, self.original_pixmap.height())))
    
    def _start_annotation(self, pos: QPointF):
        """Start a new annotation at the given position."""
        self.current_annotation = Annotation(
            tool_type=self.current_tool,
            start_pos=pos,
            end_pos=pos,
            color=self.current_color,
            line_width=self.line_width,
            filled=self.fill_shape
        )
        self.update()
    
    def _handle_selection(self, pos: QPointF, modifiers: Qt.KeyboardModifiers):
        """Handle selection of annotations."""
        # Check if we clicked on an annotation
        for annotation in reversed(self.annotations):
            if annotation.contains(pos):
                if modifiers & Qt.KeyboardModifier.ShiftModifier:
                    # Toggle selection with Shift
                    if annotation == self.selected_annotation:
                        self.selected_annotation = None
                    else:
                        self.selected_annotation = annotation
                else:
                    # Select the annotation and prepare to move it
                    self.selected_annotation = annotation
                    self.dragging = True
                    self.drag_start = pos
                break
        else:
            # Clicked on empty space, clear selection
            self.selected_annotation = None
        
        self.update()
    
    def _start_text_input(self, pos: QPointF):
        """Start text input at the given position."""
        self.text_input_active = True
        self.text_input_pos = pos
        self.text_input = ""
        self.current_annotation = Annotation(
            tool_type=ToolType.TEXT,
            start_pos=pos,
            end_pos=pos,
            color=self.current_color,
            line_width=self.line_width,
            text=""
        )
        self.setFocus()
        self.update()
    
    def _finish_text_input(self):
        """Finish text input and add the text annotation."""
        if self.current_annotation and self.text_input:
            self.current_annotation.text = self.text_input
            self.annotations.append(self.current_annotation)
            self.annotation_added.emit()
        
        self._cancel_text_input()
    
    def _cancel_text_input(self):
        """Cancel text input."""
        self.text_input_active = False
        self.current_annotation = None
        self.update()
    
    def clear_annotations(self):
        """Clear all annotations."""
        self.annotations.clear()
        self.selected_annotation = None
        self.current_annotation = None
        self.update()
    
    def get_annotated_pixmap(self) -> QPixmap:
        """Get the annotated image as a QPixmap."""
        if self.original_pixmap.isNull():
            return QPixmap()
        
        # Create a copy of the original image
        result = self.original_pixmap.copy()
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw all annotations
        for annotation in self.annotations:
            annotation.paint(painter)
        
        painter.end()
        return result


class AnnotationToolbar(QWidget):
    """Toolbar for annotation tools and options."""
    
    tool_changed = object()  # Signal for when the tool changes
    color_changed = object()  # Signal for when the color changes
    line_width_changed = object()  # Signal for when the line width changes
    fill_toggled = object()  # Signal for when fill mode is toggled
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Tool buttons
        self.tool_buttons = {}
        tools = [
            (ToolType.SELECT, "Select", "Select and move annotations"),
            (ToolType.RECTANGLE, "Rectangle", "Draw a rectangle"),
            (ToolType.ELLIPSE, "Ellipse", "Draw an ellipse"),
            (ToolType.ARROW, "Arrow", "Draw an arrow"),
            (ToolType.LINE, "Line", "Draw a line"),
            (ToolType.TEXT, "Text", "Add text"),
            (ToolType.HIGHLIGHT, "Highlight", "Highlight area"),
        ]
        
        for tool_type, text, tooltip in tools:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, t=tool_type: self._on_tool_selected(t))
            layout.addWidget(btn)
            self.tool_buttons[tool_type] = btn
        
        # Color button
        self.color_button = QPushButton()
        self.color_button.setFixedSize(32, 32)
        self.color_button.setStyleSheet("background-color: red;")
        self.color_button.clicked.connect(self._select_color)
        layout.addWidget(self.color_button)
        
        # Line width
        layout.addWidget(QLabel("Width:"))
        self.line_width = QSpinBox()
        self.line_width.setRange(1, 20)
        self.line_width.setValue(2)
        self.line_width.valueChanged.connect(self.line_width_changed.emit)
        layout.addWidget(self.line_width)
        
        # Fill checkbox
        self.fill_checkbox = QCheckBox("Fill")
        self.fill_checkbox.toggled.connect(self.fill_toggled.emit)
        layout.addWidget(self.fill_checkbox)
        
        # Clear button
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self._on_clear_clicked)
        layout.addWidget(clear_btn)
        
        # Add stretch to push everything to the left
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Select the first tool by default
        self._on_tool_selected(ToolType.RECTANGLE)
    
    def _on_tool_selected(self, tool_type: ToolType):
        """Handle tool selection."""
        # Update button states
        for t, btn in self.tool_buttons.items():
            btn.setChecked(t == tool_type)
        
        # Emit signal
        self.tool_changed.emit(tool_type)
    
    def _select_color(self):
        """Show color selection dialog."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.set_color(color)
    
    def _on_clear_clicked(self):
        """Handle clear button click."""
        # Emit a special tool type to indicate clear
        self.tool_changed.emit(None)
    
    def set_color(self, color: QColor):
        """Set the current color."""
        self.color_button.setStyleSheet(f"background-color: {color.name()};")
        self.color_changed.emit(color)
    
    def get_color(self) -> QColor:
        """Get the current color."""
        return QColor(self.color_button.styleSheet().split(":")[1].strip(";"))
    
    def get_line_width(self) -> int:
        """Get the current line width."""
        return self.line_width.value()
    
    def is_fill_enabled(self) -> bool:
        """Check if fill is enabled."""
        return self.fill_checkbox.isChecked()
