# -*- coding: utf-8 -*-
"""
@file project_edit_dialog.py
@brief Dialog window to edit project metadata such as version and changelog.

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Provides input fields for version and multiline changelog,
with OK and Cancel buttons.
"""

from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPlainTextEdit, QDialogButtonBox,
    QVBoxLayout
)
from PyQt6.QtCore import Qt
from gui.color_pantone import Pantone
from core.translator import Translator

class ProjectEditDialog(QDialog):
    """
    @brief Modal dialog to edit version string and changelog text of a project.

    Includes styled QLineEdit and QPlainTextEdit fields and standard dialog buttons.
    """
    def __init__(self, version: str = "", description: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle(Translator.tr("edit_project_title"))
        self.setMinimumSize(400, 300)

        self.version_input = QLineEdit(version)
        self.version_input.setStyleSheet("""
            background-color: #2e2e2e;
            color: white;
            border: 1px solid #555;
            font-size: 10pt;
        """)

        self.description_input = QPlainTextEdit(description)
        self.description_input.setStyleSheet("""
            background-color: #2e2e2e;
            color: white;
            border: 1px solid #555;
            font-size: 10pt;
        """)
        self.description_input.setPlaceholderText(Translator.tr("changelog_placeholder"))

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<b>{Translator.tr('version_label')}:</b>"))
        layout.addWidget(self.version_input)
        layout.addWidget(QLabel(f"<b>{Translator.tr('changelog_label')}:</b>"))
        layout.addWidget(self.description_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self
        )
        buttons.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        return self.version_input.text().strip(), self.description_input.toPlainText().strip()
