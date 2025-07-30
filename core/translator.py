# -*- coding: utf-8 -*-
"""
@file translator.py
@brief Provides translation utilities for the ESPHomeGUIeasy interface.

@defgroup core Core Modules
@ingroup main
@brief Core logic: YAML handling, logging, settings, flashing, etc.

Loads JSON translation files from the /Language folder and provides translation lookup methods.  
Includes language fallback logic and dynamic discovery of available languages.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

import os, json
from core.settings_db import get_setting
from core.log_handler import GeneralLogHandler
from config.GUIconfig import LANGUAGES

class Translator:
    """
    @brief Static utility class for managing UI translations.

    Supports language file loading, key translation, and language code ↔ name mapping.
    """
    _translations = {}
    _fallback = {}
    _lang_code = "en"
    _language_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../language")

    @classmethod
    def load_language(cls, lang_code):
        """
        @brief Loads the translation file for the given language code and sets fallback to English.

        @param lang_code Language code (e.g., "en", "it", "de").
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
        @brief Returns the translated string for the requested key.

        Falls back to English if not found, or returns the key itself if missing.
        """
        return cls._translations.get(key) or cls._fallback.get(key) or key

    @classmethod
    def get_available_languages(cls):
        """
        @brief Scans the /Language folder and returns all available translation codes.

        @return Sorted list of language codes found as `.json` files.
        """
        langs = []
        for file in os.listdir(cls._language_dir):
            if file.endswith(".json"):
                code = file.replace(".json", "")
                langs.append(code)
        return sorted(langs)

    @classmethod
    def current_language(cls):
        """
        @brief Returns the current user language from database settings, if valid.

        @return Lowercase language code (e.g., "en"), or None if unset/invalid.
        """
        return cls._lang_code
    
    @staticmethod
    def get_current_language():
        lang = get_setting("language")
        # Non ritorna mai "en" se non è stato esplicitamente impostato
        return lang.strip().lower() if lang and lang.strip().lower() in Translator.get_language_name_map() else None

    @classmethod
    def get_language_name_map(cls) -> dict[str, str]:
        """
        @brief Returns a dictionary mapping language codes to human-readable names.

        @return dict { "en": "English", "it": "Italiano", ... }
        """
        return LANGUAGES
