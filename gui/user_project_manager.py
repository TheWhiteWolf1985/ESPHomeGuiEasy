import os, sys, json
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QListWidget, QMessageBox, QListWidgetItem, QApplication,
    QInputDialog, QGridLayout
)
from PyQt6.QtCore import Qt
from gui.color_pantone import Pantone
from config.GUIconfig import DEFAULT_PROJECT_DIR
from datetime import datetime

class UserProjectManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Projects")
        self.setMinimumSize(1050, 600)
        self.setStyleSheet(f"background-color: {Pantone.SECONDARY_BG};")

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

        self.btn_load = QPushButton("📥 Carica")
        self.btn_close = QPushButton("❌ Chiudi")
        self.btn_load.setFixedWidth(140)
        self.btn_close.setFixedWidth(140)

        self.btn_load.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)
        self.btn_close.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)

        self.btn_close.clicked.connect(self.close)

        footer_layout.addWidget(self.btn_load)
        footer_layout.addWidget(self.btn_close)

        footer.setLayout(footer_layout)
        main_layout.addWidget(footer)

    def load_project_metadata(self):
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
        result = {cat: [] for cat in self.categories}
        for proj in self.project_data:
            cat = proj.get("category", "Other / Misc")
            result.setdefault(cat, []).append(proj)
        return result

    def load_category_cards(self, category_name):
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

        btn_open = QPushButton("📂 Apri")
        btn_info = QPushButton("ℹ️ Info")
        btn_edit = QPushButton("✏️ Modifica")
        btn_delete = QPushButton("🗑️ Elimina")

        for btn in [btn_open, btn_info, btn_edit, btn_delete]:
            btn.setStyleSheet(Pantone.COMMON_BUTTON_STYLE)
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
        path = fields.get("__path", "")
        self.show_message("Apertura", f"Apertura del progetto:\n{path}")

    def modifica_progetto(self, project_data):
        info_path = Path(project_data.get("__path", "")) / "info.json"
        if not info_path.exists():
            self.show_message("Errore", "File info.json non trovato.")
            return

        try:
            with open(info_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.show_message("Errore", f"Errore lettura info.json:\n{e}")
            return

        version, ok1 = QInputDialog.getText(self, "Modifica versione", "Nuova versione:", text=data.get("version", ""))
        if not ok1:
            return
        descrizione, ok2 = QInputDialog.getMultiLineText(self, "Modifica descrizione", "Changelog:", text=data.get("description", ""))
        if not ok2:
            return

        data["version"] = version.strip()
        data["description"] = descrizione.strip()
        data["update"] = datetime.today().strftime("%Y-%m-%d")

        try:
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.show_message("Salvato", "Modifiche salvate con successo.")
            self.project_data = self.load_project_metadata()
            self.category_to_cards = self.build_category_index()
            self.load_category_cards(project_data["category"])
        except Exception as e:
            self.show_message("Errore", f"Errore salvataggio:\n{e}")

    def elimina_progetto(self, project_data):
        path = Path(project_data.get("__path", ""))
        if not path.exists():
            self.show_message("Errore", "Cartella progetto non trovata.")
            return

        conferma = QMessageBox.question(self,
            "Conferma eliminazione",
            f"Sei sicuro di voler eliminare il progetto:\n{path.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if conferma != QMessageBox.StandardButton.Yes:
            return

        try:
            import shutil
            shutil.rmtree(path)
            self.show_message("Eliminato", "Progetto eliminato con successo.")            
            self.project_data = self.load_project_metadata()
            self.category_to_cards = self.build_category_index()
            self.load_category_cards(project_data["category"])
        except Exception as e:
            self.show_message("Errore", f"Errore durante l'eliminazione:\n{e}")

    def mostra_descrizione(self, project_data):
        name = project_data.get("name", "")            
        self.show_message("Stub", f"progetto {name}")

    def show_message(self, title: str, text: str, icon=QMessageBox.Icon.Information):
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(text)
        box.setIcon(icon)

        box.setStyleSheet(Pantone.QMESSAGE_BOX)

        box.exec()



# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = UserProjectManagerWindow()
#     window.show()
#     sys.exit(app.exec())
