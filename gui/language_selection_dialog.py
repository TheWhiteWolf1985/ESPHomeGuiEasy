from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize
from gui.color_pantone import Pantone
import os


class LanguageSelectionDialog(QDialog):
    def __init__(self, parent=None):
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
        self.selected_language = code
        self.accept()

    def get_selected_language(self):
        return self.selected_language
