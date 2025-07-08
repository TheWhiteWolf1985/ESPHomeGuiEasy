# -*- coding: utf-8 -*-
"""
@file user_project_manager.py
@brief Visual project manager for user ESPHome projects stored locally.

@defgroup project_ui Project Manager
@ingroup gui
@brief GUI for managing user-created ESPHome projects with categories, cards and actions.

Displays a categorized list of local projects stored in the `user_projects` directory,
allowing users to open, edit, inspect or delete their own projects.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

import os, sys, json
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QListWidget, QMessageBox, QListWidgetItem, QApplication,
    QInputDialog, QGridLayout, QDialog
)
from PyQt6.QtCore import Qt
from gui.color_pantone import Pantone
from config.GUIconfig import DEFAULT_PROJECT_DIR
from datetime import datetime
from core.translator import Translator
from gui.custom_message_dialog import CustomMessageDialog
from gui.project_edit_dialog import ProjectEditDialog
from core.settings_db import get_setting

def format_changelog(changelog: list[dict]) -> str:
    if not changelog:
        return Translator.tr("no_changelog_available")  # o ""

    lines = []
    for entry in reversed(changelog):  # mostriamo prima i più recenti
        version = entry.get("version", "?.?")
        date = entry.get("date", "???")
        text = entry.get("text", "").strip()

        lines.append(f"🟢 Versione {version} ({date})")
        if text:
            lines.append(f"- {text}")
        lines.append("")  # riga vuota tra le voci

    return "\n".join(lines).strip()            

class UserProjectManagerWindow(QMainWindow):
    """
    @brief Main window for managing local ESPHome user projects.

    Displays project categories on the left and project cards on the right.
    Each card shows metadata and quick action buttons (open, edit, info, delete).

    @note Reads project metadata from `info.json` files and supports live updates.
    """    
    def __init__(self, main_window=None):
        """
        @brief Initializes the project manager window.

        Loads language, sets up layout with:
        - Category list on the left
        - Scrollable project card grid on the right
        - Footer with close button

        @param main_window Optional reference to the main application window (for callbacks).
        """        
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle(Translator.tr("user_projects_title"))
        self.setMinimumSize(1050, 600)
        self.setStyleSheet(f"background-color: {Pantone.SECONDARY_BG};")

        lang = get_setting("language")
        Translator.load_language(lang)

        QApplication.instance().setStyleSheet("""
            QLineEdit, QTextEdit {
                color: white;
                background-color: #2e2e2e;
                border: 1px solid #555;
                border-radius: 6px;
            }

            QLabel {
                color: white;
            }

            QMessageBox {
                background-color: #2e2e2e;
            }

            QPushButton {
                background-color: #444;
                color: white;
                padding: 6px 14px;
                border-radius: 6px;
            }

            QPushButton:hover {
                background-color: #555;
            }
        """)

        
        self.categories = [
            "Home_Monitoring", "Energy_Power", "Security_Alarm",
            "Actuators_IO", "Communication", "Automation_Logic", "Other_Misc"
        ]

        self.emoji_to_category = {
            "🏠 Home Monitoring": "Home_Monitoring",
            "⚡ Energy & Power": "Energy_Power",
            "🚪 Security & Alarm": "Security_Alarm",
            "🔧 Actuators & I/O": "Actuators_IO",
            "🌐 Communication": "Communication",
            "🧠 Automation Logic": "Automation_Logic",
            "🧪 Other / Misc": "Other_Misc"
        }


        self.project_data = self.load_project_metadata()
        self.category_to_cards = self.build_category_index()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        content_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        self.category_list = QListWidget()
        emoji_categories = [
            "🏠 Home Monitoring", "⚡ Energy & Power", "🚪 Security & Alarm",
            "🔧 Actuators & I/O", "🌐 Communication", "🧠 Automation Logic", "🧪 Other / Misc"
        ]
        for label in emoji_categories:
            item = QListWidgetItem(label)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.category_list.addItem(item)

        self.category_list.setFixedWidth(220)
        self.category_list.currentTextChanged.connect(self.load_category_cards)
        self.category_list.setStyleSheet(Pantone.LISTWIDGET_STYLE)
        content_layout.addWidget(self.category_list)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.scroll_content = QWidget()
        self.scroll_layout = QGridLayout()
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_content.setLayout(self.scroll_layout)

        self.scroll_area.setWidget(self.scroll_content)
        content_layout.addWidget(self.scroll_area)
        main_layout.addLayout(content_layout)
        self.category_list.setCurrentRow(0)

        # Footer con pulsanti
        footer = QWidget()
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(10, 10, 10, 10)
        footer_layout.setSpacing(20)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        #self.btn_load = QPushButton("📥 " + Translator.tr("load_button"))
        self.btn_close = QPushButton("❌ " + Translator.tr("close_button"))
        #self.btn_load.setFixedWidth(140)
        self.btn_close.setFixedWidth(140)

        #self.btn_load.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)
        self.btn_close.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)

        self.btn_close.clicked.connect(self.close)

        #footer_layout.addWidget(self.btn_load)
        footer_layout.addWidget(self.btn_close)

        footer.setLayout(footer_layout)
        main_layout.addWidget(footer)

    def load_project_metadata(self):
        """
        @brief Scans the user projects directory and reads metadata from each `info.json`.

        For each subfolder under each category in `DEFAULT_PROJECT_DIR`, loads:
        - name
        - author
        - version
        - update
        - description
        - changelog (optional)

        @return List of dictionaries, each containing one project's metadata.
        """        
        projects = []
        if not DEFAULT_PROJECT_DIR.exists():
            return projects

        for category in DEFAULT_PROJECT_DIR.iterdir():
            if not category.is_dir():
                continue
            for project in category.iterdir():
                info_path = project / "info.json"
                if info_path.exists():
                    try:
                        with open(info_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            data["__path"] = str(project)
                            data["category"] = category.name
                            projects.append(data)
                    except Exception as e:
                        print(f"Errore caricamento {info_path}: {e}")
        return projects

    def build_category_index(self):
        """
        @brief Builds a dictionary mapping categories to their associated project data.

        This helps quickly retrieve and display projects filtered by category.

        @return Dictionary: category -> list of project metadata.
        """        
        result = {cat: [] for cat in self.categories}
        for proj in self.project_data:
            cat = proj.get("category", "Other / Misc")
            result.setdefault(cat, []).append(proj)
        return result

    def load_category_cards(self, category_name):
        """
        @brief Loads and displays all project cards for the selected category.

        Clears existing cards and populates the scroll area with widgets,
        arranged in a 2-column grid.

        @param category_name Displayed category name (with emoji).
        """        
        category_key = self.emoji_to_category.get(category_name, category_name)

        # Pulisce tutte le card esistenti
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Aggiunge le card in griglia: 2 colonne
        row, col = 0, 0
        for project in self.category_to_cards.get(category_key, []):
            card = self.create_project_card(project)
            self.scroll_layout.addWidget(card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

    def create_project_card(self, project_data: dict) -> QWidget:
        """
        @brief Creates a QWidget representing a project card with metadata and buttons.

        Displays:
        - Project name, version, author, update date
        - Buttons for open, info, edit, delete

        @param project_data Dictionary with project metadata.
        @return QWidget with styled layout and connected actions.
        """        
        card = QWidget()
        card.setFixedSize(350, 250)
        card.setStyleSheet("""
            background-color: #2e2e2e;
            border: 1px solid #444;
            border-radius: 14px;
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # --- Colonna info ---
        info_layout = QVBoxLayout()
        for label in ["name", "version", "author", "update"]:
            title = QLabel(f"{label.capitalize()}:")
            title.setStyleSheet("color: #aaa; font-size: 9pt; font-weight: bold;")
            title.setFixedWidth(150)
            value = QLabel(project_data.get(label, "-"))
            value.setStyleSheet("color: #fff; font-size: 10pt;")
            value.setFixedWidth(150)
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value.setWordWrap(True)
            info_layout.addWidget(title)
            info_layout.addWidget(value)
            info_layout.addSpacing(6)

        info_layout.addStretch()
        layout.addLayout(info_layout)

        # --- Colonna pulsanti ---
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        button_layout.setSpacing(10)

        btn_open = QPushButton("📂 " + Translator.tr("project_open"))
        btn_info = QPushButton("ℹ️ " + Translator.tr("project_info"))
        btn_edit = QPushButton("✏️ " + Translator.tr("project_edit"))
        btn_delete = QPushButton("🗑️ " + Translator.tr("project_delete"))


        for btn in [btn_open, btn_info, btn_edit, btn_delete]:
            btn.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)
            btn.setFixedWidth(150)
            button_layout.addWidget(btn)

        btn_open.clicked.connect(lambda: self.apri_progetto(project_data))
        btn_info.clicked.connect(lambda: self.mostra_descrizione(project_data))
        btn_edit.clicked.connect(lambda: self.modifica_progetto(project_data))
        btn_delete.clicked.connect(lambda: self.elimina_progetto(project_data))

        layout.addLayout(button_layout)
        card.setLayout(layout)
        return card


    def apri_progetto(self, fields):
        """
        @brief Opens the selected project in the main window.

        Verifies the existence of the folder and YAML file,
        resets the tabs, and loads the project into the main interface.

        @param fields Dictionary containing `__path` and other metadata.
        """        
        path = Path(fields.get("__path", ""))
        print(f"[DEBUG] apri_progetto chiamato con path: {path}")
        print(f"[DEBUG] main_window è: {repr(self.main_window)}")
        print(f"[DEBUG] main_window.open_project esiste: {hasattr(self.main_window, 'open_project')}")

        if not path.exists():
            self.show_message(Translator.tr("error"), Translator.tr("folder_not_found"))
            return

        yaml_files = list(path.glob("*.yaml"))
        if not yaml_files:
            self.show_message(Translator.tr("error"), "Nessun file .yaml trovato nella cartella progetto.")
            return

        yaml_path = yaml_files[0]
        print(f"[DEBUG] YAML trovato: {yaml_path}")

        if self.main_window:
            # Verifica se è già aperto
            if os.path.abspath(str(self.main_window.last_save_path or "")) == os.path.abspath(str(yaml_path)):
                print("[DEBUG] Progetto già aperto, forzo ricaricamento")
            else:
                print("[DEBUG] Progetto diverso, procedo con apertura")

            self.main_window._reset_tabs()  # forza pulizia
            self.main_window.open_project(str(yaml_path))
            self.close()
        else:
            self.show_message("Stub", f"Apertura finta del progetto:\n{yaml_path}")

    def modifica_progetto(self, project_data):
        """
        @brief Opens the edit dialog to change project version and description.

        After confirmation, updates:
        - info.json
        - update timestamp
        - changelog array

        Refreshes project list and card display.

        @param project_data Dictionary with current project info.
        """        
        info_path = Path(project_data.get("__path", "")) / "info.json"
        if not info_path.exists():
            self.show_message(Translator.tr("error"), "File info.json non trovato.")
            return

        try:
            with open(info_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.show_message(Translator.tr("error"), f"{Translator.tr('read_info_error')}\n{e}")
            return

        dialog = ProjectEditDialog(
            version=data.get("version", ""),
            description=data.get("description", ""),
            parent=self
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        version, descrizione = dialog.get_data()

        # Aggiorna dati principali
        data["version"] = version
        data["description"] = descrizione
        data["update"] = datetime.today().strftime("%Y-%m-%d")

        # Aggiorna changelog incrementale
        changelog_entry = {
            "date": data["update"],
            "version": data["version"],
            "text": data["description"]
        }

        if "changelog" not in data or not isinstance(data["changelog"], list):
            data["changelog"] = []

        data["changelog"].append(changelog_entry)

        try:
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.show_message(Translator.tr("saved"), Translator.tr("save_success"))
            self.project_data = self.load_project_metadata()
            self.category_to_cards = self.build_category_index()
            self.load_category_cards(project_data["category"])
        except Exception as e:
            self.show_message(Translator.tr("error"), Translator.tr("save_error").format(e=e))


    def elimina_progetto(self, project_data):
        """
        @brief Permanently deletes the selected project folder after user confirmation.

        Triggers reload of metadata and cards.

        @param project_data Dictionary with current project info.
        """        
        path = Path(project_data.get("__path", ""))
        if not path.exists():
            self.show_message(Translator.tr("error"), Translator.tr("folder_not_found"))
            return

        conferma = QMessageBox.question(self,
            Translator.tr("confirm_delete"),
            Translator.tr("delete_confirm_msg").format(name=path.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if conferma != QMessageBox.StandardButton.Yes:
            return

        try:
            import shutil
            shutil.rmtree(path)
            self.show_message(Translator.tr("deleted"), Translator.tr("delete_success"))            
            self.project_data = self.load_project_metadata()
            self.category_to_cards = self.build_category_index()
            self.load_category_cards(project_data["category"])
        except Exception as e:
            self.show_message(Translator.tr("error"), Translator.tr("delete_error").format(e=e))

    def mostra_descrizione(self, project_data):
        """
        @brief Shows a dialog with the project description and formatted changelog.

        @param project_data Dictionary with metadata and changelog.
        """        
        description = project_data.get("description", "")
        changelog = project_data.get("changelog", [])  # deve essere una lista
        formatted_changelog = format_changelog(changelog)
        self.show_message_custom(Translator.tr("descrizione"), description, formatted_changelog)


    def show_message(self, title: str, text: str, icon=QMessageBox.Icon.Information):
        """
        @brief Displays a standard modal message box.

        @param title Window title of the dialog.
        @param text Message text to display.
        @param icon Icon to use (default: Information).
        """        
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        box.setText(text)
        box.setIcon(icon)
        box.setMinimumWidth(400)  # 👈 forza larghezza minima
        box.setStyleSheet(Pantone.QMESSAGE_BOX)
        box.exec()

    def show_message_custom(self, title: str, text: str, changelog: str):
        """
        @brief Displays a custom dialog with description and changelog formatted as Markdown.

        @param title Dialog title.
        @param text Description content.
        @param changelog Changelog content formatted for display.
        """        
        dlg = CustomMessageDialog(title, text, changelog, self)
        dlg.exec()        
