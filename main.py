# esphomeGuieasy - GUI editor for ESPHome
# Copyright (c) 2025 Juri
#
# Released under AGPLv3 - Non-commercial use only.
# See LICENSE file for details.

import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QDialog
from gui.main_window import MainWindow
from core.translator import Translator

# Se hai messo la dialog in gui/language_dialog.py:
from gui.language_dialog import LanguageDialog

CONFIG_PATH = "user_settings.json"

def load_user_settings():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_settings(settings):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f)

def main():
    app = QApplication(sys.argv)

    # 1. Carica settings utente (o crea nuovo)
    settings = load_user_settings()

    # 2. Se manca la lingua, chiedila subito all'utente con un dialog
    if "language" not in settings:
        available_langs = Translator.get_available_languages()
        dlg = LanguageDialog(available_langs)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected:
            settings["language"] = dlg.selected
            save_user_settings(settings)
        else:
            # Se l'utente chiude la dialog senza scegliere, default inglese
            settings["language"] = "en"
            save_user_settings(settings)

    # 3. Carica la lingua scelta
    Translator.load_language(settings.get("language", "en"))

    # 4. Avvia la MainWindow
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
