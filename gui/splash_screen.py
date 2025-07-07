# -*- coding: utf-8 -*-
"""
@file splash_screen.py
@brief Gestisce la schermata iniziale (Splash Screen) dell'app ESPHomeGUIeasy.

Visualizza un'interfaccia grafica con barra di caricamento, stato operazioni,
verifica requisiti minimi e file essenziali (librerie, database, cartelle, ecc.).

Il modulo utilizza PyQt6 per la GUI e integra un logger personalizzato
per tracciare ogni fase dell'avvio. In caso di problemi bloccanti,
interrompe il caricamento e segnala l'errore all'utente.

@author: ESPHomeGUIeasy Team
@version \ref PROJECT_NUMBER
@date: Luglio 2025
@license: AGPLv3 License
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
Inizializza la schermata di avvio (SplashScreen) con un'immagine scalata, 
stile personalizzato, barra di avanzamento, etichette informative e passaggi di inizializzazione.

@param pixmap: QPixmap dell'immagine da usare come sfondo dello splash screen.
"""
    def __init__(self, pixmap):
        scaled_pixmap = pixmap.scaled(QSize(500, 500), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        super().__init__(scaled_pixmap)
        self.setFixedSize(500, 500) # Imposta dimensione fissa della finestra splash (quadrata, 500x500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFont(QFont("Arial", 10))

        # Inizializza gestore log per tracciare lo stato dello splash screen
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

        # Definisce i passaggi sequenziali per la procedura di avvio
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
        Avanza la barra di progresso dello splash screen in base al numero di step previsti. 
        Aggiorna anche il log con il valore corrente della barra.
        """
        self.counter += int(100 / len(self.init_steps)) # Calcola incremento percentuale in base al numero totale di step
        self.progress.setValue(min(self.counter, 100))
        self.logger.debug(f"Avanzamento barra splash al {self.counter}%")

    def start_initialization(self, on_complete_callback):
        """
        Avvia la sequenza di inizializzazione dello splash screen, compreso il rilevamento del sistema operativo
        e il salvataggio delle informazioni nel database. La procedura è asincrona e termina con una callback.

        @param on_complete_callback: Funzione da chiamare al termine dell'inizializzazione.
        """
        self.logger.info("Avvio sequenza inizializzazione splash screen.")

        # Rilevamento dettagli OS
        os_platform = platform.system()     # Rileva e registra le informazioni sul sistema operativo
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
        Esegue il passaggio successivo della sequenza di inizializzazione. 
        Aggiorna lo stato visivo, gestisce gli errori bloccanti e chiama la callback finale al termine.
        """
        self.logger.debug(f"Esecuzione step splash n. {self.current_step + 1} / {len(self.init_steps)}")
        if self.current_step < len(self.init_steps):     # Se sono presenti altri step, esegue il prossimo nella lista
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
                QMessageBox.critical(self, Translator.tr("splash_init_error"), f"{Translator.tr('splash_error_generic')}\n\n{err_msg}")     # Esegue lo step corrente e gestisce eventuali eccezioni
                QTimer.singleShot(2000, QApplication.quit)
                return
            self.advance()
            self.current_step += 1
            QTimer.singleShot(500, self.perform_next_step)     # Avvia il primo step della sequenza dopo un breve ritardo
        else:
            self.close()     # Tutti gli step completati: chiude lo splash e chiama la funzione di completamento
            if self.on_complete_callback:
                self.on_complete_callback()

    def check_python_version(self):
        """
        Verifica che la versione di Python in esecuzione sia compatibile con l'applicazione.
        Richiede almeno Python 3.10. In caso contrario, solleva un'eccezione bloccante.
        """
        self.logger.info("Avvio controllo versione Python...")
        min_required = (3, 10)     # Versione minima di Python richiesta dall'applicazione
        current = sys.version_info

        if current < min_required:
            self.logger.error(f"Versione Python non compatibile: {current[0]}.{current[1]}. Minimo richiesto: {min_required[0]}.{min_required[1]}")
            raise Exception(f"Python >= {min_required[0]}.{min_required[1]} richiesto. Attuale: {current[0]}.{current[1]}")
        
        self.logger.info(f"Versione Python valida: {current[0]}.{current[1]}")

    def check_base_project_template(self):
        """
        Controlla la presenza del file YAML di progetto base nella directory config/.
        Se il file non esiste, solleva un'eccezione bloccante.
        """
        self.logger.info("Avvio controllo file template di progetto base...")

        template_path = conf.TEMPLATE_PROJECT_PATH      # Percorso del file template YAML di progetto base
        if not os.path.exists(template_path):     # Verifica se il file è presente nel percorso previsto
            self.logger.error(f"File base progetto mancante: {template_path}")
            raise Exception(f"File base progetto mancante: {template_path}")
        else:
            self.logger.info(f"Template base presente: {template_path}")
            self.logger.info("Controllo file template di progetto completato con successo.")


    def check_working_folders(self):
        """
        Verifica l'esistenza delle cartelle di lavoro essenziali per l'applicazione.
        Controlla che la directory di build esista e crea, se necessario, le altre cartelle standard.
        Solleva eccezione se la cartella di build è assente.
        """
        self.logger.info("Avvio controllo cartelle di lavoro...")

        try:
            # Verifica che la cartella build esista nel percorso corretto
            if not DEFAULT_BUILD_DIR.exists():     # La cartella di build è essenziale e non viene creata automaticamente
                self.logger.error(f"La cartella di lavoro 'build' non è stata trovata: {DEFAULT_BUILD_DIR}")
                raise FileNotFoundError(f"La cartella di lavoro 'build' non è stata trovata: {DEFAULT_BUILD_DIR}")

            for folder in ["assets", "core", "config", "gui", "language"]:     # Crea le altre cartelle standard dell'applicazione se non presenti
                os.makedirs(folder, exist_ok=True)
                self.logger.debug(f"Cartella verificata o creata: {folder}")

            self.logger.info("Controllo cartelle di lavoro completato con successo.")

        except Exception as e:
            self.logger.log_exception("Errore durante la verifica delle cartelle di lavoro")
            raise


    def check_online_version(self):
        """
        Controlla se è disponibile una versione più recente dell'app su GitHub.
        Se disponibile, mostra un messaggio all'utente con changelog e link alla pagina delle release.
        Il controllo viene eseguito solo se la connessione è disponibile.
        """
        self.logger.info("Avvio controllo aggiornamenti da GitHub...")

        # Verifica connessione Internet
        def is_online():     # Verifica se è disponibile una connessione a Internet
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
            req = urllib.request.Request(     # Richiesta HTTP per ottenere dati aggiornamento da GitHub
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

                if latest and latest != conf.APP_VERSION:     # Se la versione remota è più recente, mostra dialogo di aggiornamento
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
        Verifica l'esistenza della cartella locale dei progetti community. 
        Se non esiste, la crea. Mostra il percorso nella label di stato.
        """
        self.logger.info("Avvio controllo cartella community...")

        try:
            community_path = conf.COMMUNITY_LOCAL_FOLDER     # Percorso della cartella usata per progetti condivisi dalla community
            os.makedirs(community_path, exist_ok=True)
            self.logger.info(f"Cartella community verificata o creata: {community_path}")
            self.status_label.setText(f"Cartella community: {community_path}")
            self.logger.info("Controllo cartella community completato con successo.")
        except Exception:
            self.logger.log_exception("Errore durante il controllo o la creazione della cartella community")
            raise


    def maybe_check_updates_step(self):
        """
        Restituisce il messaggio da mostrare nello splash screen relativo al controllo aggiornamenti.
        Se la funzione è disabilitata, restituisce un messaggio appropriato.
        
        @return: Stringa tradotta con lo stato del controllo aggiornamenti.
        """
        return Translator.tr("splash_check_updates") if get_setting("check_updates") == "1" else Translator.tr("splash_disable_updates")

    def maybe_check_online_version(self):
        """
        Esegue il controllo aggiornamenti solo se l'opzione è abilitata nel database.
        In caso contrario, la funzione viene ignorata senza effetto.
        """
        if get_setting("check_updates") != "1":     # Controlla se il controllo aggiornamenti è attivo prima di procedere
            return  # salta il controllo se disabilitato
        self.check_online_version()

    def check_critical_libraries(self):
        """
        Controlla la presenza delle librerie fondamentali per il funzionamento del programma.

        Verifica se sono presenti:
        - PyQt6
        - ruamel.yaml
        - serial
        - esphome (modulo o CLI)

        Se una libreria è mancante, solleva un'eccezione.
        Se il modulo esphome non è importabile ma la CLI è disponibile (PATH, percorso personalizzato o fallback), viene comunque considerato valido.
        """
        self.logger.info("Avvio controllo librerie critiche...")
        try:
            # Verifica disponibilità delle librerie Python fondamentali per la GUI e il parsing YAML
            import PyQt6     
            import ruamel.yaml
            import serial
            self.logger.debug("Librerie di base (PyQt6, ruamel.yaml, serial) importate correttamente.")
            self.logger.info("Librerie di base importate correttamente.")
        except ImportError as e:
            self.logger.error(f"Libreria mancante: {e.name}")
            raise Exception(f"Libreria mancante: {e.name}. L'app non può avviarsi.")

        try:
            import esphome  # type: ignore     # Prova a importare esphome come modulo (opzionale)
            self.logger.debug("Libreria esphome disponibile.")
        except ImportError:
            self.logger.warning("Modulo esphome non importabile. Verifica della CLI in corso...")
            if shutil.which("esphome"):     # Se il modulo non è disponibile, controlla se la CLI è nel PATH
                self.logger.info("ESPHome CLI trovata nel PATH.")
                self.logger.debug("Modulo esphome non importabile, ma CLI rilevata nel PATH → OK")
                return  # ESPHome CLI sufficiente → termina qui
            
            custom_path = get_setting("custom_esphome_path")     # Controlla se l'utente ha configurato un percorso personalizzato alla CLI
            if custom_path and Path(custom_path).exists():
                self.logger.info(f"ESPHome CLI trovato nel percorso personalizzato: {custom_path}")
                return

            # Percorsi di fallback comuni su sistemi Windows per la CLI di ESPHome
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
                    # Se tutto fallisce, chiede all'utente se vuole aprire la pagina di installazione
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
        Controlla la presenza del file user_config.db nella cartella %LOCALAPPDATA%.

        Il file è essenziale per il funzionamento dell'app. 
        Non viene creato automaticamente: deve essere presente, installato o ripristinato tramite setup.

        @raises Exception: Se il file è assente, l'applicazione non può essere avviata.
        """
        self.logger.info("Avvio controllo file user_config.db...")

        if os.path.exists(USER_DB_PATH):
            self.logger.info(f"File user_config.db trovato in: {USER_DB_PATH}")
            self.status_label.setText("File user_config.db presente")
            self.logger.info("Controllo user_config.db completato con successo.")
        else:
            self.logger.error("File user_config.db mancante. Avvio impossibile.")
            raise Exception("File user_config.db mancante. Reinstalla o ripara l'applicazione.")


