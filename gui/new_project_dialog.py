from PyQt6.QtWidgets import QMessageBox
import sys, os, re
from gui.color_pantone import Pantone
from core.translator import Translator
from PyQt6.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt
from pathlib import Path
from config.GUIconfig import DEFAULT_PROJECT_DIR

CATEGORIES = [
    "Home Monitoring",
    "Energy & Power",
    "Security & Alarm",
    "Actuators & I/O",
    "Communication",
    "Automation Logic",
    "Other / Misc"
]

class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(Translator.tr("new_project"))
        self.setMinimumSize(600,400)
        self.init_ui()
        self.setStyleSheet(Pantone.DIALOG_STYLE)

        DEFAULT_PROJECT_DIR.mkdir(parents=True, exist_ok=True)
        self.base_dir_input.setText(str(DEFAULT_PROJECT_DIR))

    def init_ui(self):
        layout = QVBoxLayout()

        # Nome progetto
        self.name_input = QLineEdit()
        name_label = QLabel(Translator.tr("project_name_title"))
        name_label.setStyleSheet(Pantone.LABEL_TITLE_STYLE)
        layout.addWidget(name_label)
        self.name_input.setStyleSheet(Pantone.LINEEDIT_STYLE)
        layout.addWidget(self.name_input)

        # Autore
        self.author_input = QLineEdit()
        author_label = QLabel(Translator.tr("project_author"))
        author_label.setStyleSheet(Pantone.LABEL_TITLE_STYLE)
        layout.addWidget(author_label)
        self.author_input.setStyleSheet(Pantone.LINEEDIT_STYLE)
        layout.addWidget(self.author_input)

        # Versione
        self.version_input = QLineEdit("1.0.0")
        version_label = QLabel(Translator.tr("version_label").split(" ")[0] + ":")
        version_label.setStyleSheet(Pantone.LABEL_TITLE_STYLE)
        layout.addWidget(version_label)
        self.version_input.setStyleSheet(Pantone.LINEEDIT_STYLE)
        layout.addWidget(self.version_input)

        # Categoria
        self.category_combo = QComboBox()
        self.category_combo.addItems(CATEGORIES)
        category_label = QLabel(Translator.tr("project_category"))
        category_label.setStyleSheet(Pantone.LABEL_TITLE_STYLE)
        layout.addWidget(category_label)
        self.category_combo.setStyleSheet(Pantone.COMBO_STYLE)
        layout.addWidget(self.category_combo)

        # Descrizione
        self.description_input = QTextEdit()
        desc_label = QLabel(Translator.tr("descrizione"))
        desc_label.setStyleSheet(Pantone.LABEL_TITLE_STYLE)
        layout.addWidget(desc_label)
        self.description_input.setStyleSheet(Pantone.TEXTAREA_STYLE)
        layout.addWidget(self.description_input)

        # Directory base
        dir_layout = QHBoxLayout()
        self.base_dir_input = QLineEdit()
        browse_btn = QPushButton()
        browse_btn.setText(Translator.tr("settings_browse"))
        browse_btn.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)
        self.base_dir_input.setStyleSheet(Pantone.LINEEDIT_STYLE)
        browse_btn.clicked.connect(self.browse_folder)
        dir_layout.addWidget(self.base_dir_input)
        dir_layout.addWidget(browse_btn)
        dir_label = QLabel(Translator.tr("select_project_dir"))
        dir_label.setStyleSheet(Pantone.LABEL_TITLE_STYLE)
        layout.addWidget(dir_label)
        layout.addLayout(dir_layout)

        # Checkbox per sottocartelle
        self.subfolders_checkbox = QCheckBox()
        self.subfolders_checkbox.setText(Translator.tr("project_subfolders"))
        self.subfolders_checkbox.setStyleSheet(Pantone.CHECKBOX_STYLE)
        self.subfolders_checkbox.setChecked(True)
        layout.addWidget(self.subfolders_checkbox)

        # Pulsanti
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.create_btn = QPushButton()
        self.cancel_btn = QPushButton()

        self.create_btn.setText("➕ " + Translator.tr("create"))
        self.cancel_btn.setText("❌ " + Translator.tr("cancel_button"))

        self.create_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn.clicked.connect(self.reject)

        self.create_btn.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)
        self.cancel_btn.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)

        # Uniforma dimensioni e allineamento
        self.create_btn.setFixedSize(150, 45)
        self.cancel_btn.setFixedSize(150, 45)

        button_layout.addStretch()
        button_layout.addWidget(self.create_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)


        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, Translator.tr("select_project_dir"))
        if folder:
            self.base_dir_input.setText(folder)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "version": self.version_input.text().strip(),
            "author": self.author_input.text().strip(),
            "category": self.category_combo.currentText(),
            "description": self.description_input.toPlainText().strip(),
            "base_dir": self.base_dir_input.text().strip(),
            "create_subfolders": self.subfolders_checkbox.isChecked()
        }
    
    def validate_and_accept(self):
        name = self.name_input.text().strip()
        base_dir = self.base_dir_input.text().strip()

        if not name:
            QMessageBox.warning(self, Translator.tr("warning"), Translator.tr("error_project_name_required"))
            return

        # Controlla caratteri non validi per nomi di cartelle
        if re.search(r'[<>:"/\\|?*]', name):
            QMessageBox.warning(self, Translator.tr("warning"), Translator.tr("error_invalid_characters"))
            return

        # Fallback se base_dir è vuoto
        if not base_dir:
            self.base_dir_input.setText(str(DEFAULT_PROJECT_DIR))

        self.accept()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     dlg = NewProjectDialog()
#     if dlg.exec():
#         data = dlg.get_data()
#         print("Dati progetto:")
#         for k, v in data.items():
#             print(f"{k}: {v}")
#     sys.exit()
