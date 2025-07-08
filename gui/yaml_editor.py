# -*- coding: utf-8 -*-
"""
@file yaml_editor.py
@brief YAML editor with line numbers and current line highlighting.

@defgroup widgets GUI Components
@ingroup gui
@brief Custom code editor widget for editing YAML with modern usability.

Extends QPlainTextEdit to show a vertical LineNumberArea, styled like a modern IDE,
and highlights the current line for better readability.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtGui import QPainter, QTextCharFormat, QColor
from PyQt6.QtCore import Qt, QRect, QSize

class LineNumberArea(QWidget):
    """
    @brief Side widget displaying line numbers for the YamlCodeEditor.

    Used internally by the editor to draw numbered lines on the left-hand side.

    @note This widget is tightly coupled with `YamlCodeEditor`.
    """
    def __init__(self, editor):
        super().__init__(editor)
        """
        @brief Initializes the line number area.

        @param editor Reference to the parent YamlCodeEditor.
        """        
        self.code_editor = editor

    def sizeHint(self):
        """
        @brief Suggests the size of the line number area based on the current editor state.

        @return QSize with suggested width.
        """        
        return self.code_editor.line_number_area_size()

    def paintEvent(self, event):
        """
        @brief Delegates painting to the parent editor.

        This allows the editor to control the actual drawing of line numbers.

        @param event QPaintEvent triggering the update.
        """        
        self.code_editor.line_number_area_paint(event)


class YamlCodeEditor(QPlainTextEdit):
    """
    @brief Extended text editor for YAML with line numbers and line highlighting.

    Provides an enhanced editing experience, similar to modern code editors:
    - Displays line numbers
    - Highlights the current line
    - Disables word wrapping
    """
    def __init__(self):
        """
        @brief Initializes the YAML code editor with line numbers and highlighting.

        Connects signals to handle editor resizing, text block changes,
        and cursor movement. Disables line wrapping.
        """        
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.line_number_area.setStyleSheet("background-color: #1e1e1e;")

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

    def line_number_area_size(self):
        """
        @brief Calculates the width needed to display all line numbers.

        Depends on the number of digits in the total line count.

        @return QSize with calculated width.
        """        
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return QSize(space, 0)

    def update_line_number_area_width(self, _):
        """
        @brief Adjusts the left margin of the editor to fit the line number area.

        Called whenever the number of blocks (lines) changes.
        """        
        self.setViewportMargins(self.line_number_area_size().width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """
        @brief Updates/redraws the line number area when the editor changes.

        Handles vertical scrolling and full redraw requests.

        @param rect QRect describing the affected area.
        @param dy Vertical delta scroll (0 if full repaint is needed).
        """        
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """
        @brief Repositions the line number area on editor resize.

        Ensures the number area stays aligned with the editor content.

        @param event Resize event.
        """        
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_size().width(), cr.height()))

    def line_number_area_paint(self, event):
        """
        @brief Custom paint method for rendering line numbers.

        Iterates over visible text blocks and draws their line numbers
        in the left margin.

        @param event Paint event describing the updated region.
        """        
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.GlobalColor.darkGray)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.GlobalColor.white)
                painter.drawText(0, top, self.line_number_area.width() - 4, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1



    def highlight_current_line(self):
        """
        @brief Highlights the background of the current line (if not read-only).

        Uses a subtle dark color for better text tracking.
        """        
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            # Crea un nuovo formato basato sullo stile corrente del testo
            format = QTextCharFormat(self.currentCharFormat())
            format.setBackground(QColor("#2a2d2e"))  # colore scuro stile VS Code

            selection.format = format
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()

            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

