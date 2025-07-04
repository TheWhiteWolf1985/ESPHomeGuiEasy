import os
import json
from core.settings_db import get_setting
from core.log_handler import GeneralLogHandler

class Translator:
    _translations = {}
    _fallback = {}
    _lang_code = "en"
    _language_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../Language")

    @classmethod
    def load_language(cls, lang_code):
        """
        Carica il file di traduzione richiesto e l’inglese come fallback.
        """
        cls._lang_code = lang_code
        # Fallback inglese (sempre caricato)
        with open(os.path.join(cls._language_dir, "en.json"), encoding="utf-8") as f:
            cls._fallback = json.load(f)
        # Prova a caricare la lingua richiesta
        if lang_code == "en":
            cls._translations = cls._fallback
        else:
            path = os.path.join(cls._language_dir, f"{lang_code}.json")
            GeneralLogHandler().debug(f"Caricamento file lingua: {path}")

            try:
                with open(path, encoding="utf-8") as f:
                    cls._translations = json.load(f)
            except Exception:
                cls._translations = cls._fallback

    @classmethod
    def tr(cls, key):
        """
        Restituisce la stringa tradotta per la chiave richiesta.
        Fallback: se manca nella lingua selezionata cerca in inglese,
        altrimenti restituisce la chiave così com’è.
        """
        return cls._translations.get(key) or cls._fallback.get(key) or key

    @classmethod
    def get_available_languages(cls):
        """
        Ritorna una lista di lingue disponibili trovate nella cartella Language.
        """
        langs = []
        for file in os.listdir(cls._language_dir):
            if file.endswith(".json"):
                code = file.replace(".json", "")
                langs.append(code)
        return sorted(langs)

    @classmethod
    def current_language(cls):
        return cls._lang_code
    
    @staticmethod
    def get_current_language():
        lang = get_setting("language")
        # Non ritorna mai "en" se non è stato esplicitamente impostato
        return lang.strip().lower() if lang and lang.strip().lower() in Translator.get_language_name_map() else None

    @classmethod
    def get_language_name_map(cls) -> dict[str, str]:
        """
        Ritorna un dizionario {codice: nome visibile} delle lingue.
        """
        return {
            "en": "English",
            "it": "Italiano",
            "es": "Español",
            "de": "Deutsch",
            "br": "Brasileiro",
            "pt": "Português"
        }
