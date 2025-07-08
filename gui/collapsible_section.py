# -*- coding: utf-8 -*-
"""
@file collapsible_section.py
@brief Custom collapsible/expandable section widget for use as accordion panels.

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Implements a QWidget that can expand or collapse its content area,
with a toggle button that shows an arrow and optional icon.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QToolButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from gui.color_pantone import Pantone

class CollapsibleSection(QWidget):
    """
    @brief A collapsible panel widget that can show or hide its content with a toggle button.

    Includes an arrow icon indicating expansion state, and supports a text title with optional icon.
    """
    def __init__(self, title: str, content: QWidget, icon: str = ""):
        """
        @brief Initializes the collapsible section with a title, content widget, and optional icon.

        @param title The header text to display.
        @param content The QWidget to show or hide inside the section.
        @param icon Optional string icon (e.g. emoji) to show before the title.
        """
        super().__init__()
        self._icon = icon  # <--- salva l’icona come attributo di istanza
        self.toggle_button = QToolButton(text=f"{icon} {title}", checkable=True, checked=False)
        self.toggle_button.setStyleSheet(Pantone.ACCORDION_QTOOLBUTTON)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.toggled.connect(self.on_toggled)
        self.toggle_button.setStyleSheet(Pantone.ACCORDION_HEADER_STYLE)
        self.toggle_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.content_area = QFrame()
        self.content_area.setFrameShape(QFrame.Shape.NoFrame)
        self.content_area.setMaximumHeight(0)
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.content_area.setStyleSheet("background-color: #2a2d2e; border-radius: 0 0 8px 8px;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        # Set layout for content
        content_layout = QVBoxLayout()
        content_layout.addWidget(content)
        content_layout.setContentsMargins(0, 0, 0, 0)  # Imposta sempre a zero
        self.content_area.setLayout(content_layout)

    def on_toggled(self, checked):
        """
        @brief Slot connected to the toggle button to expand or collapse the content area.

        @param checked True if expanded, False if collapsed.
        """
        if checked:
            self.toggle_button.setArrowType(Qt.ArrowType.DownArrow)
            self.content_area.setMaximumHeight(16777215)
        else:
            self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
            self.content_area.setMaximumHeight(0)
        self.updateGeometry()

    def set_title(self, title):
        """
        @brief Updates the section title text, preserving the icon.

        @param title New text for the header.
        """
        self.toggle_button.setText(f"{self._icon} {title}")        

