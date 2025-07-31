# -*- coding: utf-8 -*-
"""
@file custom_dialog_box.py
@brief Generic and reusable dialog box with configurable buttons and message.

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Implements a QDialog with title, message, and one or more custom buttons.
"""

from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from gui.color_pantone import Pantone

class CustomDialogBox(QDialog):
    """
    @brief Generic modal dialog for displaying a message and configurable buttons.
    """

    def __init__(self, title: str, message: str, buttons: list[str], parent=None):
        """
        @param title Title of the dialog window
        @param message Main message to display
        @param buttons List of button labels (e.g. ["OK"], or ["Cancel", "Retry"])
        @param parent Optional parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(400, 200)
        self.setStyleSheet(Pantone.DIALOG_STYLE)

        self.selected_index = -1
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # === MESSAGE LABEL ===
        label = QLabel(message)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setStyleSheet("color: white; font-size: 11pt;")
        layout.addWidget(label)

        # === BUTTONS ===
        btn_box = QHBoxLayout()
        btn_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._buttons = {}

        for index, label in enumerate(buttons):
            btn = QPushButton(label)
            btn.setFixedWidth(120)
            btn.setStyleSheet(
                Pantone.BUTTON_STYLE_GREEN if index == 0 else Pantone.BUTTON_STYLE_GREEN
            )
            btn.clicked.connect(lambda checked=False, i=index: self._button_clicked(i))
            btn_box.addWidget(btn)
            self._buttons[label] = index

        layout.addLayout(btn_box)
        self.setLayout(layout)

    def _button_clicked(self, index: int):
        self.selected_index = index
        self.accept()

    def button_index(self, label: str) -> int:
        """
        @brief Returns the index of a button by its label (case sensitive)
        """
        return self._buttons.get(label, -1)

    def exec(self) -> int:
        """
        @return Index of the button that was pressed
        """
        super().exec()
        return self.selected_index
