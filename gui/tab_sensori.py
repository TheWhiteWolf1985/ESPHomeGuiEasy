from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton, QHBoxLayout, QSpinBox, QLineEdit, QComboBox
from PyQt6.QtCore import Qt
from gui.sensor_canvas import SensorCanvas
from core.yaml_handler import YAMLHandler
from gui.color_pantone import Pantone
from ruamel.yaml import YAML
from gui.sensor_block_item import SensorBlockItem
from core.translator import Translator
from gui.block_selection_dialog import *
from gui.sensor_block_item import SensorBlockItem
from gui.action_block_item import ActionBlockItem
from gui.trigger_block_item import TriggerBlockItem
from gui.condition_block_item import ConditionBlockItem
from gui.timer_block_item import TimerBlockItem
from gui.script_block_item import ScriptBlockItem
import os

class TabSensori(QWidget):
    def __init__(self, yaml_editor, logger, tab_settings):
        super().__init__()
        self.logger = logger
        self.tab_settings = tab_settings  

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- GroupBox per la creazione sensori ---
        sensor_creation = QGroupBox(Translator.tr("sensors_creation"))
        sensor_creation.setStyleSheet(Pantone.GROUPBOX_STYLE)
        sensor_layout = QVBoxLayout()

        self.sensor_canvas = SensorCanvas()
        self.sensor_canvas.setMinimumHeight(400)

        # Pulsanti azione
        self.add_sensor_btn = QPushButton("➕ " + Translator.tr("add_sensor"))
        self.add_action_btn = QPushButton("➕ " + Translator.tr("add_action"))
        self.add_trigger_btn = QPushButton("➕ " + Translator.tr("add_trigger"))
        self.add_condition_btn = QPushButton("➕ " + Translator.tr("add_condition"))
        self.add_timer_btn = QPushButton("➕ " + Translator.tr("add_timer"))
        self.add_script_btn = QPushButton("➕ " + Translator.tr("add_script"))
        self.update_yaml_btn = QPushButton("🔁 " + Translator.tr("update_yaml"))
        self.update_yaml_btn.setStyleSheet(Pantone.UPDATE_YAML_BTN_STYLE)

        # Applica stile comune e larghezza fissa
        for btn in [
            self.add_sensor_btn, self.add_action_btn, self.add_trigger_btn,
            self.add_condition_btn, self.add_timer_btn, self.add_script_btn
        ]:
            btn.setStyleSheet(Pantone.BUTTON_STYLE_GREEN)
            btn.setFixedWidth(180)

        # Connessioni ai metodi stub
        self.add_sensor_btn.clicked.connect(self.aggiungi_blocco_sensore)
        self.add_action_btn.clicked.connect(self.aggiungi_blocco_azione)
        self.add_trigger_btn.clicked.connect(self.aggiungi_blocco_trigger)
        self.add_condition_btn.clicked.connect(self.aggiungi_blocco_condizione)
        self.add_timer_btn.clicked.connect(self.aggiungi_blocco_timer)
        self.add_script_btn.clicked.connect(self.aggiungi_blocco_script)
        self.update_yaml_btn.clicked.connect(self.aggiorna_yaml_da_blocchi)

        # --- Layout a due righe per i pulsanti di aggiunta ---
        row1 = QHBoxLayout()
        row1.addWidget(self.add_sensor_btn)
        row1.addWidget(self.add_action_btn)
        row1.addWidget(self.add_trigger_btn)

        row2 = QHBoxLayout()
        row2.addWidget(self.add_condition_btn)
        row2.addWidget(self.add_timer_btn)
        row2.addWidget(self.add_script_btn)

        # --- Pulsante aggiornamento YAML centrato ---
        sensor_btn_layout = QVBoxLayout()
        sensor_btn_layout.addLayout(row1)
        sensor_btn_layout.addLayout(row2)
        sensor_btn_layout.addSpacing(10)
        sensor_btn_layout.addStretch()
        sensor_btn_layout.addWidget(self.update_yaml_btn, alignment=Qt.AlignmentFlag.AlignRight)


        sensor_btn_widget = QWidget()
        sensor_btn_widget.setLayout(sensor_btn_layout)

        sensor_layout.addWidget(self.sensor_canvas)
        sensor_layout.addWidget(sensor_btn_widget)
        sensor_creation.setLayout(sensor_layout)

        layout.addWidget(sensor_creation)

    def _editor(self):
        main = self.window()
        if hasattr(main, "yaml_editor") and main.yaml_editor:
            return main.yaml_editor
        return None


    def aggiorna_yaml_da_blocchi(self):
        """
        @brief Aggiorna SOLO la sezione sensori nel file YAML, mantenendo il resto invariato.
        Logga eventuali blocchi ignorati per campi incompleti.
        """
        try:
            main = self.window()
            editor = self._editor()
            if editor is None:
                return

            from core.yaml_handler import YAMLHandler
            current_yaml = editor.toPlainText()

            # Usa metodo esteso con lista blocchi scartati
            scene = self.sensor_canvas.scene()
            new_yaml, scartati = YAMLHandler.generate_yaml_sensors_only_with_log(scene, current_yaml)

            editor.setPlainText(new_yaml)

            if self.logger:
                if scartati:
                    for titolo_blocco in scartati:
                        self.logger.log(
                            Translator.tr("sensor_block_skipped").format(name=titolo_blocco),
                            "warning"
                        )
                else:
                    self.logger.log(Translator.tr("yaml_updated_from_sensors"), "success")

        except RuntimeError as e:
            print(f"[Errore YAML TabSensori] {e}")
            try:
                if hasattr(main, "logger"):
                    self.logger.log(Translator.tr("yaml_update_crash_sensors").format(error=str(e)), "error")
            except Exception:
                pass

    def get_sensor_canvas(self):
        return self.sensor_canvas
    
    def aggiorna_blocchi_da_yaml(self, yaml_content):
        """
        @brief Parsea il file YAML e ricrea i blocchi dei sensori sul canvas.
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

        # 3. Carica definizioni da sensors.json
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "..", "config", "sensors.json")
        dialog = SensorSelectionDialog(sensors_json_path=json_path)
        sensor_defs = dialog.sensors

        # 4. Ricrea ogni blocco
        for sensor in data["sensor"]:
            platform = sensor.get("platform", "").lower()
            name = sensor.get("name", "Nuovo Sensore")

            # Trova definizione da JSON
            sensor_def = next(
                (s for s in sensor_defs if s["platform"] == platform or s["label"] == name),
                None
            )

            if not sensor_def:
                continue  # salta sensori non definiti

            # Crea blocco
            blocco = SensorBlockItem(title=name)
            blocco.name_edit.setText(name)

            # Imposta tipo connessione
            conn_type = self.tab_settings.detect_connection_type(sensor_def) if hasattr(self.tab_settings, "detect_connection_type") else "custom"
            blocco.conn_type_display.setText(conn_type)

            # Costruisci parametri e outputs
            param_list = sensor_def.get("params", [])
            blocco.build_from_params(param_list)

            outputs = sensor_def.get("outputs", [])
            blocco.build_from_returns(outputs)

            # Popola i parametri dinamici dal YAML
            for key, widget in blocco.param_widgets.items():
                value = sensor.get(key)
                if value is not None:
                    if isinstance(widget, QLineEdit):
                        widget.setText(str(value))
                    elif isinstance(widget, QSpinBox):
                        try:
                            widget.setValue(int(str(value).replace("s", "")))
                        except Exception:
                            pass
                    elif isinstance(widget, QComboBox):
                        idx = widget.findText(str(value))
                        if idx >= 0:
                            widget.setCurrentIndex(idx)

            # Popola anche i campi output (es. temperature, humidity)
            for output_key, output_widget in getattr(blocco, "output_links", {}).items():
                if output_key in sensor and isinstance(sensor[output_key], dict):
                    name_val = sensor[output_key].get("name", "")
                    output_widget.setText(name_val)

            self.get_sensor_canvas().add_sensor_block(blocco)



    def aggiorna_label(self):
        from core.translator import Translator
        self.sensor_canvas.setToolTip(Translator.tr("sensors_creation"))
        self.add_sensor_btn.setText("➕ " + Translator.tr("add_sensor"))
        self.update_yaml_btn.setText("🔁 " + Translator.tr("update_yaml"))
        # Aggiorna i blocchi già presenti nel canvas (se ce ne sono)
        for item in self.sensor_canvas.scene().items():
            if hasattr(item, "aggiorna_label"):
                item.aggiorna_label()

    def aggiungi_blocco_sensore(self):
        """
        @brief Apre la dialog di selezione sensore e aggiunge un blocco al canvas se confermato.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "..", "config", "sensors.json")

        dialog = SensorSelectionDialog(sensors_json_path=json_path, parent=self)
        if dialog.exec():
            selected = dialog.get_selected_sensor()
            if selected:
                label = selected.get("label", "Nuovo Sensore")
                solo_nome = label.split(" (")[0]  # Prende tutto prima della prima parentesi aperta
                blocco = SensorBlockItem(title=solo_nome)
                blocco.sensor_platform = selected.get("platform", "custom")

                # Imposta nome e tipo
                blocco.name_edit.setText(solo_nome)
                conn_type = dialog.detect_connection_type(selected)
                blocco.conn_type_display.setText(conn_type)

                # Costruzione dinamica dei parametri
                param_list = selected.get("params", [])
                blocco.build_from_params(param_list)

                outputs = selected.get("outputs", [])
                blocco.build_from_returns(outputs)

                self.sensor_canvas.add_sensor_block(blocco)                

    def aggiungi_blocco_azione(self):
        """
        @brief Apre la dialog di selezione azione e aggiunge un blocco al canvas se confermato.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "..", "config", "actions.json")

        from gui.block_selection_dialog import ActionSelectionDialog
        dialog = ActionSelectionDialog(actions_json_path=json_path, parent=self)
        if dialog.exec():
            selected = dialog.get_selected_action()
            if selected:
                label = selected.get("label", "Nuova Azione")
                solo_nome = label.split(" (")[0]
                blocco = ActionBlockItem(title=solo_nome)

                # Costruzione dinamica dei parametri
                param_list = selected.get("params", [])
                blocco.build_from_params(param_list)

                self.sensor_canvas.add_sensor_block(blocco)

    def aggiungi_blocco_trigger(self):
        """
        @brief Apre la dialog di selezione trigger e aggiunge un blocco al canvas se confermato.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "..", "config", "triggers.json")

        dialog = TriggerSelectionDialog(triggers_json_path=json_path, parent=self)
        if dialog.exec():
            selected = dialog.get_selected_trigger()
            if selected:
                label = selected.get("label", "Nuovo Trigger")
                solo_nome = label.split(" (")[0]
                blocco = TriggerBlockItem(title=solo_nome)

                param_list = selected.get("params", [])
                blocco.build_from_params(param_list)

                self.sensor_canvas.add_sensor_block(blocco)


    def aggiungi_blocco_condizione(self):
        """
        @brief Apre la dialog di selezione condizione e aggiunge un blocco al canvas se confermato.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "..", "config", "conditions.json")

        dialog = ConditionSelectionDialog(conditions_json_path=json_path, parent=self)
        if dialog.exec():
            selected = dialog.get_selected_condition()
            if selected:
                label = selected.get("label", "Nuova Condizione")
                solo_nome = label.split(" (")[0]
                blocco = ConditionBlockItem(title=solo_nome)

                param_list = selected.get("params", [])
                blocco.build_from_params(param_list)

                self.sensor_canvas.add_sensor_block(blocco)


    def aggiungi_blocco_timer(self):
        """
        @brief Apre la dialog di selezione timer e aggiunge un blocco al canvas se confermato.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "..", "config", "timers.json")

        dialog = TimerSelectionDialog(timers_json_path=json_path, parent=self)
        if dialog.exec():
            selected = dialog.get_selected_timer()
            if selected:
                label = selected.get("label", "Nuovo Timer")
                solo_nome = label.split(" (")[0]
                blocco = TimerBlockItem(title=solo_nome)

                param_list = selected.get("params", [])
                blocco.build_from_params(param_list)

                self.sensor_canvas.add_sensor_block(blocco)


    def aggiungi_blocco_script(self):
        """
        @brief Apre la dialog di selezione script e aggiunge un blocco al canvas se confermato.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "..", "config", "scripts.json")

        dialog = ScriptSelectionDialog(scripts_json_path=json_path, parent=self)
        if dialog.exec():
            selected = dialog.get_selected_script()
            if selected:
                label = selected.get("label", "Nuovo Script")
                solo_nome = label.split(" (")[0]
                blocco = ScriptBlockItem(title=solo_nome)

                param_list = selected.get("params", [])
                blocco.build_from_params(param_list)

                self.sensor_canvas.add_sensor_block(blocco)

