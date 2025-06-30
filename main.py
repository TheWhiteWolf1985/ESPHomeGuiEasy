# esphomeGuieasy - GUI editor for ESPHome
# Copyright (c) 2025 Juri
# Released under AGPLv3 - Non-commercial use only.
# See LICENSE file for details.

import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
sys.path.insert(0, os.path.dirname(__file__))
from gui.main_window import MainWindow
from core.translator import Translator
from gui.language_selection_dialog import LanguageSelectionDialog
from gui.splash_screen import SplashScreen
import config.GUIconfig as conf
from core.settings_db import init_db, get_setting, set_setting
from core.log_handler import GeneralLogHandler
import logging
import tempfile

logger = GeneralLogHandler()

# Log iniziale
logger.info("Avvio main.py")

def should_show_splash() -> bool:
    """
    Restituisce True se lo splash screen deve essere mostrato.
    Se la chiave non è ancora presente nel database, imposta il valore predefinito a '1'.
    """
    splash_setting = get_setting("show_splash")
    if splash_setting is None:
        set_setting("show_splash", "1")
        return True
    return splash_setting == "1"

def show_main_window():
    window = MainWindow()
    window.show()

def main():
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
        print(language)
        if not language or not language.strip():
            logger.debug("[DEBUG] Creo LanguageSelectionDialog")
            dlg = LanguageSelectionDialog()
            dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
            dlg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            dlg.resize(400, 400)
            dlg.show()

            logger.debug("[DEBUG] Apro exec() sul dialog")
            result = dlg.exec()
            logger.debug(f"[DEBUG] Risultato exec: {result}")

            if result == QDialog.DialogCode.Accepted and dlg.get_selected_language():
                language = dlg.get_selected_language()
                logger.debug(f"[DEBUG] Lingua selezionata: {language}")
                set_setting("language", language)
                Translator.load_language(language.strip().lower())
            else:
                logger.warning("Lingua non selezionata. Chiusura applicazione.")
                logger.debug("[DEBUG] Lingua non selezionata, esco.")
                return

        # A questo punto siamo sicuri che la lingua è impostata
        logger.info(f"Lingua attiva: {language}")

        # Mostra splash SOLO dopo selezione lingua
        if should_show_splash():
            logger.info("Caricamento splash screen")
            pixmap = QPixmap(conf.SPLASH_IMAGE)
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
    main()
