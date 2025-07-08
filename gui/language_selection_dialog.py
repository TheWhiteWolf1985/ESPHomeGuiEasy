# -*- coding: utf-8 -*-
"""
@file language_selection_dialog.py
@brief Dialog for selecting the application language with flag icons.

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Displays buttons for supported languages with respective flag icons.
On selection, stores the chosen language code.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize
from gui.color_pantone import Pantone
import os


class LanguageSelectionDialog(QDialog):
    """
    @brief QDialog that presents a list of language options as buttons with flag icons.

    Supports language selection and acceptance.
    """
    def __init__(self, parent=None):
        """
        @brief Initializes the language selection dialog UI with buttons and icons.
        """
        super().__init__(parent)
        self.setWindowTitle("Seleziona la lingua")
        self.setMinimumSize(300, 300)
        self.setStyleSheet(Pantone.DIALOG_STYLE)
        self.selected_language = None

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("\ud83c\udf0d Seleziona la tua lingua")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(Pantone.DIALOG_TITLE_STYLE)
        layout.addWidget(title)

        # Percorso bandiere
        flag_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "flags")

        # Lingue supportate
        languages = [
            ("it", "Italiano", "it.png"),
            ("en", "English", "en.png"),
            ("es", "Espa\u00f1ol", "es.png"),
            ("de", "Deutsch", "de.png"),
            ("br", "Brasileiro", "br.png"),
            ("pt", "Português", "pt.png")
        ]

        for code, label, icon_file in languages:
            button = QPushButton(label)
            icon_path = os.path.join(flag_path, icon_file)
            if os.path.exists(icon_path):
                button.setIcon(QIcon(icon_path))
            button.setStyleSheet(Pantone.BUTTON_STYLE)
            button.setIconSize(QSize(48, 48))
            button.clicked.connect(lambda checked, lang=code: self.select_language(lang))
            layout.addWidget(button)

    def select_language(self, code):
        """
        @brief Slot that sets the selected language code and accepts the dialog.

        @param code Language code string (e.g., "en", "it").
        """
        self.selected_language = code
        self.accept()

    def get_selected_language(self):
        """
        @brief Returns the language code selected by the user.

        @return Selected language code as string.
        """
        return self.selected_language
