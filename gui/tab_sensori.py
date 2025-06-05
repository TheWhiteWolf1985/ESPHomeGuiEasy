from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
from gui.sensor_canvas import SensorCanvas
from core.yaml_handler import YAMLHandler
from gui.color_pantone import Pantone
from ruamel.yaml import YAML
from gui.sensor_block_item import SensorBlockItem
from core.translator import Translator

class TabSensori(QWidget):
    def __init__(self, yaml_editor, logger, tab_settings):
        super().__init__()
        self.logger = logger
        self.tab_settings = tab_settings

        common_btn_style = """
            QPushButton {
                background-color: #6A9955;
                color: white;
                border-radius: 8px;
                font-size: 12pt;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #4e7d44;
            }
        """        

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- GroupBox per la creazione sensori ---
        sensor_creation = QGroupBox(Translator.tr("sensors_creation"))
        sensor_creation.setStyleSheet(Pantone.GROUPBOX_STYLE)
        sensor_layout = QVBoxLayout()

        self.sensor_canvas = SensorCanvas()
        self.sensor_canvas.setMinimumHeight(400)

        self.add_sensor_btn = QPushButton("➕ " + Translator.tr("add_sensor"))
        self.add_sensor_btn.setStyleSheet(common_btn_style)
        self.add_sensor_btn.setFixedWidth(180)
        self.add_sensor_btn.clicked.connect(self.aggiungi_blocco_sensore)

        self.update_yaml_btn = QPushButton(Translator.tr("update_yaml"))
        self.update_yaml_btn.setStyleSheet(common_btn_style)
        self.update_yaml_btn.setFixedWidth(180)
        self.update_yaml_btn.clicked.connect(self.aggiorna_yaml_da_blocchi)

        sensor_btn_layout = QHBoxLayout()
        sensor_btn_layout.addWidget(self.add_sensor_btn)
        sensor_btn_layout.addWidget(self.update_yaml_btn)

        sensor_btn_widget = QWidget()
        sensor_btn_widget.setLayout(sensor_btn_layout)

        sensor_layout.addWidget(self.sensor_canvas)
        sensor_layout.addWidget(sensor_btn_widget)
        sensor_creation.setLayout(sensor_layout)

        layout.addWidget(sensor_creation)

    def aggiungi_blocco_sensore(self):
        """
        @brief Crea e aggiunge un nuovo blocco sensore nel canvas.
        """
        nuovo_blocco = SensorBlockItem(Translator.tr("new_sensor"))
        self.sensor_canvas.add_sensor_block(nuovo_blocco)

    def _editor(self):
        main = self.window()
        if hasattr(main, "yaml_editor") and main.yaml_editor:
            return main.yaml_editor
        return None


    def aggiorna_yaml_da_blocchi(self):
        """
        @brief Aggiorna SOLO la sezione sensori nel file YAML, mantenendo il resto invariato.
        """
        try:
            main = self.window()
            editor = self._editor()
            if editor is None:
                return

            from core.yaml_handler import YAMLHandler
            current_yaml = editor.toPlainText()
            new_yaml = YAMLHandler.generate_yaml_sensors_only(
                canvas=self.sensor_canvas.scene(),
                current_yaml=current_yaml
            )
            editor.setPlainText(new_yaml)
            if self.logger:
                self.logger.log(Translator.tr("yaml_updated_from_sensors"), "success")

        except RuntimeError as e:
            print(f"[Errore YAML TabSensori] {e}")
            try:
                if hasattr(main, "logger"):
                    main.logger.log(f"❌ YAML update crash (sensori): {e}", "error")
            except Exception:
                pass




    def get_sensor_canvas(self):
        return self.sensor_canvas
    
    def aggiorna_blocchi_da_yaml(self, yaml_content):
        """
        Parsea il file YAML e ricrea i blocchi dei sensori sul canvas.
        """

        # 1. Svuota tutti i blocchi esistenti
        self.get_sensor_canvas().clear_blocks()

        # 2. Parsea il contenuto YAML
        yaml = YAML(typ="safe")
        try:
            data = yaml.load(yaml_content)
        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.log(f"{Translator.tr('yaml_parse_error')}: {e}", "error")
            return

        if not data or "sensor" not in data or not isinstance(data["sensor"], list):
            if hasattr(self, "logger"):
                self.logger.log(Translator.tr("no_sensor_section"), "warning")
            return

        # 3. Ricrea un blocco per ogni sensore
        for sensor in data["sensor"]:
            # Prendi tipo sensore e info
            platform = sensor.get("platform", "").lower()
            name = sensor.get("name", "")
            pin = sensor.get("pin", "")
            interval = None

            # Determina tipo per il combo
            if platform == "dht":
                sensor_type = sensor.get("model", "dht11")
                name = sensor.get("temperature", {}).get("name", "DHT Temp")
                pin = sensor.get("pin", "")
                interval = sensor.get("update_interval", "60s").replace("s", "")
            elif platform == "gpio":
                sensor_type = "gpio"
                interval = ""  # GPIO non ha update interval di solito
            elif platform == "adc":
                sensor_type = "analogico"
                interval = sensor.get("update_interval", "60s").replace("s", "")
            else:
                sensor_type = platform

            # Crea blocco
            nuovo_blocco = SensorBlockItem(name)
            # Imposta tipo sensore
            idx = nuovo_blocco.type_combo.findText(sensor_type, Qt.MatchFlag.MatchFixedString)
            if idx >= 0:
                nuovo_blocco.type_combo.setCurrentIndex(idx)
            # Imposta nome
            nuovo_blocco.name_edit.setText(name)
            # Imposta pin
            nuovo_blocco.pin_edit.setText(str(pin))
            # Imposta intervallo, se presente
            if interval and hasattr(nuovo_blocco, "update_spin"):
                try:
                    nuovo_blocco.update_spin.setValue(int(interval))
                except Exception:
                    pass  # intervallo non numerico, ignora

            self.get_sensor_canvas().add_sensor_block(nuovo_blocco)

    def aggiorna_label(self):
        from core.translator import Translator
        self.sensor_canvas.setToolTip(Translator.tr("sensors_creation"))
        self.add_sensor_btn.setText("➕ " + Translator.tr("add_sensor"))
        self.update_yaml_btn.setText(Translator.tr("update_yaml"))
        # Aggiorna i blocchi già presenti nel canvas (se ce ne sono)
        for item in self.sensor_canvas.scene().items():
            if hasattr(item, "aggiorna_label"):
                item.aggiorna_label()
