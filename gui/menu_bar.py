from PyQt6.QtWidgets import *
from PyQt6.QtGui import QAction
from core.translator import Translator
from gui.color_pantone import Pantone
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from gui.language_selection_dialog import LanguageSelectionDialog
from core.settings_db import set_setting, get_setting
from core.settings_db import get_recent_files
from PyQt6.QtWidgets import QFileDialog
import config.GUIconfig as conf
import os
from functools import partial
from gui.project_gallery_window import ProjectGalleryWindow


class MainMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet(Pantone.MENU_BAR)

        # --- FILE MENU ---
        self.file_menu = self.addMenu(Translator.tr("menu_file"))

        self.new_action = QAction(Translator.tr("new_project"), self)
        self.new_action.setShortcut("Ctrl+N")
        self.file_menu.addAction(self.new_action)

        self.open_action = QAction(Translator.tr("open_project"), self)
        self.open_action.setShortcut("Ctrl+O")
        self.file_menu.addAction(self.open_action)

        self.save_action = QAction(Translator.tr("save_project"), self)
        self.save_action.setShortcut("Ctrl+S")
        self.file_menu.addAction(self.save_action)

        self.saveas_action = QAction(Translator.tr("save_as"), self)
        self.saveas_action.setShortcut("Ctrl+Shift+S")
        self.file_menu.addAction(self.saveas_action)

        self.file_menu.addSeparator()

        self.import_action = QAction(Translator.tr("import_yaml"), self)
        self.file_menu.addAction(self.import_action)

        self.export_action = QAction(Translator.tr("export_yaml"), self)
        self.file_menu.addAction(self.export_action)

        self.file_menu.addSeparator()      

        self.import_project_action = QAction(Translator.tr("import_project"), self)
        self.import_project_action.triggered.connect(self.parent().import_project)
        self.file_menu.addAction(self.import_project_action)

        self.export_project_action = QAction(Translator.tr("export_project"), self)
        self.export_project_action.triggered.connect(self.parent().export_project)
        self.file_menu.addAction(self.export_project_action)

        self.file_menu.addSeparator()

        self.exit_action = QAction(Translator.tr("exit"), self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.file_menu.addAction(self.exit_action)

        self.file_menu.addSeparator()
        self.recent_file_actions = []
        self._update_recent_files_menu()        

        # MENU PROGETTI

        self.project_menu = self.addMenu(Translator.tr("menu_progetti"))

        self.community_project_action = QAction(Translator.tr("progetti_community"), self)
        self.community_project_action.triggered.connect(self.open_project_gallery_window)
        self.project_menu.addAction(self.community_project_action)

        # MENU IMPOSTAZIONI

        self.settings_menu = self.addMenu(Translator.tr("menu_settings"))

        self.language_action = QAction(Translator.tr("menu_language"), self)
        self.language_action.triggered.connect(self.open_language_dialog)
        self.settings_menu.addAction(self.language_action)

        self.current_language = Translator.current_language()

                # --- HELP MENU ---
        help_menu = self.addMenu("❓")
        self.about_action = QAction(Translator.tr("menu_about"), self)
        self.documentation_action = QAction(Translator.tr("menu_documentation"), self)
        help_menu.addAction(self.about_action)
        help_menu.addAction(self.documentation_action)
        self.about_action.triggered.connect(self.show_about_dialog)
        # Deleghiamo la documentazione alla finestra principale
        self.documentation_action.triggered.connect(
            lambda: self.parent().show_documentation()
        )

    def update_labels(self):
        # Elimina tutti i menu e ricrea da zero
        self.clear()

        # FILE MENU
        self.file_menu = self.addMenu(Translator.tr("menu_file"))
        self.new_action = QAction(Translator.tr("new_project"), self)
        self.open_action = QAction(Translator.tr("open_project"), self)
        self.save_action = QAction(Translator.tr("save_project"), self)
        self.saveas_action = QAction(Translator.tr("save_as"), self)
        self.import_action = QAction(Translator.tr("import_yaml"), self)
        self.export_action = QAction(Translator.tr("export_yaml"), self)
        self.import_project_action = QAction(Translator.tr("import_project"), self)
        self.export_project_action = QAction(Translator.tr("export_project"), self)
        self.exit_action = QAction(Translator.tr("exit"), self)

        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.saveas_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.import_action)
        self.file_menu.addAction(self.export_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.import_project_action)
        self.file_menu.addAction(self.export_project_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self._update_recent_files_menu()

        # PROJECT MENU
        self.project_menu = self.addMenu(Translator.tr("menu_progetti"))
        self.community_project_action = QAction(Translator.tr("progetti_community"), self)
        self.community_project_action.triggered.connect(self.open_project_gallery_window)
        self.project_menu.addAction(self.community_project_action)

        # SETTINGS MENU
        self.settings_menu = self.addMenu(Translator.tr("menu_settings"))
        self.language_action = QAction(Translator.tr("menu_language"), self)
        self.language_action.triggered.connect(self.open_language_dialog)
        self.settings_menu.addAction(self.language_action)

        # HELP MENU
        help_menu = self.addMenu("❓")
        self.about_action.setText(Translator.tr("menu_about"))
        self.documentation_action.setText(Translator.tr("menu_documentation"))
        help_menu.addAction(self.about_action)
        help_menu.addAction(self.documentation_action)



    def show_about_dialog(self):
        # Prendi dati versione (da config)
        version = getattr(conf, "APP_VERSION", "1.0.0")
        release_date = getattr(conf, "APP_RELEASE_DATE", "2025-05-30")
        icon_path = getattr(conf, "SW_ICON_PATH", "")

        dlg = QDialog(self)
        dlg.setWindowTitle("Informazioni su ESPHomeGuiEasy")
        dlg.setStyleSheet(Pantone.DIALOG_STYLE)
        layout = QVBoxLayout()

        # Logo (se presente)
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(90, 90)
            lbl_logo = QLabel()
            lbl_logo.setPixmap(pix)
            lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl_logo)
        else:
            layout.addWidget(QLabel("ESPHomeGuiEasy"))

        # Info testo
        lbl_info = QLabel(
            f"<b>ESPHomeGuiEasy</b><br>"
            f"Versione: <b>{version}</b><br>"
            f"Data rilascio: <b>{release_date}</b><br>"
            f"<br>"
            f"Copyright (c) 2025 Juri<br>"
            f"Licenza: AGPLv3 - Uso non commerciale"
        )
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_info)

        # Bottone chiudi
        btn = QPushButton("Chiudi")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        dlg.setLayout(layout)
        dlg.exec()

    def open_language_dialog(self):
        dlg = LanguageSelectionDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.get_selected_language():
            lang = dlg.get_selected_language()
            from core.translator import Translator
            Translator.load_language(lang)
            set_setting("language", lang)

            # Aggiorna GUI
            if hasattr(self.parent(), "aggiorna_tutte_le_label"):
                self.parent().aggiorna_tutte_le_label()

    def open_project_gallery_window(self):
        """
        @brief Apre la finestra dei progetti della community.
        """
        if not hasattr(self, "_project_gallery_window") or self._project_gallery_window is None:
            self._project_gallery_window = ProjectGalleryWindow()

        self._project_gallery_window.show()
        self._project_gallery_window.raise_()
        self._project_gallery_window.activateWindow()


    def _update_recent_files_menu(self):
        # Rimuove le precedenti
        for act in self.recent_file_actions:
            self.file_menu.removeAction(act)
        self.recent_file_actions.clear()

        recent_files = get_recent_files(limit=4)
        if recent_files:
            self.file_menu.addSeparator()
            for path, name in recent_files:
                action = QAction(name, self)
                action.setToolTip(path)
                action.triggered.connect(self._make_open_file_handler(path))
                self.file_menu.addAction(action)
                self.recent_file_actions.append(action)

    def _open_recent_file(self, path: str):
        parent = self.parent()
        if parent and callable(getattr(parent, "open_project", None)):
            parent.open_project(path)

    def _make_open_file_handler(self, path: str):
        return lambda checked=False: self._open_recent_file(path)
