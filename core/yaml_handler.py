# -*- coding: utf-8 -*-
"""
@file yaml_handler.py
@brief Provides high-level YAML processing for ESPHome projects.

@defgroup core Core Modules
@ingroup main
@brief Core logic: YAML handling, logging, settings, flashing, etc.

Handles:
- Loading YAML templates
- Updating general sections (esphome, esp32, wifi)
- Building sensor sections from GUI canvas
- Inserting/removing module sections
- Extracting module data from YAML or widgets

Preserves formatting and comments using ruamel.yaml.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

import os, json
from ruamel.yaml import YAML
from PyQt6.QtWidgets import *
from gui.sensor_block_item import SensorBlockItem
from io import StringIO

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.preserve_quotes = True

class YAMLHandler:
    """
    @brief Static class to handle YAML operations in the application.

    All methods are static and operate on text or GUI canvas to generate valid YAML.
    """
    # -----------------------------------------------
    # |  Caricamento del template YAML di default   |
    # -----------------------------------------------
    @staticmethod
    def load_default_yaml():
        """
        @brief Loads the default YAML template with placeholders.

        @return YAML content as string, or error message on failure.
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
        @brief Updates only the general sections of a YAML file (esphome, esp32, wifi), without touching sensors.

        @param current_yaml Existing YAML as string.
        @param device_name Device name (used in esphome section).
        @param board Board type (e.g., esp32dev).
        @param ssid WiFi SSID.
        @param password WiFi password.
        @return Updated YAML as string.
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
        @brief Generates only the `sensor` section of the YAML from the GUI canvas.

        @param canvas QGraphicsScene containing sensor blocks.
        @param current_yaml Existing YAML as string.
        @return Updated YAML string with only the sensor section replaced.
        """
        try:
            data = yaml.load(current_yaml) or {}

            # Sezione sensor
            data['sensor'] = []

            for item in canvas.items():
                if isinstance(item, SensorBlockItem):
                    params = {}

                    if not item.has_valid_data():
                        continue

                    # Recupera ogni widget dinamico e il suo valore
                    for key, widget in getattr(item, 'param_widgets', {}).items():
                        value = None

                        if isinstance(widget, QSpinBox):
                            v = widget.value()
                            value = f"{v}s" if key == "update_interval" else v

                        elif isinstance(widget, QComboBox):
                            value = widget.currentText().strip()

                        elif isinstance(widget, QLineEdit):
                            txt = widget.text().strip()
                            if key == "update_interval" and txt.isdigit():
                                value = f"{txt}s"
                            elif txt.isdigit():
                                value = int(txt)
                            else:
                                value = txt

                        if value not in ["", None]:
                            params[key] = value

                    # Nome principale (fallback se non c'è un campo 'name')
                    raw_name = item.name_edit.text().strip()
                    if raw_name and raw_name != item.title:
                        params["name"] = raw_name

                    # Piattaforma sensore (deducibile dal tipo selezionato)
                    sensor_type = item.conn_type_display.text().strip().lower()
                    platform_map = {
                        "analogico": "adc",
                        "digitale": "gpio",
                        "i2c": "i2c",
                    }

                    platform = item.sensor_platform if hasattr(item, 'sensor_platform') else platform_map.get(sensor_type, "custom")

                    # Includi nel blocco YAML
                    yaml_block = {"platform": platform}
                    yaml_block.update(params)

                    # Gestione outputs (es. temperature, humidity)
                    for output_key, name_widget in getattr(item, "output_links", {}).items():
                        nome_output = name_widget.text().strip()
                        if nome_output:
                            yaml_block[output_key] = {"name": nome_output}

                    data['sensor'].append(yaml_block)

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
        """
        @brief Extracts top-level module sections from a widget map based on a JSON schema.

        @param widget_map Dictionary of GUI widget groups.
        @param modules_schema_path Path to modules_schema.json file.
        @return Dict of enabled modules with their parameters.
        """
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
        @brief Adds or updates top-level module sections in the YAML based on provided dictionary.

        @param current_yaml Existing YAML as string.
        @param modules_dict Dictionary of modules and parameters to write.
        @param modules_schema_path Path to the modules schema.
        @return Updated YAML as string.
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
        """
        @brief Reads a YAML string and extracts the values of supported modules as defined in schema.

        @param yaml_string Full YAML content as string.
        @param modules_schema_path Path to modules_schema.json.
        @return Dict { gui_module_name: {key: value, ...} }
        """
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

    @staticmethod
    def generate_yaml_sensors_only_with_log(canvas: QGraphicsScene, current_yaml: str) -> tuple[str, list]:
        """
        @brief Like generate_yaml_sensors_only, but also returns a list of ignored sensor blocks.

        @param canvas QGraphicsScene with sensor items.
        @param current_yaml YAML input string.
        @return Tuple (yaml_string, ignored_sensor_names: list)
        """
        scartati = []
        try:
            data = yaml.load(current_yaml) or {}
            data['sensor'] = []

            for item in canvas.items():
                if isinstance(item, SensorBlockItem):
                    if not item.has_valid_data():
                        scartati.append(item.title)
                        continue

                    params = {}
                    for key, widget in getattr(item, 'param_widgets', {}).items():
                        value = None
                        if isinstance(widget, QSpinBox):
                            v = widget.value()
                            value = f"{v}s" if key == "update_interval" else v
                        elif isinstance(widget, QComboBox):
                            value = widget.currentText().strip()
                        elif isinstance(widget, QLineEdit):
                            txt = widget.text().strip()
                            if key == "update_interval" and txt.isdigit():
                                value = f"{txt}s"
                            elif txt.isdigit():
                                value = int(txt)
                            else:
                                value = txt

                        if value not in ["", None]:
                            params[key] = value

                    raw_name = item.name_edit.text().strip()
                    if raw_name and raw_name != item.title:
                        params["name"] = raw_name

                    sensor_type = item.conn_type_display.text().strip().lower()
                    platform_map = {"analogico": "adc", "digitale": "gpio", "i2c": "i2c"}
                    platform = item.sensor_platform if hasattr(item, 'sensor_platform') else platform_map.get(sensor_type, "custom")

                    yaml_block = {"platform": platform}
                    yaml_block.update(params)

                    for output_key, name_widget in getattr(item, "output_links", {}).items():
                        nome_output = name_widget.text().strip()
                        if nome_output:
                            yaml_block[output_key] = {"name": nome_output}

                    data['sensor'].append(yaml_block)

            output = StringIO()
            yaml.dump(data, output)
            return output.getvalue(), scartati

        except Exception as e:
            return f"# Errore aggiornamento YAML (sensori): {e}", []
