# -*- coding: utf-8 -*-
"""
@file setting_menu.py
@brief Settings dialog with multiple categorized pages for ESPHomeGUIeasy.

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Implements a QDialog containing a side category list and stacked pages for:
- UI preferences (theme, font size, spacing)
- Language selection
- Default project folder paths
- Startup options (splash screen, update checks)
- Advanced settings (debug logs, cache clearing)
- ESPHome version and path information
- Log file access

Includes apply and cancel buttons and manages saving settings to the database.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QStackedWidget, QWidget, QLabel, QComboBox, QCheckBox, QPushButton,
    QFileDialog, QLineEdit, QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt
from core.save_settings import save_settings, set_setting
from gui.color_pantone import Pantone
from core.settings_db import get_setting
from PyQt6.QtWidgets import QMessageBox
from core.translator import Translator
from gui.splash_screen import SplashScreen
from PyQt6.QtGui import QPixmap, QIcon
from config.GUIconfig import GlobalPaths, conf
import os
import webbrowser
from core.log_handler import GeneralLogHandler as logger
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

class SettingsDialog(QDialog):
    """
    @brief Main settings dialog window organizing preferences into categorized tabs.

    Handles UI initialization, user interactions, and saving configuration changes.
    Connects GUI controls to underlying database and application logic.
    """
    def __init__(self, parent=None):
        """
        @brief Initializes the settings dialog UI, including category list and stacked pages.

        Sets up buttons, connects signals, and applies styling.
        """
        super().__init__(parent)
        self.setWindowTitle(Translator.tr("settings_title"))
        self.setFixedSize(800, 550)
        self.setStyleSheet(Pantone.DIALOG_STYLE)
        self.logger = logger()

        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setStyleSheet("color: #444; margin: 10px 0;")


        main_layout = QVBoxLayout(self)

        content_layout = QHBoxLayout()

        # --- Pannello laterale categorie ---
        self.category_list = QListWidget()
        self.category_list.setFixedWidth(240)
        self.category_list.addItem(Translator.tr("settings_ui"))
        self.category_list.addItem(Translator.tr("settings_language"))
        self.category_list.addItem(Translator.tr("settings_paths"))
        self.category_list.addItem(Translator.tr("settings_startup"))
        self.category_list.addItem(Translator.tr("settings_advanced"))
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets/icon", "esphome.png")
        icon = QIcon(icon_path)
        esphome_item = QListWidgetItem(icon, "ESPHome Version")
        self.category_list.addItem(esphome_item)
        self.category_list.addItem(Translator.tr("settings_log"))
        self.category_list.currentRowChanged.connect(self.switch_category)
        self.category_list.setSpacing(6)
        self.category_list.setStyleSheet(Pantone.LISTWIDGET_STYLE)

        # Nasconde le barre di scorrimento
        self.category_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.category_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Disabilita lo scrolling manuale pur mantenendo la selezionabilità
        self.category_list.wheelEvent = lambda event: None
        self.category_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.category_list.setHorizontalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)

        content_layout.addWidget(self.category_list)

        # --- Pannello destro con pagine ---
        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_ui_page())
        self.stack.addWidget(self.create_language_page())
        self.stack.addWidget(self.create_paths_page())
        self.stack.addWidget(self.create_startup_page())
        self.stack.addWidget(self.create_advanced_page())
        self.stack.addWidget(self.create_esphome_page())
        self.stack.addWidget(self.create_log_page())

        content_layout.addWidget(self.stack)
        main_layout.addLayout(content_layout)

        # --- Pulsanti Applica e Annulla ---
        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.apply_button = QPushButton(Translator.tr("apply_button"))
        self.apply_button.clicked.connect(self.save_settings)  # Salva configurazione
        self.apply_button.setStyleSheet(Pantone.COMMON_BUTTON_STYLE)
        button_layout.addWidget(self.apply_button)
        

        self.cancel_button = QPushButton(Translator.tr("cancel_button"))
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet(Pantone.COMMON_BUTTON_STYLE)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        self.category_list.setCurrentRow(0)

    def switch_category(self, index):
        """
        @brief Switches the visible settings page based on category list selection.

        @param index Index of the selected category.
        """
        self.stack.setCurrentIndex(index)

    def save_settings(self):
        """
        @brief Saves current settings from all pages to the configuration database.

        Calls helper functions and sets custom ESPHome CLI path if provided.
        Shows an information message box on success.
        """
        save_settings(self)

        if hasattr(self, "custom_esphome_input"):
          set_setting("custom_esphome_path", self.custom_esphome_input.text().strip())


        QMessageBox.information(
            self,
            Translator.tr("settings_saved_title"),
            Translator.tr("settings_saved_message"),
            QMessageBox.StandardButton.Ok
        )


    def create_ui_page(self):
        """
        @brief Creates the UI preferences page with theme, font size, and compact spacing options.
        """
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel(Translator.tr("settings_theme")))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "System Default"])
        layout.addWidget(self.theme_combo)

        layout.addWidget(QLabel(Translator.tr("settings_font_size")))
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Small", "Medium", "Large"])
        layout.addWidget(self.font_combo)

        self.compact_checkbox = QCheckBox(Translator.tr("settings_compact_spacing"))
        layout.addWidget(self.compact_checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.theme_combo.setStyleSheet(Pantone.COMBO_STYLE)
        self.font_combo.setStyleSheet(Pantone.COMBO_STYLE)
        self.compact_checkbox.setStyleSheet(Pantone.CHECKBOX_STYLE)

        return page

    def create_language_page(self):
        """
        @brief Creates the language selection page with combo box and language prompt option.
        """
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel(Translator.tr("settings_language_label")))
        self.language_combo = QComboBox()
        lang_map = Translator.get_language_name_map()
        self.lang_code_from_name = {v: k for k, v in lang_map.items()}  # mapping inverso
        self.language_combo.addItems(lang_map.values())


        saved_lang_code = get_setting("language")
        if saved_lang_code and saved_lang_code in lang_map:
            try:
                name = lang_map[saved_lang_code]
                idx = self.language_combo.findText(name)
                if idx != -1:
                    self.language_combo.setCurrentIndex(idx)
            except Exception as e:
                logger.warning(f"Errore nel settaggio della lingua nella combobox: {e}")

        layout.addWidget(self.language_combo)
        self.lang_prompt_checkbox = QCheckBox(Translator.tr("settings_show_lang_selector"))
        layout.addWidget(self.lang_prompt_checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.language_combo.setStyleSheet(Pantone.COMBO_STYLE)
        self.lang_prompt_checkbox.setStyleSheet(Pantone.CHECKBOX_STYLE)

        return page

    def create_paths_page(self):
        """
        @brief Creates the paths page for selecting default project folder and cache clearing.
        """
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel(Translator.tr("settings_default_project_folder")))
        self.project_path_edit = QLineEdit()
        # Carica il path salvato dal DB, se esiste
        saved_path = get_setting("default_project_path")
        if saved_path:
            self.project_path_edit.setText(saved_path)

        browse_btn = QPushButton(Translator.tr("settings_browse"))
        browse_btn.clicked.connect(self.browse_project_folder)
        layout.addWidget(self.project_path_edit)
        layout.addWidget(browse_btn)

        self.clear_cache_btn = QPushButton(Translator.tr("settings_clear_cache"))
        layout.addWidget(self.clear_cache_btn)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.project_path_edit.setStyleSheet(Pantone.LINEEDIT_STYLE)
        browse_btn.setStyleSheet(Pantone.BUTTON_STYLE)
        self.clear_cache_btn.setStyleSheet(Pantone.BUTTON_STYLE)

        return page

    def create_startup_page(self):
        """
        @brief Creates the startup options page for splash screen and update check toggles.
        """
        page = QWidget()
        layout = QVBoxLayout(page)

        self.splash_checkbox = QCheckBox(Translator.tr("settings_splash"))
        layout.addWidget(self.splash_checkbox)

        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.update_checkbox = QCheckBox(Translator.tr("settings_check_updates"))
        layout.addWidget(self.update_checkbox)

        self.check_update_btn = QPushButton(Translator.tr("settings_check_updates_now"))
        self.check_update_btn.clicked.connect(self.check_updates_now)
        layout.addWidget(self.check_update_btn)
        self.check_update_btn.setStyleSheet(Pantone.BUTTON_STYLE)


        self.restore_checkbox = QCheckBox(Translator.tr("settings_open_last"))
        layout.addWidget(self.restore_checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        saved_splash = get_setting("show_splash")
        if saved_splash == "1":
            self.splash_checkbox.setChecked(True)
        elif saved_splash == "0":
            self.splash_checkbox.setChecked(False)


        self.splash_checkbox.setStyleSheet(Pantone.CHECKBOX_STYLE)
        self.update_checkbox.setStyleSheet(Pantone.CHECKBOX_STYLE)
        self.restore_checkbox.setStyleSheet(Pantone.CHECKBOX_STYLE)

        return page

    def create_advanced_page(self):
        """
        @brief Creates the advanced options page for debug log enabling and cache refresh.
        """
        page = QWidget()
        layout = QVBoxLayout(page)

        self.debug_checkbox = QCheckBox(Translator.tr("settings_enable_devlog"))
        layout.addWidget(self.debug_checkbox)

        self.logfile_checkbox = QCheckBox(Translator.tr("settings_save_debug_log"))
        layout.addWidget(self.logfile_checkbox)

        self.force_refresh_btn = QPushButton(Translator.tr("settings_force_refresh"))
        layout.addWidget(self.force_refresh_btn)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.debug_checkbox.setStyleSheet(Pantone.CHECKBOX_STYLE)
        self.logfile_checkbox.setStyleSheet(Pantone.CHECKBOX_STYLE)
        self.force_refresh_btn.setStyleSheet(Pantone.BUTTON_STYLE)

        return page

    def browse_project_folder(self):
        """
        @brief Opens a folder selection dialog to change the default project folder path.
        """
        folder = QFileDialog.getExistingDirectory(self, Translator.tr("settings_browse"))
        if folder:
            self.project_path_edit.setText(folder)

    def aggiorna_tutte_le_label(self):
        """
        @brief Updates all UI text labels to reflect current language selection.
        """
        self.setWindowTitle(Translator.tr("settings_title"))

        self.category_list.clear()
        self.category_list.addItem(Translator.tr("settings_ui"))
        self.category_list.addItem(Translator.tr("settings_language"))
        self.category_list.addItem(Translator.tr("settings_paths"))
        self.category_list.addItem(Translator.tr("settings_startup"))
        self.category_list.addItem(Translator.tr("settings_advanced"))

        self.apply_button.setText(Translator.tr("apply_button"))
        self.cancel_button.setText(Translator.tr("cancel_button"))

        # UI Page
        self.stack.widget(0).layout().itemAt(0).widget().setText(Translator.tr("settings_theme"))
        self.stack.widget(0).layout().itemAt(2).widget().setText(Translator.tr("settings_font_size"))
        self.compact_checkbox.setText(Translator.tr("settings_compact_spacing"))

        # Language Page
        self.stack.widget(1).layout().itemAt(0).widget().setText(Translator.tr("settings_language_label"))
        self.lang_prompt_checkbox.setText(Translator.tr("settings_show_lang_selector"))

        # Paths Page
        self.stack.widget(2).layout().itemAt(0).widget().setText(Translator.tr("settings_default_project_folder"))
        self.stack.widget(2).layout().itemAt(3).widget().setText(Translator.tr("settings_browse"))
        self.clear_cache_btn.setText(Translator.tr("settings_clear_cache"))

        # Startup Page
        self.splash_checkbox.setText(Translator.tr("settings_splash"))
        self.update_checkbox.setText(Translator.tr("settings_check_updates"))
        self.restore_checkbox.setText(Translator.tr("settings_open_last"))

        # Advanced Page
        self.debug_checkbox.setText(Translator.tr("settings_enable_devlog"))
        self.logfile_checkbox.setText(Translator.tr("settings_save_debug_log"))
        self.force_refresh_btn.setText(Translator.tr("settings_force_refresh"))

    def check_updates_now(self):
        """
        @brief Triggers an immediate online version check via the splash screen module.
        """
        if self.logger:
            self.logger.log(Translator.tr("log_opening_update_dialog"), "info")
        pixmap = QPixmap(GlobalPaths.SPLASH_IMAGE)
        splash = SplashScreen(pixmap)
        splash.check_online_version()  # solo controllo, nessun ciclo completo
        splash.show()

    def create_esphome_page(self):
        """
        @brief Creates the ESPHome information page showing version, executable path, Python version, and online status.

        Includes an input for custom ESPHome CLI path and a download button if not found.
        """
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Logo
        esphome_img = os.path.join(os.path.dirname(__file__), "..", "assets/icon", "esphome.png")
        logo = QPixmap(esphome_img).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label = QLabel()
        logo_label.setPixmap(logo)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Titolo
        label_title = QLabel(Translator.tr("settings_esphome_title"))
        label_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(label_title)

        # Recupero informazioni
        import subprocess, shutil, sys, urllib.request

        # Versione ESPHome
        try:
            result = subprocess.run(["esphome", "version"], capture_output=True, text=True)
            version = result.stdout.strip()
        except Exception as e:
            version = Translator.tr("esphome_version_error").format(error=str(e))

        label_version = QLabel(f"🔢 {version}")
        layout.addWidget(label_version)

        # Percorso eseguibile
        esphome_path = shutil.which("esphome")
        if esphome_path:
            label_path = QLabel(f"📁 {Translator.tr('esphome_path')}: {esphome_path}")
            label_path.setWordWrap(True)
            label_path.setMaximumWidth(700)
            label_path.setToolTip(esphome_path)
            label_path.setStyleSheet("font-family: Consolas, monospace;")
        else:
            label_path = QLabel(f"❌ {Translator.tr('esphome_not_found')}")
            download_btn = QPushButton(Translator.tr("download_esphome_button"))
            download_btn.setStyleSheet(Pantone.COMMON_BUTTON_STYLE)
            download_btn.clicked.connect(lambda: webbrowser.open("https://esphome.io/guides/installing_esphome.html"))
            layout.addWidget(download_btn)
        
        layout.addWidget(label_path)


        # Versione Python
        label_py = QLabel(f"🐍 {Translator.tr('python_version')}: {sys.version.split()[0]}")
        layout.addWidget(label_py)

        # Percorso personalizzato eseguibile ESPHome
        layout.addSpacing(10)
        custom_path_label = QLabel(Translator.tr("custom_esphome_path_label"))
        layout.addWidget(custom_path_label)

        path_layout = QHBoxLayout()
        self.custom_esphome_input = QLineEdit()
        self.custom_esphome_input.setPlaceholderText("C:/Percorso/esp/esphome.exe")
        self.custom_esphome_input.setStyleSheet(Pantone.LINEEDIT_STYLE)
        path_layout.addWidget(self.custom_esphome_input)

        browse_btn = QPushButton(Translator.tr("settings_browse"))
        browse_btn.setStyleSheet(Pantone.BUTTON_STYLE)
        browse_btn.clicked.connect(self.browse_esphome_executable)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        # Carica valore salvato, se esiste
        saved_custom_path = get_setting("custom_esphome_path")
        if saved_custom_path:
            self.custom_esphome_input.setText(saved_custom_path)

        # Stato sito
        try:
            urllib.request.urlopen("https://esphome.io", timeout=3)
            online_label = QLabel(f"🌐 esphome.io: ✅ {Translator.tr('online')}")
        except:
            online_label = QLabel(f"🌐 esphome.io: ❌ {Translator.tr('offline')}")
        layout.addWidget(online_label)

        return page
    
    def create_log_page(self):
        """
        @brief Creates a page with a button to open the application log file.
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.open_log_btn = QPushButton(Translator.tr("open_log_button"))
        self.open_log_btn.clicked.connect(self.open_log_file)
        self.open_log_btn.setStyleSheet(Pantone.BUTTON_STYLE)

        layout.addWidget(self.open_log_btn)
        return page

    def open_log_file(self):
        """
        @brief Opens the log file using the system default application if the file exists,
        otherwise shows a warning message.
        """
        log_path = conf.LOG_PATH  # OS-specific, già corretto
        if os.path.exists(log_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(log_path)))
        else:
            QMessageBox.warning(self, Translator.tr("warning"), Translator.tr("log_file_not_found"))

    def browse_esphome_executable(self):
        file_path, _ = QFileDialog.getOpenFileName(self, Translator.tr("settings_browse"), "", "Executables (*.exe);;All Files (*)")
        if file_path:
            self.custom_esphome_input.setText(file_path)