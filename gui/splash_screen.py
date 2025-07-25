import os
import sys
import json
import config.GUIconfig as conf
import urllib.request
import webbrowser
from PyQt6.QtWidgets import QLabel, QProgressBar, QApplication, QMessageBox, QSplashScreen
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer, QSize
from importlib.metadata import version, PackageNotFoundError
from core.translator import Translator
from core.settings_db import init_db, get_setting, set_setting, get_user_db_path
from config.GUIconfig import USER_DB_PATH, DEFAULT_BUILD_DIR
import sqlite3
import shutil
from core.log_handler import GeneralLogHandler

class SplashScreen(QSplashScreen):
    def __init__(self, pixmap):
        scaled_pixmap = pixmap.scaled(QSize(500, 500), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        super().__init__(scaled_pixmap)
        self.setFixedSize(500, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFont(QFont("Arial", 10))

        self.logger = GeneralLogHandler()

        # Settaggio stile finestra
        self.setStyleSheet("""
            QSplashScreen {
                border-radius: 20px;
                background-color: black;
                color: white;
            }
        """)        

        # Barra di avanzamento
        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 430, 400, 20)
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid white;
                text-align: center;
                color: black;
                background-color: #e0e0e0;
            }
            QProgressBar::chunk {
                background-color: #2E7D32;
            }
        """)

        # Label della versione
        self.version_label = QLabel(Translator.tr("version_label").format(version=conf.APP_VERSION), self)
        self.version_label.setFont(QFont("Arial"))
        self.version_label.setStyleSheet("""
            color: black;
            font-size: 25px;                                                  
            """)
        self.version_label.adjustSize()
        self.version_label.move(175, 310)

        self.copyright_label = QLabel(Translator.tr("license_label"), self)
        self.copyright_label.setFont(QFont("Arial"))
        self.copyright_label.setStyleSheet("""
            color: black;
            font-size: 15px;                                                  
            """)
        self.copyright_label.adjustSize()
        self.copyright_label.move(250-int((self.copyright_label.width()/2)), 350)   

        self.status_label = QLabel(Translator.tr("splash_starting"), self)
        self.status_label.setStyleSheet("color: black; font-size: 12pt;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setGeometry(0, 400, self.width(), 20)  # Modifica Y per spostarlo su/giù   

        # Stile generale
        self.setStyleSheet("QSplashScreen { background-color: black; color: white; }")

        # Contatore avanzamento
        self.counter = 0

        self.init_steps = [
            (self.maybe_check_updates_step, self.maybe_check_online_version),
            (Translator.tr("splash_check_db"), self.check_or_create_user_config),
            (Translator.tr("splash_check_python"), self.check_python_version),
            (Translator.tr("splash_check_critical_libs"), self.check_critical_libraries),
            (Translator.tr("splash_check_base_project"), self.check_base_project_template),
            (Translator.tr("splash_check_working_folders"), self.check_working_folders),
            (Translator.tr("splash_check_community_folder"), self.check_community_folder),
            (Translator.tr("splash_start_completed"), lambda: None)
        ]
        self.current_step = 0

    def advance(self):
        self.counter += int(100 / len(self.init_steps))
        self.progress.setValue(min(self.counter, 100))

    def start_initialization(self, on_complete_callback):
        self.on_complete_callback = on_complete_callback
        QTimer.singleShot(500, self.perform_next_step)

    def perform_next_step(self):
        if self.current_step < len(self.init_steps):
            message, func = self.init_steps[self.current_step]
            self.status_label.setText(str(message()) if callable(message) else str(message))
            QApplication.processEvents()
            try:
                func()
            except Exception:
                self.logger.log_exception("Errore durante lo step di inizializzazione splash")
                self.status_label.setText(Translator.tr("splash_error_generic").format(error="Errore imprevisto"))
                QMessageBox.critical(None, Translator.tr("splash_init_error"), Translator.tr("splash_error_generic"))
                QTimer.singleShot(2000, QApplication.quit)
                return
            self.advance()
            self.current_step += 1
            QTimer.singleShot(500, self.perform_next_step)
        else:
            self.close()
            if self.on_complete_callback:
                self.on_complete_callback()

    def check_python_version(self):
        min_required = (3, 10)
        current = sys.version_info
        if current < min_required:
            raise Exception(f"Python >= {min_required[0]}.{min_required[1]} richiesto. Attuale: {current[0]}.{current[1]}")

    def check_base_project_template(self):
        template_path = "config/default_template.yaml"
        if not os.path.exists(template_path):
            self.logger.error(f"File base progetto mancante: {template_path}")
            raise Exception(f"File base progetto mancante: {template_path}")
        else:
            self.logger.debug(f"Template base presente: {template_path}")

    def check_working_folders(self):
        # Verifica che la cartella build esista nel percorso corretto
        if not DEFAULT_BUILD_DIR.exists():
            raise FileNotFoundError(f"La cartella di lavoro 'build' non è stata trovata: {DEFAULT_BUILD_DIR}")

        # Crea comunque le altre cartelle locali (non la build!)
        for folder in ["assets", "core", "config", "gui", "language"]:
            os.makedirs(folder, exist_ok=True)

    def check_online_version(self):
        try:
            req = urllib.request.Request(
                conf.GITHUB_URL,
                headers={
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache"
                }
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                latest = data.get("latest_version")
                changelog = data.get("changelog", "")
         
                # Ottieni lingua corrente attiva nel sistema Translator
                current_lang = Translator.get_current_language()
                changelog_text = changelog.get(current_lang, changelog.get("en", ""))

                if latest and latest != conf.APP_VERSION:
                    self.status_label.setText(Translator.tr("update_available"))

                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setWindowTitle(Translator.tr("update_available_title"))
                    msg.setText(
                        Translator.tr("update_available_text").format(
                            latest=latest, current=conf.APP_VERSION
                        )
                    )
                    msg.setInformativeText(
                        Translator.tr("update_changelog_prompt") + "\n\n" + changelog_text
                    )
                    msg.setStandardButtons(
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    msg.setDefaultButton(QMessageBox.StandardButton.Yes)

                    res = msg.exec()
                    if res == QMessageBox.StandardButton.Yes:
                        webbrowser.open(conf.RELEASE_URL)
                else:
                    self.status_label.setText(Translator.tr("version_up_to_date"))
        except Exception:
            self.status_label.setText(Translator.tr("version_check_failed"))                 

    def check_community_folder(self):
        community_path = conf.COMMUNITY_LOCAL_FOLDER
        os.makedirs(community_path, exist_ok=True)
        self.status_label.setText(f"Cartella community: {community_path}")

    def maybe_check_updates_step(self):
        return Translator.tr("splash_check_updates") if get_setting("check_updates") == "1" else Translator.tr("splash_disable_updates")

    def maybe_check_online_version(self):
        if get_setting("check_updates") != "1":
            return  # salta il controllo se disabilitato
        self.check_online_version()

    def check_critical_libraries(self):
        try:
            import PyQt6
            import ruamel.yaml
            import serial
            self.logger.debug("Librerie di base (PyQt6, ruamel.yaml, serial) importate correttamente.")
        except ImportError as e:
            self.logger.error(f"Libreria mancante: {e.name}")
            raise Exception(f"Libreria mancante: {e.name}. L'app non può avviarsi.")

        try:
            import esphome  # type: ignore
            self.logger.debug("Libreria esphome disponibile.")
        except ImportError:
            if shutil.which("esphome"):
                self.logger.debug("Modulo esphome non importabile, ma CLI rilevata nel PATH → OK")
                return  # ESPHome CLI sufficiente → termina qui
            else:
                self.status_label.setText("⚠️ " + Translator.tr("esphome_not_found_title"))
                try:
                    self.logger.warning("ESPHome non rilevato. Prompt per download mostrato all'utente.")
                    reply = QMessageBox.question(
                        self,
                        Translator.tr("esphome_not_found_title"),
                        Translator.tr("esphome_not_found_text"),
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        webbrowser.open("https://esphome.io/guides/installing_esphome.html")
                        self.logger.info("Aperta la pagina di download di ESPHome.")
                except Exception:
                    self.logger.log_exception("Errore durante il prompt per download ESPHome")

                self.logger.warning("Fine controllo ESPHome (non installato)")

    def check_or_create_user_config(self):
        """
        Verifica la presenza del file user_config.db in LOCALAPPDATA.
        Non crea né modifica nulla. Il setup deve fornirlo.
        """
        if os.path.exists(USER_DB_PATH):
            self.logger.debug(f"File user_config.db trovato in: {USER_DB_PATH}")
            self.status_label.setText("File user_config.db presente")
        else:
            self.logger.error("File user_config.db mancante. Avvio impossibile.")
            raise Exception("File user_config.db mancante. Reinstalla o ripara l'applicazione.")

