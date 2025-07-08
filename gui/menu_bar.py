# -*- coding: utf-8 -*-
"""
@file menu_bar.py
@brief Main menu bar of the application, including File, Project, Settings, and Help menus.

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Handles menu creation, recent files list, project galleries, settings dialog,
and about dialog.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtWidgets import *
from PyQt6.QtGui import QAction
from core.translator import Translator
from gui.color_pantone import Pantone
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from core.settings_db import get_recent_files
import config.GUIconfig as conf
import os, webbrowser
from gui.project_gallery_window import ProjectGalleryWindow
from gui.user_project_manager import UserProjectManagerWindow
from gui.setting_menu import SettingsDialog


class MainMenuBar(QMenuBar):
    """
    @brief Implements the application’s main menu bar with various menus and actions.

    Creates and updates menus dynamically, manages recent files,
    and provides dialogs for settings, project galleries, and about info.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setStyleSheet(Pantone.MENU_BAR)
        self.recent_file_actions = []
        self.create_menus()

    def update_labels(self):
        self.clear()
        self.create_menus()

    def create_menus(self):
        parent = self.parent()

        # FILE MENU
        self.file_menu = self.addMenu(Translator.tr("menu_file"))

        self.header_action_proj = QWidgetAction(self)
        self.label_proj = QLabel(f"📁 {Translator.tr('menu_header_projects')}")
        self.label_proj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_proj.setStyleSheet("""
            QLabel {
                background-color: #2c2c2c;
                color: #ffffff;
                font-weight: bold;
                padding: 6px;
                border-top: 1px solid #555;
                border-bottom: 1px solid #555;
            }
        """)
        self.header_action_proj.setDefaultWidget(self.label_proj)
        self.file_menu.addAction(self.header_action_proj)

        self.new_action = QAction("🆕 " + Translator.tr("new_project"), self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.main_window.nuovo_progetto)
        self.file_menu.addAction(self.new_action)

        self.import_project_action = QAction("📂 " + Translator.tr("import_project"), self)
        self.import_project_action.triggered.connect(parent.import_project)
        self.file_menu.addAction(self.import_project_action)

        self.export_project_action = QAction("📄 " + Translator.tr("export_project"), self)
        self.export_project_action.triggered.connect(parent.export_project)
        self.file_menu.addAction(self.export_project_action)

        self.file_menu.addSeparator()

        self.header_action_yaml = QWidgetAction(self)
        self.label_yaml = QLabel(f"📄 {Translator.tr('menu_header_yaml')}")
        self.label_yaml.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_yaml.setStyleSheet("""
            QLabel {
                background-color: #2c2c2c;
                color: #ffffff;
                font-weight: bold;
                padding: 6px;
                border-top: 1px solid #555;
                border-bottom: 1px solid #555;
            }
        """)
        self.header_action_yaml.setDefaultWidget(self.label_yaml)
        self.file_menu.addAction(self.header_action_yaml)

        self.open_action = QAction("📁 " + Translator.tr("open_project"), self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(lambda _: parent.open_project_dialog())
        self.file_menu.addAction(self.open_action)

        self.save_action = QAction("📂 " + Translator.tr("save_project"), self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(parent.salva_progetto)
        self.file_menu.addAction(self.save_action)

        self.saveas_action = QAction("📁 " + Translator.tr("save_as"), self)
        self.saveas_action.setShortcut("Ctrl+Shift+S")
        self.saveas_action.triggered.connect(parent.salva_con_nome)
        self.file_menu.addAction(self.saveas_action)

        self.import_action = QAction("📅 " + Translator.tr("import_yaml"), self)
        self.import_action.triggered.connect(parent.importa_yaml)
        self.file_menu.addAction(self.import_action)

        self.export_action = QAction("📄 " + Translator.tr("export_yaml"), self)
        self.export_action.triggered.connect(parent.esporta_yaml)
        self.file_menu.addAction(self.export_action)

        self.file_menu.addSeparator()

        self.exit_action = QAction("❌ " + Translator.tr("exit"), self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(parent.close)
        self.file_menu.addAction(self.exit_action)

        self._update_recent_files_menu()

        # PROJECT MENU
        self.project_menu = self.addMenu(Translator.tr("menu_progetti"))
        self.community_project_action = QAction(Translator.tr("progetti_community"), self)
        self.community_project_action.triggered.connect(self.open_project_gallery_window)
        self.project_menu.addAction(self.community_project_action)

        self.user_projects_action = QAction(Translator.tr("user_projects_title"), self)
        self.user_projects_action.triggered.connect(self.open_user_project_gallery_window)
        self.project_menu.addAction(self.user_projects_action)

        # SETTINGS MENU
        self.settings_menu = self.addMenu(Translator.tr("menu_settings"))
        self.full_settings_action = QAction(Translator.tr("menu_full_settings"), self)
        self.full_settings_action.triggered.connect(self.open_full_settings_dialog)
        self.settings_menu.addAction(self.full_settings_action)

        # HELP MENU
        help_menu = self.addMenu("❓")

        self.about_action = QAction(Translator.tr("menu_about"), self)
        self.about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(self.about_action)

        self.docs_action = QAction(Translator.tr("menu_documentation"), self)
        self.docs_action.triggered.connect(self.open_docs)
        help_menu.addAction(self.docs_action)


    def _update_recent_files_menu(self):
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

    def show_about_dialog(self):
        version = getattr(conf, "APP_VERSION", "1.0.0")
        release_date = getattr(conf, "APP_RELEASE_DATE", "2025-05-30")
        icon_path = getattr(conf, "SW_ICON_PATH", "")

        dlg = QDialog(self)
        dlg.setWindowTitle("Informazioni su ESPHomeGuiEasy")
        dlg.setStyleSheet(Pantone.DIALOG_STYLE)
        layout = QVBoxLayout()

        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(90, 90)
            lbl_logo = QLabel()
            lbl_logo.setPixmap(pix)
            lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl_logo)
        else:
            layout.addWidget(QLabel("ESPHomeGuiEasy"))

        lbl_info = QLabel(
            f"<b>ESPHomeGuiEasy</b><br>"
            f"Versione: <b>{version}</b><br>"
            f"Data rilascio: <b>{release_date}</b><br><br>"
            f"Copyright (c) 2025 Juri<br>"
            f"Licenza: AGPLv3 - Uso non commerciale"
        )
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_info)

        btn = QPushButton("Chiudi")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        dlg.setLayout(layout)
        dlg.exec()

    def open_project_gallery_window(self):
        if not hasattr(self, "_project_gallery_window") or self._project_gallery_window is None:
            self._project_gallery_window = ProjectGalleryWindow()
        self._project_gallery_window.show()
        self._project_gallery_window.raise_()
        self._project_gallery_window.activateWindow()

    def open_user_project_gallery_window(self):
        # Se l'oggetto esiste ma è stato chiuso, lo azzero
        if hasattr(self, "_user_project_gallery_window"):
            if self._user_project_gallery_window is not None and not self._user_project_gallery_window.isVisible():
                self._user_project_gallery_window = None

        if not hasattr(self, "_user_project_gallery_window") or self._user_project_gallery_window is None:
            self._user_project_gallery_window = UserProjectManagerWindow(main_window=self.main_window)

        self._user_project_gallery_window.show()
        self._user_project_gallery_window.raise_()
        self._user_project_gallery_window.activateWindow()


    def open_full_settings_dialog(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def open_docs(self):
        """
        @brief Opens the local Doxygen documentation in the default web browser.
        """
        doc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../docs/html/index.html"))
        if os.path.exists(doc_path):
            webbrowser.open_new_tab(f"file://{doc_path}")
        else:
            QMessageBox.warning(None, Translator.tr("menu_documentation"), Translator.tr("error_docs_not_found"))

