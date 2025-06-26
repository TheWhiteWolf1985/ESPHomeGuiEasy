from core.settings_db import set_setting
from PyQt6.QtWidgets import QApplication
from core.settings_db import set_setting
from core.translator import Translator

def save_settings(dialog):
    # --- LANGUAGE ---
    lang_map = {
        "English": "en",
        "Italiano": "it",
        "Español": "es",
        "Deutsch": "de",
        "Brasileiro": "br",
        "Português": "pt"
    }

    selected_lang = dialog.language_combo.currentText()
    lang_code = lang_map.get(selected_lang, "en")
    set_setting("language", lang_code)

    # Applica subito la lingua nella sessione corrente
    Translator.load_language(lang_code)
    if hasattr(dialog, "aggiorna_tutte_le_label"):
        dialog.aggiorna_tutte_le_label()

    # Prova ad aggiornare l'interfaccia se disponibile
    parent = dialog.parent()
    if parent and hasattr(parent, "aggiorna_tutte_le_label"):
        parent.aggiorna_tutte_le_label()
    else:
        # Fallback: forza aggiornamento delle traduzioni via evento globale
        for widget in QApplication.instance().allWidgets():
            if hasattr(widget, "aggiorna_tutte_le_label"):
                widget.aggiorna_tutte_le_label()

    # --- PROJECT PATH ---
    project_path = dialog.project_path_edit.text().strip()
    if project_path:
        set_setting("default_project_path", project_path)

    # --- SPLASH SCREEN ---
    splash_enabled = dialog.splash_checkbox.isChecked()
    set_setting("show_splash", "1" if splash_enabled else "0")

    # --- CHECK AGGIORNAMENTI ---
    check_updates = dialog.update_checkbox.isChecked()
    set_setting("check_updates", "1" if check_updates else "0")




