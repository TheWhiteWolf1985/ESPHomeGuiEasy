from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from gui.color_pantone import Pantone
from core.translator import Translator

class CustomMessageDialog(QDialog):
    def __init__(self, title: str, message: str, changelog: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(400, 400)
        self.setStyleSheet(Pantone.DIALOG_STYLE)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # === BLOCCO DESCRIZIONE ===
        label_description = QLabel(f"""
            <b>📄 {Translator.tr('descrizione')}:</b><br>
            <div style="margin-left: 10px;">{message}</div>
        """)
        label_description.setWordWrap(True)
        label_description.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label_description.setAlignment(Qt.AlignmentFlag.AlignTop)
        label_description.setStyleSheet("color: white; font-size: 11pt;")
        layout.addWidget(label_description)

        # === BLOCCO CHANGELOG ===
        label_changelog = QLabel(f"""
            <b>📘 Changelog:</b><br>
            <div style="margin-left: 10px; white-space: pre-line;">{changelog}</div>
        """)
        label_changelog.setWordWrap(True)
        label_changelog.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label_changelog.setAlignment(Qt.AlignmentFlag.AlignTop)
        label_changelog.setStyleSheet("color: white; font-size: 11pt;")
        layout.addWidget(label_changelog)

        btn_box = QHBoxLayout()
        btn_box.setAlignment(Qt.AlignmentFlag.AlignRight)

        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)
        ok_btn.setFixedWidth(120)
        ok_btn.clicked.connect(self.accept)
        btn_box.addWidget(ok_btn)

        layout.addLayout(btn_box)
        self.setLayout(layout)
