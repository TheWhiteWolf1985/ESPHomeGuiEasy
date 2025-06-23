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
from core.settings_db import init_db, get_setting, set_setting


class SplashScreen(QSplashScreen):
    def __init__(self, pixmap):
        scaled_pixmap = pixmap.scaled(QSize(500, 500), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        super().__init__(scaled_pixmap)
        self.setFixedSize(500, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFont(QFont("Arial", 10))

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
            (Translator.tr("splash_check_python"), self.check_python_version),
            (Translator.tr("splash_check_requirements"), self.check_requirements_file),
            (Translator.tr("splash_check_dependencies"), self.check_required_libraries),
            (Translator.tr("splash_check_user_settings"), self.check_user_settings),
            (Translator.tr("splash_check_base_project"), self.check_base_project_template),
            (Translator.tr("splash_check_working_folders"), self.check_working_folders),
            ("Controllo cartella progetti community...", self.check_community_folder),
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
            except Exception as e:
                self.status_label.setText(Translator.tr("splash_error_generic").format(error=str(e)))
                QMessageBox.critical(None, Translator.tr("splash_init_error"), str(e))
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

    def check_requirements_file(self):
        if not os.path.exists("requirements.txt"):
            raise Exception("File requirements.txt non trovato.")

    def check_required_libraries(self):
        with open("requirements.txt", "r", encoding="utf-8") as f:
            libs = [
                line.strip().split("==")[0].split(">=")[0].split("<=")[0]
                for line in f if line.strip() and not line.startswith("#")
            ]
        missing = []
        for lib in libs:
            try:
                _ = version(lib)
            except PackageNotFoundError:
                missing.append(lib)
        if missing:
            raise Exception("Dipendenze mancanti:\n" + "\n".join(missing))

    def check_user_settings(self):
        init_db()
        if not get_setting("language"):
            set_setting("language", "en")
            self.status_label.setText("Impostazione lingua creata: 'en'")
        else:
            self.status_label.setText("Lingua già impostata")


    def check_base_project_template(self):
        if not os.path.exists("config/default_template.yaml"):
            raise Exception("File base progetto mancante: config/default_template.yaml")

    def check_working_folders(self):
        for folder in ["assets", "build", "core", "config", "gui", "language"]:
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
        return Translator.tr("splash_check_updates") if get_setting("check_updates") == "1" else "Aggiornamenti disabilitati"

    def maybe_check_online_version(self):
        if get_setting("check_updates") != "1":
            return  # salta il controllo se disabilitato
        self.check_online_version()
