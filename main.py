# esphomeGuieasy - GUI editor for ESPHome
# Copyright (c) 2025 Juri
# Released under AGPLv3 - Non-commercial use only.
# See LICENSE file for details.

import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtGui import QPixmap
from gui.main_window import MainWindow
from core.translator import Translator
from gui.language_selection_dialog import LanguageSelectionDialog
from gui.splash_screen import SplashScreen
import config.GUIconfig as conf
from core.settings_db import init_db, get_setting, set_setting

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
    app = QApplication(sys.argv)

    # Inizializza database delle impostazioni
    init_db()

    # Se la lingua non è ancora impostata, mostra il dialog
    language = get_setting("language")
    if not language:
        dlg = LanguageSelectionDialog()
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.get_selected_language():
            set_setting("language", dlg.get_selected_language())
        else:
            set_setting("language", "en")

    # Carica la lingua da DB
    language = get_setting("language")

    print("Python path:", sys.executable)
    # Carica traduzioni
    Translator.load_language(get_setting("language") or "en")

    # Splash attivo solo se DEBUG è False
    if should_show_splash():
        pixmap = QPixmap(conf.SPLASH_IMAGE)
        splash = SplashScreen(pixmap)
        splash.show()
        splash.start_initialization(on_complete_callback=show_main_window)
    else:
        show_main_window()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
