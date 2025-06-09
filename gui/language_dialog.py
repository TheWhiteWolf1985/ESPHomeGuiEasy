from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
from core.translator import Translator

class LanguageDialog(QDialog):
    def __init__(self, available_langs, parent=None):
        super().__init__(parent)
        self.selected = None
        self.setWindowTitle(Translator.tr("language_title"))
        self.setMinimumWidth(350)
        layout = QVBoxLayout()
        label = QLabel(Translator.tr("language_select_label"))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Rappresentazione bandiere e nomi (semplice, puoi personalizzare)
        buttons = QHBoxLayout()
        flag_map = {
            "it": "🇮🇹",
            "en": "🇬🇧",
            "de": "🇩🇪",
            "es": "🇪🇸"
        }
        name_map = {
            "it": "Italiano",
            "en": "English",
            "de": "Deutsch",
            "es": "Español"
        }
        for code in available_langs:
            text = f"{flag_map.get(code, code.upper())} {Translator.tr(f'language_{code}')}"
            btn = QPushButton(text)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            btn.clicked.connect(lambda _, c=code: self.choose_lang(c))
            buttons.addWidget(btn)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def choose_lang(self, code):
        self.selected = code
        self.accept()
