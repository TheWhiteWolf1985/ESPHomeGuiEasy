# -*- coding: utf-8 -*-
"""
@file splash_screen.py
@brief Manages the ESPHomeGUIeasy application startup splash screen.

Displays a GUI with loading bar, operation status,
verifies system requirements and required files (libraries, database, folders, etc.).

This module uses PyQt6 for the GUI and integrates a custom logger
to trace each initialization step. In case of blocking issues,
it halts the process and notifies the user of the error.

@author: ESPHomeGUIeasy Team
@version \ref PROJECT_NUMBER
@date: July 2025
@license: GNU Affero General Public License v3.0 (AGPLv3)
"""

import os, sys, traceback, json, webbrowser, shutil, sqlite3, platform, socket, urllib.request
import config.GUIconfig as conf
from pathlib import Path
from PyQt6.QtWidgets import QLabel, QProgressBar, QApplication, QMessageBox, QSplashScreen
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer, QSize
from importlib.metadata import version, PackageNotFoundError
from core.translator import Translator
from core.settings_db import init_db, get_setting, set_setting, get_user_db_path
from config.GUIconfig import USER_DB_PATH, DEFAULT_BUILD_DIR
from core.log_handler import GeneralLogHandler

class SplashScreen(QSplashScreen):
    """
Initializes the startup splash screen (SplashScreen) with a scaled image, 
custom style, progress bar, informational labels and initialization steps.

@param pixmap: QPixmap to be used as the splash screen background image.
"""
    def __init__(self, pixmap):
        scaled_pixmap = pixmap.scaled(QSize(500, 500), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        super().__init__(scaled_pixmap)
        self.setFixedSize(500, 500) # Sets a fixed size for the splash window (square, 500x500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFont(QFont("Arial", 10))

        # Initializes the logger to track splash screen status
        self.logger = GeneralLogHandler()

        # Sets window style
        self.setStyleSheet("""
            QSplashScreen {
                border-radius: 20px;
                background-color: black;
                color: white;
            }
        """)        

        # Progress bar
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

        # Version label
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
        self.status_label.setGeometry(0, 400, self.width(), 20)  

        # Global style
        self.setStyleSheet("QSplashScreen { background-color: black; color: white; }")

        # Progress counter
        self.counter = 0

        # Defines the sequential steps for initialization procedure
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
        """
        Advances the splash screen progress bar based on the number of steps. 
        Also updates the log with the current progress value.
        """
        self.counter += int(100 / len(self.init_steps)) # Computes percentage increment based on total steps
        self.progress.setValue(min(self.counter, 100))
        self.logger.debug(f"Avanzamento barra splash al {self.counter}%")

    def start_initialization(self, on_complete_callback):
        """
        Starts the splash screen initialization sequence, including OS detection
        and saving the information to the database. The procedure is asynchronous and ends with a callback.

        @param on_complete_callback: Function to be called upon completion of the initialization.
        """
        self.logger.info("Avvio sequenza inizializzazione splash screen.")

        # Rilevamento dettagli OS
        os_platform = platform.system()     # Detects and logs operating system information
        os_version = platform.version()
        os_release = platform.release()

        # Log nel file
        self.logger.info(f"Sistema operativo rilevato: {os_platform} {os_release} (build: {os_version})")

        # Salvataggio nel DB
        set_setting("os_platform", os_platform)
        set_setting("os_version", os_version)
        set_setting("os_build", os_release)

        self.on_complete_callback = on_complete_callback
        QTimer.singleShot(500, self.perform_next_step)

    def perform_next_step(self):
        """
        Performs the next step of the initialization sequence. 
        Updates the visual status, handles blocking errors and calls the final callback on completion.
        """
        self.logger.debug(f"Esecuzione step splash n. {self.current_step + 1} / {len(self.init_steps)}")
        if self.current_step < len(self.init_steps):     # If more steps are present, execute the next one
            message, func = self.init_steps[self.current_step]
            self.status_label.setText(str(message()) if callable(message) else str(message))
            QApplication.processEvents()
            try:
                func()
                self.logger.debug(f"Step {self.current_step + 1} completato con successo.")
            except Exception:
                err_msg = traceback.format_exc()
                self.logger.log_exception("Errore durante lo step di inizializzazione splash")
                self.logger.error(f"Errore bloccante nello step n. {self.current_step + 1}")
                self.status_label.setText("❌ " + Translator.tr("splash_error_generic"))
                QMessageBox.critical(self, Translator.tr("splash_init_error"), f"{Translator.tr('splash_error_generic')}\n\n{err_msg}")     # Executes the current step and handles any exceptions
                QTimer.singleShot(2000, QApplication.quit)
                return
            self.advance()
            self.current_step += 1
            QTimer.singleShot(500, self.perform_next_step)     # Starts the first step of the sequence after a short delay
        else:
            self.close()     # All steps completed: closes splash and calls the completion function
            if self.on_complete_callback:
                self.on_complete_callback()

    def check_python_version(self):
        """
        Verifies that the running Python version is compatible with the application.
        Requires at least Python 3.10. Otherwise, it raises a blocking exception.
        """
        self.logger.info("Avvio controllo versione Python...")
        min_required = (3, 10)     # Minimum required Python version for the application
        current = sys.version_info

        if current < min_required:
            self.logger.error(f"Versione Python non compatibile: {current[0]}.{current[1]}. Minimo richiesto: {min_required[0]}.{min_required[1]}")
            raise Exception(f"Python >= {min_required[0]}.{min_required[1]} richiesto. Attuale: {current[0]}.{current[1]}")
        
        self.logger.info(f"Versione Python valida: {current[0]}.{current[1]}")

    def check_base_project_template(self):
        """
        Checks for the presence of the base project YAML file in the config/ directory.
        If the file does not exist, a blocking exception is raised.
        """
        self.logger.info("Avvio controllo file template di progetto base...")

        template_path = conf.TEMPLATE_PROJECT_PATH      # Path to base project YAML template
        if not os.path.exists(template_path):     # Checks if the file exists at the expected location
            self.logger.error(f"File base progetto mancante: {template_path}")
            raise Exception(f"File base progetto mancante: {template_path}")
        else:
            self.logger.info(f"Template base presente: {template_path}")
            self.logger.info("Controllo file template di progetto completato con successo.")


    def check_working_folders(self):
        """
        Verifies the existence of the essential working folders for the application.
        Checks that the build directory exists and creates the other standard folders if necessary.
        Raises an exception if the build directory is missing.
        """
        self.logger.info("Avvio controllo cartelle di lavoro...")

        try:
            # Checks if the build folder exists in the correct path
            if not DEFAULT_BUILD_DIR.exists():     # Build folder is essential and not created automatically
                self.logger.error(f"La cartella di lavoro 'build' non è stata trovata: {DEFAULT_BUILD_DIR}")
                raise FileNotFoundError(f"La cartella di lavoro 'build' non è stata trovata: {DEFAULT_BUILD_DIR}")

            for folder in ["assets", "core", "config", "gui", "language"]:     # Creates standard application folders if missing
                os.makedirs(folder, exist_ok=True)
                self.logger.debug(f"Cartella verificata o creata: {folder}")

            self.logger.info("Controllo cartelle di lavoro completato con successo.")

        except Exception as e:
            self.logger.log_exception("Errore durante la verifica delle cartelle di lavoro")
            raise


    def check_online_version(self):
        """
        Checks whether a newer version of the app is available on GitHub.
        If available, displays a message with changelog and link to the release page.
        Check is only performed if an internet connection is available.
        """
        self.logger.info("Avvio controllo aggiornamenti da GitHub...")

        # Verifica connessione Internet
        def is_online():     # Checks if an internet connection is available
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=2)
                return True
            except OSError:
                return False

        if not is_online():
            self.logger.warning("Connessione Internet non disponibile. Salto controllo aggiornamenti.")
            self.status_label.setText(Translator.tr("version_check_failed"))
            return

        try:
            req = urllib.request.Request(     # HTTP request to fetch update data from GitHub
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

                current_lang = Translator.get_current_language()
                changelog_text = changelog.get(current_lang, changelog.get("en", ""))

                if latest and latest != conf.APP_VERSION:     # If remote version is newer, display update dialog
                    self.logger.info(f"Nuova versione disponibile: {latest} (attuale: {conf.APP_VERSION})")
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
                        self.logger.info("Pagina GitHub delle release aperta su richiesta dell’utente.")
                else:
                    self.status_label.setText(Translator.tr("version_up_to_date"))
                    self.logger.info("Versione del programma aggiornata.")
            
            self.logger.info("Controllo aggiornamenti completato con successo.")

        except Exception:
            self.status_label.setText(Translator.tr("version_check_failed"))
            self.logger.log_exception("Errore durante il controllo aggiornamenti GitHub")
            raise

    def check_community_folder(self):
        """
        Verifies the existence of the local community projects folder. 
        Creates it if it doesn't exist. Shows the path in the status label.
        """
        self.logger.info("Avvio controllo cartella community...")

        try:
            community_path = conf.COMMUNITY_LOCAL_FOLDER     # Path to the folder used for shared community projects
            os.makedirs(community_path, exist_ok=True)
            self.logger.info(f"Cartella community verificata o creata: {community_path}")
            self.status_label.setText(f"Cartella community: {community_path}")
            self.logger.info("Controllo cartella community completato con successo.")
        except Exception:
            self.logger.log_exception("Errore durante il controllo o la creazione della cartella community")
            raise


    def maybe_check_updates_step(self):
        """
        Returns the message to display in the splash screen for the update check.
        If the feature is disabled, returns an appropriate message.
        
        @return: Translated string with the status of the update check.
        """
        return Translator.tr("splash_check_updates") if get_setting("check_updates") == "1" else Translator.tr("splash_disable_updates")

    def maybe_check_online_version(self):
        """
        Performs the update check only if the option is enabled in the database.
        Otherwise, the function is skipped with no effect.
        """
        if get_setting("check_updates") != "1":     # Checks if update checking is enabled before proceeding
            return  # salta il controllo se disabilitato
        self.check_online_version()

    def check_critical_libraries(self):
        """
        Checks for the presence of core libraries required by the application.

        Verifica se sono presenti:
        - PyQt6
        - ruamel.yaml
        - serial
        - esphome (modulo o CLI)

        If a library is missing, an exception is raised.
        If the esphome module is not importable but the CLI is available (PATH, custom or fallback), it is considered valid.
        """
        self.logger.info("Avvio controllo librerie critiche...")
        try:
            # Checks availability of core Python libraries for GUI and YAML parsing
            import PyQt6     
            import ruamel.yaml
            import serial
            self.logger.debug("Librerie di base (PyQt6, ruamel.yaml, serial) importate correttamente.")
            self.logger.info("Librerie di base importate correttamente.")
        except ImportError as e:
            self.logger.error(f"Libreria mancante: {e.name}")
            raise Exception(f"Libreria mancante: {e.name}. L'app non può avviarsi.")

        try:
            import esphome  # type: ignore     # Tries to import esphome as a module (optional)
            self.logger.debug("Libreria esphome disponibile.")
        except ImportError:
            self.logger.warning("Modulo esphome non importabile. Verifica della CLI in corso...")
            if shutil.which("esphome"):     # If the module is unavailable, checks if CLI is in PATH
                self.logger.info("ESPHome CLI trovata nel PATH.")
                self.logger.debug("Modulo esphome non importabile, ma CLI rilevata nel PATH → OK")
                return  # ESPHome CLI sufficiente → termina qui
            
            custom_path = get_setting("custom_esphome_path")     # Checks if the user has configured a custom path for the CLI
            if custom_path and Path(custom_path).exists():
                self.logger.info(f"ESPHome CLI trovato nel percorso personalizzato: {custom_path}")
                return

            # Common fallback paths on Windows systems for ESPHome CLI
            known_paths = [
                Path.home() / ".esphome" / "esphome_venv" / "Scripts" / "esphome.exe",
                Path("C:/Program Files/ESPHome/esphome.exe"),
                Path("C:/Tools/esphome/esphome.exe")
            ]

            for path in known_paths:
                if path.exists():
                    self.logger.info(f"ESPHome CLI trovata nel percorso fallback: {path}")
                    return

            else:
                self.status_label.setText("⚠️ " + Translator.tr("esphome_not_found_title"))
                try:
                    self.logger.warning("ESPHome non rilevato. Prompt per download mostrato all'utente.")
                    # If all checks fail, prompts user to open the installation page
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

                raise Exception("ESPHome non installato e CLI non trovata.")

    def check_or_create_user_config(self):
        """
        Checks for the presence of the user_config.db file in the %LOCALAPPDATA% folder.

        The file is essential for the application's functionality. 
        It is not created automatically: it must be provided by setup or restored.

        @raises Exception: If the file is missing, the application cannot start.
        """
        self.logger.info("Avvio controllo file user_config.db...")

        if os.path.exists(USER_DB_PATH):
            self.logger.info(f"File user_config.db trovato in: {USER_DB_PATH}")
            self.status_label.setText("File user_config.db presente")
            self.logger.info("Controllo user_config.db completato con successo.")
        else:
            self.logger.error("File user_config.db mancante. Avvio impossibile.")
            raise Exception("File user_config.db mancante. Reinstalla o ripara l'applicazione.")


