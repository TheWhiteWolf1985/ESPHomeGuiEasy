"""
@file yaml_editor.py
@brief Editor YAML con numeri di riga ed evidenziazione riga attiva.

Estende QPlainTextEdit per aggiungere una LineNumberArea laterale, stile editor moderno.
"""

from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtGui import QPainter, QTextCharFormat, QColor
from PyQt6.QtCore import Qt, QRect, QSize

class LineNumberArea(QWidget):
    """
    @class LineNumberArea
    @brief Area laterale per visualizzare i numeri di riga accanto all'editor YAML.
    """
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return self.code_editor.line_number_area_size()

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint(event)


class YamlCodeEditor(QPlainTextEdit):
    """
    @class YamlCodeEditor
    @brief QPlainTextEdit esteso con numeri di riga e evidenziazione riga corrente.
    """
    def __init__(self):
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
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return QSize(space, 0)

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_size().width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_size().width(), cr.height()))

    def line_number_area_paint(self, event):
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

