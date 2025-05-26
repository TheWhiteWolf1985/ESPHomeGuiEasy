"""
@file yaml_handler.py
@brief Gestione centralizzata del file YAML per esphomeGuieasy.

Contiene funzioni per caricare, salvare, sostituire e gestire template YAML
con placeholder dinamici.
"""

import os

class YAMLHandler:
    """
    @class YAMLHandler
    @brief Classe per gestire le operazioni legate ai file YAML.
    """

    @staticmethod
    def load_default_yaml():
        """
        @brief Carica il contenuto del template YAML con placeholder.

        @return stringa del file YAML oppure messaggio d'errore
        """
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(base_path, "../config/default_template.yaml")

            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"# Errore nel caricamento del template: {e}"
