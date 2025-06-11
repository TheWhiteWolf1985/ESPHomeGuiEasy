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
from gui.language_dialog import LanguageDialog
from gui.splash_screen import SplashScreen
import config.GUIconfig as conf

def load_user_settings():
    if os.path.exists(conf.CONFIG_PATH):
        with open(conf.CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_settings(settings):
    with open(conf.CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f)

def show_main_window():
    window = MainWindow()
    window.show()

def main():
    app = QApplication(sys.argv)

    # Carica o crea impostazioni utente
    settings = load_user_settings()

    # Dialog lingua se non specificata
    if "language" not in settings:
        available_langs = Translator.get_available_languages()
        dlg = LanguageDialog(available_langs)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected:
            settings["language"] = dlg.selected
            save_user_settings(settings)
        else:
            settings["language"] = "en"
            save_user_settings(settings)

    # Carica traduzioni
    Translator.load_language(settings.get("language", "en"))

    # Splash attivo solo se DEBUG è False
    if not conf.DEBUG:
        pixmap = QPixmap(conf.SPLASH_IMAGE)  # Sostituisci con percorso reale
        splash = SplashScreen(pixmap)
        splash.show()
        splash.start_initialization(on_complete_callback=show_main_window)
    else:
        show_main_window()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
