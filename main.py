# -*- coding: utf-8 -*-
"""
@file main.py
@brief Entry point of the ESPHomeGUIeasy application.

@mainpage ESPHomeGUIeasy
@defgroup core_entry Entry Point
@ingroup main
@brief Application launcher, global initializer and exception handler.

This file initializes the ESPHomeGUIeasy environment. It sets up the QApplication,
loads the selected language (or prompts for it if not yet defined), handles
global exception logging, manages the splash screen visibility logic, and finally
launches the main user interface.

Key responsibilities:
- Loads application settings from the SQLite database
- Displays a language selection dialog on first run
- Initializes the splash screen (if enabled)
- Ensures proper logging of uncaught exceptions
- Launches the main application window (`MainWindow`)

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

import sys, os, traceback
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
sys.path.insert(0, os.path.dirname(__file__))
from gui.main_window import MainWindow
from core.translator import Translator
from gui.language_selection_dialog import LanguageSelectionDialog
from gui.splash_screen import SplashScreen
from config.GUIconfig import conf, GlobalPaths
from core.settings_db import init_db, get_setting, set_setting
from core.log_handler import GeneralLogHandler

def global_exception_hook(exc_type, exc_value, exc_traceback):
    logger = GeneralLogHandler()
    logger.error(f"UNCAUGHT EXCEPTION: {exc_type.__name__}: {exc_value}")
    logger.error("Traceback:\n" + "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))


sys.excepthook = global_exception_hook

logger = GeneralLogHandler()

# Log iniziale
logger.info("Avvio main.py")

def should_show_splash() -> bool:
    """
    @brief Determines whether the splash screen should be displayed.

    Reads the `show_splash` setting from the SQLite configuration database.
    If not previously set, defaults to True and creates the entry.

    @return True if the splash screen should be shown, False otherwise.
    """
    splash_setting = get_setting("show_splash")
    if splash_setting is None:
        set_setting("show_splash", "1")
        return True
    return splash_setting == "1"

def show_main_window():
    logger.info("=== CHIAMATA CALLBACK show_main_window() ===")
    app = QApplication.instance()
    if app is None:
        logger.error("QApplication.instance() restituisce None!")
    else:
        try:
            app.main_window = MainWindow()
            app.main_window.show()
            logger.info("Main window creata e mostrata!")
        except Exception as e:
            logger.error(f"Eccezione durante la creazione della MainWindow: {e}")
            logger.error(traceback.format_exc())

def main():
    """
    @brief Main application entry point.

    This function performs all critical startup tasks in the correct order:

    1. Initializes the `QApplication` instance required for the GUI.
    2. Initializes the configuration database via `init_db()`.
    3. Loads the current language settings or displays a language selection dialog if undefined.
    4. Depending on configuration, displays the splash screen (`SplashScreen`) or skips it.
    5. Starts the Qt event loop.

    If any unexpected error occurs, the `GeneralLogHandler` records the exception to disk.

    @throws Any unhandled exceptions will be logged and re-raised.
    """    
    try:
        app = QApplication(sys.argv)

        # Inizializza il database
        init_db()

        # Carica la lingua solo se già selezionata
        lang = Translator.get_current_language()
        if lang:
            Translator.load_language(lang)

        # Controllo lingua
        language = get_setting("language")
        logger.debug(f"Lingua trovata nel DB: {language}")
        if not language or not language.strip():
            logger.debug("[DEBUG] Creo LanguageSelectionDialog")
            dlg = LanguageSelectionDialog()
            dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
            dlg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            dlg.resize(400, 400)

            logger.debug("[DEBUG] Apro exec() sul dialog")
            result = dlg.exec()
            logger.debug(f"[DEBUG] Risultato exec: {result}")

            if result == QDialog.DialogCode.Accepted and dlg.get_selected_language():
                language = dlg.get_selected_language()
                logger.debug(f"[DEBUG] Lingua selezionata: {language}")
                set_setting("language", language)
                Translator.load_language(language.strip().lower())
            else:
                logger.warning(Translator.tr("language_not_selected"))
                logger.debug("[DEBUG] Lingua non selezionata, esco.")
                return

        # A questo punto siamo sicuri che la lingua è impostata
        logger.info(f"Lingua attiva: {language}")

        # Mostra splash SOLO dopo selezione lingua
        if should_show_splash():
            logger.info("Caricamento splash screen")
            pixmap = QPixmap(GlobalPaths.SPLASH_IMAGE)
            splash = SplashScreen(pixmap)
            splash.show()
            splash.start_initialization(on_complete_callback=show_main_window)
        else:
            show_main_window()

        sys.exit(app.exec())

    except Exception:
        GeneralLogHandler().log_exception("Errore imprevisto in main()")
        raise

if __name__ == "__main__":
    """
    @brief Standard Python entry-point for standalone execution.

    This ensures the main application logic is executed only when the file is run
    directly (and not imported as a module).
    """    
    main()
