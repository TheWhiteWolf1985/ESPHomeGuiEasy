"""
@file yaml_handler.py
@brief Gestione avanzata del file YAML per esphomeGuieasy.

Contiene funzioni per caricare, salvare, modificare dinamicamente sezioni YAML
senza sovrascrivere il contenuto globale, mantenendo commenti e ordine.
"""

import os
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

    @staticmethod
    def generate_yaml_from_blocks(canvas: QGraphicsScene, current_yaml: str,
                                  device_name: str, board: str, ssid: str, password: str) -> str:
        """
        @brief Genera un file YAML aggiornato inserendo dati generali e sensori.
        @param canvas QGraphicsScene contenente i blocchi sensori
        @param current_yaml YAML attuale da cui partire
        @param device_name Nome del dispositivo (esphome.name)
        @param board Nome board tecnica
        @param ssid SSID rete WiFi
        @param password Password WiFi
        @return YAML completo aggiornato
        """
        try:
            data = yaml.load(current_yaml) or {}

            # === Sezione esphome ===
            data['esphome'] = data.get('esphome', {})
            data['esphome']['name'] = device_name or "nome_dispositivo"
            data['esphome']['friendly_name'] = device_name or "Dispositivo ESPHome"

            # === Sezione esp32 ===
            data['esp32'] = {
                'board': board or "esp32dev",
                'framework': {'type': 'arduino'}
            }

            # === Sezione wifi ===
            data['wifi'] = {
                'ssid': ssid or "YourSSID",
                'password': password or "YourPassword"
            }

            # === Sezione sensor ===
            data['sensor'] = []

            for item in canvas.items():
                if isinstance(item, SensorBlockItem):
                    sensor_type = item.type_combo.currentText()
                    name = item.name_edit.text().strip()
                    pin = item.pin_edit.text().strip()
                    interval = item.update_spin.value()

                    if not name:
                        continue

                    # Costruzione del blocco sensor YAML
                    if sensor_type.lower() in ['dht11', 'dht22']:
                        sensor_block = {
                            'platform': 'dht',
                            'model': sensor_type,
                            'pin': pin,
                            'temperature': {'name': f"{name}_Temp"},
                            'humidity': {'name': f"{name}_Hum"},
                            'update_interval': f"{interval}s"
                        }
                        data['sensor'].append(sensor_block)
                    elif sensor_type.lower() == 'gpio':
                        sensor_block = {
                            'platform': 'gpio',
                            'pin': pin,
                            'name': name
                        }
                        data['sensor'].append(sensor_block)
                    elif sensor_type.lower() == 'analogico':
                        sensor_block = {
                            'platform': 'adc',
                            'pin': pin,
                            'name': name,
                            'update_interval': f"{interval}s"
                        }
                        data['sensor'].append(sensor_block)

            # Serializza in stringa YAML
            from io import StringIO
            output = StringIO()
            yaml.dump(data, output)
            return output.getvalue()

        except Exception as e:
            return f"# Errore generazione YAML: {e}"
        
    @staticmethod
    def generate_yaml_general_sections(current_yaml: str, device_name: str, board: str, ssid: str, password: str) -> str:
        """
        Aggiorna solo le sezioni generali nel file YAML senza toccare la sezione sensori.
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


    def generate_yaml_sensors_only(canvas: QGraphicsScene, current_yaml: str) -> str:
        """
        Aggiorna solo la sezione sensori nel file YAML senza toccare le sezioni generali.
        """
        try:
            data = yaml.load(current_yaml) or {}

            # Sezione sensor
            data['sensor'] = []

            from gui.sensor_block_item import SensorBlockItem
            for item in canvas.items():
                if isinstance(item, SensorBlockItem):
                    sensor_type = item.type_combo.currentText()
                    name = item.name_edit.text().strip()
                    pin = item.pin_edit.text().strip()
                    interval = item.update_spin.value()

                    if not name:
                        continue

                    if sensor_type.lower() in ['dht11', 'dht22']:
                        sensor_block = {
                            'platform': 'dht',
                            'model': sensor_type,
                            'pin': pin,
                            'temperature': {'name': f"{name} Temp"},
                            'humidity': {'name': f"{name} Hum"},
                            'update_interval': f"{interval}s"
                        }
                        data['sensor'].append(sensor_block)
                    elif sensor_type.lower() == 'gpio':
                        sensor_block = {
                            'platform': 'gpio',
                            'pin': pin,
                            'name': name
                        }
                        data['sensor'].append(sensor_block)
                    elif sensor_type.lower() == 'analogico':
                        sensor_block = {
                            'platform': 'adc',
                            'pin': pin,
                            'name': name,
                            'update_interval': f"{interval}s"
                        }
                        data['sensor'].append(sensor_block)

            from io import StringIO
            output = StringIO()
            yaml.dump(data, output)
            return output.getvalue()

        except Exception as e:
            return f"# Errore aggiornamento YAML (sensori): {e}"

