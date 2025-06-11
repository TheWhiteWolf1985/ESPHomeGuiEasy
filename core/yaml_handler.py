"""
@file yaml_handler.py
@brief Gestione avanzata del file YAML per esphomeGuieasy.

Contiene funzioni per caricare, salvare, modificare dinamicamente sezioni YAML
senza sovrascrivere il contenuto globale, mantenendo commenti e ordine.
"""

import os
import json
from ruamel.yaml import YAML
from PyQt6.QtWidgets import QGraphicsScene
from gui.sensor_block_item import SensorBlockItem

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.preserve_quotes = True

class YAMLHandler:
    """
    @class YAMLHandler
    @brief Classe per gestire le operazioni legate ai file YAML.
    """

    # -----------------------------------------------
    # |  Caricamento del template YAML di default   |
    # -----------------------------------------------
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

    # -----------------------------------------------------------------
    # |  Aggiornamento sezioni generali YAML (senza toccare sensori)  |
    # -----------------------------------------------------------------
    @staticmethod
    def generate_yaml_general_sections(current_yaml: str, device_name: str, board: str, ssid: str, password: str) -> str:
        """
        @brief Aggiorna solo le sezioni generali nel file YAML senza toccare la sezione sensori.
        @param current_yaml YAML attuale come stringa
        @param device_name Nome del dispositivo (esphome.name)
        @param board Nome board tecnica
        @param ssid SSID rete WiFi
        @param password Password WiFi
        @return YAML aggiornato (solo sezioni generali)
        """
        try:
            from ruamel.yaml import YAML
            yaml = YAML()
            yaml.indent(mapping=2, sequence=4, offset=2)
            yaml.preserve_quotes = True

            from io import StringIO
            data = yaml.load(current_yaml) or {}

            # Sezione esphome
            data['esphome'] = data.get('esphome', {})
            data['esphome']['name'] = device_name or "nome_dispositivo"
            data['esphome']['friendly_name'] = device_name or "Dispositivo ESPHome"

            # Sezione esp32
            data['esp32'] = {
                'board': board or "esp32dev",
                'framework': {'type': 'arduino'}
            }

            # Sezione wifi
            data['wifi'] = {
                'ssid': ssid or "YourSSID",
                'password': password or "YourPassword"
            }

            output = StringIO()
            yaml.dump(data, output)
            return output.getvalue()

        except Exception as e:
            return f"# Errore aggiornamento YAML (generale): {e}"

    # -------------------------------------------------------------
    # |   Aggiorna solo la sezione sensori senza toccare il resto  |
    # -------------------------------------------------------------
    @staticmethod
    def generate_yaml_sensors_only(canvas: QGraphicsScene, current_yaml: str) -> str:
        """
        @brief Aggiorna solo la sezione sensori nel file YAML senza toccare le sezioni generali.
        @param canvas QGraphicsScene contenente i blocchi sensori
        @param current_yaml YAML attuale da cui partire
        @return YAML aggiornato (solo sensori)
        """
        try:
            data = yaml.load(current_yaml) or {}

            # Sezione sensor
            data['sensor'] = []

            for item in canvas.items():
                if isinstance(item, SensorBlockItem):
                    params = {}

                    # Recupera ogni widget dinamico e il suo valore
                    for key, widget in getattr(item, 'param_widgets', {}).items():
                        if hasattr(widget, "text"):
                            value = widget.text().strip()
                        elif hasattr(widget, "value"):
                            value = widget.value()
                        elif hasattr(widget, "currentText"):
                            value = widget.currentText().strip()
                        else:
                            continue

                        if value not in ["", None]:
                            params[key] = value

                    # Nome principale (fallback se non c'è un campo 'name')
                    if "name" not in params:
                        raw_name = item.name_edit.text().strip()
                        if raw_name:
                            params["name"] = raw_name

                    # Piattaforma sensore (deducibile dal tipo selezionato)
                    sensor_type = item.conn_type_display.text().strip().lower()
                    platform_map = {
                        "analogico": "adc",
                        "digitale": "gpio",
                        "i2c": "i2c",  # dipenderà poi da piattaforma reale
                    }

                    platform = item.sensor_platform if hasattr(item, 'sensor_platform') else platform_map.get(sensor_type, "custom")

                    # Includi nel blocco YAML
                    yaml_block = {"platform": platform}
                    yaml_block.update(params)
                    data['sensor'].append(yaml_block)


            from io import StringIO
            output = StringIO()
            yaml.dump(data, output)
            return output.getvalue()

        except Exception as e:
            return f"# Errore aggiornamento YAML (sensori): {e}"

    # -------------------------------------------------------------------------
    # |     Estrazione dei moduli attivi dagli accordion/widget_map           |
    # -------------------------------------------------------------------------
    @staticmethod
    def extract_module_sections_from_widgets(widget_map: dict, modules_schema_path: str) -> dict:
        with open(modules_schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        modules_dict = {}

        for human_name, info in schema.items():
            yaml_key = human_name.lower().replace(" ", "_")
            fields = widget_map.get(human_name)
            if not fields:
                continue
            enabled_widget = fields.get("enabled")
            if enabled_widget is not None and hasattr(enabled_widget, "isChecked") and not enabled_widget.isChecked():
                continue
            params = {}
            for field in info["fields"]:
                key = field["key"]
                widget = fields.get(key)
                if key == "enabled":
                    continue
                if widget is None:
                    continue
                # Gestione tipo numerico/spinbox
                if field["type"] == "int":
                    if hasattr(widget, "value"):
                        v = widget.value()
                        # Se è update_interval, aggiungi 's'
                        if key == "update_interval":
                            value = f"{v}s"
                        else:
                            value = v
                elif hasattr(widget, "text"):
                    value = widget.text().strip()
                elif hasattr(widget, "currentText"):
                    value = widget.currentText().strip()
                elif hasattr(widget, "isChecked"):
                    value = widget.isChecked()
                if value not in [None, ""]:
                    params[key] = value
            modules_dict[yaml_key] = params
        return modules_dict


    # -------------------------------------------------------------------------
    # |   Aggiornamento dello YAML aggiungendo/rimuovendo sezioni dei moduli   |
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_yaml_with_modules(current_yaml: str, modules_dict: dict, modules_schema_path: str) -> str:
        """
        @brief Aggiorna/aggiunge/rimuove le sezioni moduli (top-level) nello YAML.
        @param current_yaml YAML attuale come stringa
        @param modules_dict dict {modulo_yaml_key: {parametri...}}
        @param modules_schema_path Percorso al file modules_schema.json (serve per sapere i nomi di tutti i moduli gestiti)
        @return YAML completo aggiornato
        """
        try:
            data = yaml.load(current_yaml) or {}

            # Carica lista dei moduli supportati (chiavi YAML)
            with open(modules_schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            supported_modules = [k.lower().replace(" ", "_") for k in schema]

            # Rimuovi sezioni moduli non più attive
            for mod in supported_modules:
                if mod in data and mod not in modules_dict:
                    del data[mod]

            # Aggiorna/inserisci sezioni moduli attive
            for mod, params in modules_dict.items():
                data[mod] = params

            # Serializza YAML
            from io import StringIO
            output = StringIO()
            yaml.dump(data, output)
            return output.getvalue()

        except Exception as e:
            return f"# Errore aggiornamento YAML (moduli): {e}"

    @staticmethod
    def extract_modules_from_yaml(yaml_string: str, modules_schema_path: str) -> dict:
        with open(modules_schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        data = yaml.load(yaml_string) or {}
        result = {}
        for gui_name, info in schema.items():
            yaml_key = gui_name.lower().replace(" ", "_")
            if yaml_key in data and isinstance(data[yaml_key], dict):
                values = {}
                for field in info["fields"]:
                    k = field["key"]
                    if k in data[yaml_key]:
                        val = data[yaml_key][k]
                        # Parsing specifico per int/update_interval
                        if field["type"] == "int" and k == "update_interval":
                            if isinstance(val, str) and val.endswith("s"):
                                try:
                                    val = int(val.rstrip("s"))
                                except Exception:
                                    val = 1
                            elif isinstance(val, int):
                                pass  # già ok
                        values[k] = val
                result[gui_name] = values
        return result

