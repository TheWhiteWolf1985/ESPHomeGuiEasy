from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QStackedWidget, QWidget, QLabel, QComboBox, QCheckBox, QPushButton,
    QFileDialog, QLineEdit, QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt
from core.save_settings import save_settings
from gui.color_pantone import Pantone
from core.settings_db import get_setting
from PyQt6.QtWidgets import QMessageBox
from core.translator import Translator
from gui.splash_screen import SplashScreen
from PyQt6.QtGui import QPixmap, QIcon
import config.GUIconfig as conf
import os

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(Translator.tr("settings_title"))
        self.setFixedSize(800, 550)
        self.setStyleSheet(Pantone.DIALOG_STYLE)

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
        self.apply_button.setStyleSheet(Pantone.COMMON_BUTTON_STYLE)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        self.category_list.setCurrentRow(0)

    def switch_category(self, index):
        self.stack.setCurrentIndex(index)

    def save_settings(self):
        save_settings(self)

        QMessageBox.information(
            self,
            Translator.tr("settings_saved_title"),
            Translator.tr("settings_saved_message"),
            QMessageBox.StandardButton.Ok
        )


    def create_ui_page(self):
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
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel(Translator.tr("settings_language_label")))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Italiano", "Español", "Deutsch"])
        layout.addWidget(self.language_combo)

        # Leggi lingua salvata dal database
        saved_lang_code = get_setting("language")
        lang_map = {
            "en": "English",
            "it": "Italiano",
            "es": "Español",
            "de": "Deutsch"
        }

        if saved_lang_code and saved_lang_code in lang_map:
            try:
                idx = self.language_combo.findText(lang_map[saved_lang_code])
                if idx != -1:
                    self.language_combo.setCurrentIndex(idx)
            except Exception as e:
                print(f"Errore nel settaggio della lingua nella combobox: {e}")

        self.lang_prompt_checkbox = QCheckBox(Translator.tr("settings_show_lang_selector"))
        layout.addWidget(self.lang_prompt_checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.language_combo.setStyleSheet(Pantone.COMBO_STYLE)
        self.lang_prompt_checkbox.setStyleSheet(Pantone.CHECKBOX_STYLE)

        return page

    def create_paths_page(self):
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
        folder = QFileDialog.getExistingDirectory(self, Translator.tr("settings_browse"))
        if folder:
            self.project_path_edit.setText(folder)

    def aggiorna_tutte_le_label(self):
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

        pixmap = QPixmap(conf.SPLASH_IMAGE)
        splash = SplashScreen(pixmap)
        splash.check_online_version()  # solo controllo, nessun ciclo completo
        splash.show()

    def create_esphome_page(self):
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
        layout.addWidget(label_path)


        # Versione Python
        label_py = QLabel(f"🐍 {Translator.tr('python_version')}: {sys.version.split()[0]}")
        layout.addWidget(label_py)

        # Stato sito
        try:
            urllib.request.urlopen("https://esphome.io", timeout=3)
            online_label = QLabel(f"🌐 esphome.io: ✅ {Translator.tr('online')}")
        except:
            online_label = QLabel(f"🌐 esphome.io: ❌ {Translator.tr('offline')}")
        layout.addWidget(online_label)

        return page




if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    from core.translator import Translator
    Translator.load_language("en")  # o "it" se vuoi forzare in italiano

    from gui.color_pantone import Pantone
    app.setStyleSheet(Pantone.DIALOG_STYLE)

    dlg = SettingsDialog()
    dlg.show()
    sys.exit(app.exec())
