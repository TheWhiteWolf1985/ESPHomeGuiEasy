# -*- coding: utf-8 -*-
"""
@file project_gallery_window.py
@brief Main window displaying community projects from GitHub repository.

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Loads project metadata from GitHub, groups projects by category,
and displays project cards with metadata and actions such as download and description.

Provides interactive UI with category selection and styled message dialogs.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

import os, sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QListWidget, QLineEdit, QApplication, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from gui.color_pantone import Pantone
from core.translator import Translator
from core.github_handler import GitHubHandler
import config.GUIconfig as config
from core.log_handler import GeneralLogHandler as logger


class ProjectGalleryWindow(QMainWindow):
    """
    @brief Window showing a categorized gallery of ESPHome community projects.

    Handles loading project metadata from GitHub,
    populating category lists and project cards,
    and providing download and description dialogs.

    Includes UI styling consistent with application theme.
    """
    def __init__(self):
        """
        @brief Initializes the gallery window, sets up UI components and loads project data.

        Checks for network availability and shows a warning dialog if no projects are retrieved.
        Initializes category list and scrollable project display area.
        """
        super().__init__()
        self.setWindowTitle("Community Projects")
        self.setMinimumSize(1050, 600)
        self.setStyleSheet(f"background-color: {Pantone.SECONDARY_BG};")

        self.categories = [
            "Home Monitoring", "Energy & Power", "Security & Alarm",
            "Actuators & I/O", "Communication", "Automation Logic", "Other / Misc"
        ]

        self.project_data = GitHubHandler.fetch_project_metadata_list()
        if not self.project_data:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Errore di rete")
            logger.warning("Nessun progetto recuperato dalla galleria GitHub. Controllare la connessione.")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2e2e2e;
                }
                QPushButton {
                    background-color: #444;
                    color: white;
                    border-radius: 4px;
                    padding: 4px 12px;
                }
                QPushButton:hover {
                    background-color: #666;
                }
            """)

            # 🔥 forza il colore bianco del testo QLabel interno
            for child in msg.children():
                if isinstance(child, QLabel):
                    child.setStyleSheet("color: white; font-size: 11pt;")

            msg.exec()



        self.category_to_cards = self.build_category_index()

        # Layout principale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Lista categorie a sinistra
        self.category_list = QListWidget()
        categories = [
            ("🏠 Home Monitoring"),
            ("⚡ Energy & Power"),
            ("🚪 Security & Alarm"),
            ("🔧 Actuators & I/O"),
            ("🌐 Communication"),
            ("🧠 Automation Logic"),
            ("🧪 Other / Misc"),
        ]
        for label in categories:
            item = QListWidgetItem(label)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.category_list.addItem(item)

        self.category_list.setFixedWidth(220)
        self.category_list.currentTextChanged.connect(self.load_category_cards)
        self.category_list.setStyleSheet(Pantone.LISTWIDGET_STYLE)
        main_layout.addWidget(self.category_list)


        # Scroll area a destra
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_content.setLayout(self.scroll_layout)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        self.category_list.setCurrentRow(0)  # carica la prima categoria

    def build_category_index(self):
        """
        @brief Builds an index dictionary grouping projects by category.

        @return Dictionary with category names as keys and lists of projects as values.
        """
        result = {cat: [] for cat in self.categories}
        for proj in self.project_data:
            cat = proj.get("category", "Other / Misc")
            result.setdefault(cat, []).append(proj)
        return result

    def load_category_cards(self, category_name):
        """
        @brief Loads project cards for the selected category into the scroll area.

        Clears existing cards and adds new widgets for each project in the category.
        """
        emoji_to_category = {
            "🏠 Home Monitoring": "Home Monitoring",
            "⚡ Energy & Power": "Energy & Power",
            "🚪 Security & Alarm": "Security & Alarm",
            "🔧 Actuators & I/O": "Actuators & I/O",
            "🌐 Communication": "Communication",
            "🧠 Automation Logic": "Automation Logic",
            "🧪 Other / Misc": "Other / Misc",
        }
        category_name = emoji_to_category.get(category_name, category_name)
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for project in self.category_to_cards.get(category_name, []):
            self.add_project_card(project)

    def add_project_card(self, fields):
        """
        @brief Creates and adds a UI card widget displaying project metadata and action buttons.

        @param fields Dictionary of project metadata fields (name, version, author, update).
        """
        card = QWidget()
        card.setFixedHeight(100)
        card.setStyleSheet("""
            background-color: #2e2e2e;
            border: 1px solid #555;
            border-radius: 6px;
        """)

        card_layout = QHBoxLayout()
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(4)

        # Campi visibili
        for label_text in ["Name", "Version", "Author", "Update"]:
            value_text = fields.get(label_text, fields.get(label_text.lower(), "-"))

            row = QVBoxLayout()
            row.setSpacing(4)

            label = QLabel(f"{label_text}:")
            label.setStyleSheet("color: #aaa; font-size: 10pt; padding: 0px;")
            label.setFixedSize(150, 35)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            value = QLabel(value_text)
            value.setStyleSheet("color: #fff; font-size: 10pt; padding: 0px;")
            value.setWordWrap(True)
            value.setFixedSize(150, 35)
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)

            row.addWidget(label)
            row.addWidget(value)
            card_layout.addLayout(row)
            card_layout.addStretch()

        # Pulsanti
        btn = QWidget()
        btn_layout = QVBoxLayout()

        download_btn = QPushButton("➕ " + Translator.tr("download"))
        download_btn.setStyleSheet(Pantone.COMMON_BUTTON_STYLE)
        download_btn.clicked.connect(lambda: self.download_project(fields))

        open_card_btn = QPushButton("➕ " + Translator.tr("descrizione"))
        open_card_btn.setStyleSheet(Pantone.COMMON_BUTTON_STYLE)
        open_card_btn.clicked.connect(lambda _, f=fields: self.mostra_descrizione_progetto(f))


        btn_layout.addWidget(download_btn)
        btn_layout.addWidget(open_card_btn)
        btn.setLayout(btn_layout)
        card_layout.addWidget(btn)

        card.setLayout(card_layout)
        self.scroll_layout.addWidget(card)

    def download_project(self, fields):
        """
        @brief Downloads the selected project from GitHub to the local community folder.

        Creates local folders if needed and triggers GitHubHandler download.
        Shows an information dialog on completion with local path.
        """
        nome_progetto = fields.get("name", fields.get("Name", "unknown")).strip().replace(" ", "-").lower()
        local_folder = os.path.join(config.COMMUNITY_LOCAL_FOLDER, nome_progetto)
        os.makedirs(local_folder, exist_ok=True)

        GitHubHandler.download_project_to_folder(nome_progetto, local_folder)

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Download completato")
        msg.setText(f"Il progetto '{nome_progetto}' è stato salvato in:\n{local_folder}")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2e2e2e;
            }
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        # Forza il testo bianco nel QLabel interno
        for child in msg.children():
            if isinstance(child, QLabel):
                child.setStyleSheet("color: white; font-size: 11pt;")

        msg.exec()

    def mostra_descrizione_progetto(self, fields):
        """
        @brief Shows a message dialog displaying the project description.

        @param fields Dictionary containing project metadata including description.
        """
        nome = fields.get("name", fields.get("Name", "Senza nome"))
        descrizione = fields.get("description", "Nessuna descrizione disponibile.")

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(f"{nome}")
        msg.setText(descrizione)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2e2e2e;
            }
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        for child in msg.children():
            if isinstance(child, QLabel):
                child.setStyleSheet("color: white; font-size: 11pt;")
        msg.exec()
