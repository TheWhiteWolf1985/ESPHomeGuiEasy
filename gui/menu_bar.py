from PyQt6.QtWidgets import QMenuBar, QFileDialog
from PyQt6.QtGui import QAction

class MainMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QMenuBar {
                background-color: #23272e;
                color: #d4d4d4;
                font-size: 12pt;
                font-weight: bold;
                border: none;
            }
            QMenuBar::item {
                background: transparent;
                color: #d4d4d4;
                padding: 6px 14px;
            }
            QMenuBar::item:selected {
                background: #333842;
                color: #61dafb;
                border-radius: 5px;
            }
            QMenuBar::item:pressed {
                background: #22262d;
                color: #3a9dda;
            }
            QMenu {
                background-color: #23272e;
                color: #d4d4d4;
                font-size: 11pt;
                border: 1.5px solid #2a2d2e;
                border-radius: 6px;
            }
            QMenu::item {
                background: transparent;
                color: #d4d4d4;
                padding: 6px 16px;
            }
            QMenu::item:selected {
                background-color: #3a9dda;
                color: #fff;
                border-radius: 4px;
            }
            QMenu::separator {
                height: 2px;
                background: #333842;
                margin-left: 6px;
                margin-right: 6px;
            }
        """)

        # --- FILE MENU ---
        file_menu = self.addMenu("&File")

        self.new_action = QAction("Nuovo progetto", self)
        self.new_action.setShortcut("Ctrl+N")
        file_menu.addAction(self.new_action)

        self.open_action = QAction("Apri progetto...", self)
        self.open_action.setShortcut("Ctrl+O")
        file_menu.addAction(self.open_action)

        self.save_action = QAction("Salva progetto", self)
        self.save_action.setShortcut("Ctrl+S")
        file_menu.addAction(self.save_action)

        self.saveas_action = QAction("Salva con nome...", self)
        self.saveas_action.setShortcut("Ctrl+Shift+S")
        file_menu.addAction(self.saveas_action)

        file_menu.addSeparator()

        self.import_action = QAction("Importa YAML...", self)
        file_menu.addAction(self.import_action)

        self.export_action = QAction("Esporta YAML...", self)
        file_menu.addAction(self.export_action)

        file_menu.addSeparator()

        self.exit_action = QAction("Esci", self)
        self.exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(self.exit_action)

        # Altri menu futuri (Modifica, Visualizza, ecc.) puoi aggiungerli qui

    # (Opzionale: qui puoi mettere funzioni utili per apri/salva file dialog ecc.)
