# -*- coding: utf-8 -*-
"""
@file tab_sensori.py
@brief GUI tab managing sensors, actions, triggers, and logic blocks for ESPHome.

@defgroup gui GUI Modules
@ingroup main
@brief Graphical interface: canvas and block-based configuration.

Provides a visual interface for creating and connecting ESPHome components
such as sensors, actions, triggers, conditions, timers, and scripts.

The visual blocks are dynamically generated based on JSON definitions,
and YAML is generated or parsed accordingly.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton, QHBoxLayout, QSpinBox, QLineEdit, QComboBox
from PyQt6.QtCore import Qt
from gui.sensor_canvas import SensorCanvas
from core.yaml_handler import YAMLHandler
from gui.color_pantone import Pantone
from ruamel.yaml import YAML
from core.translator import Translator
from gui.block_selection_dialog import *
from gui.sensor_block_item import SensorBlockItem
from gui.action_block_item import ActionBlockItem
from gui.trigger_block_item import TriggerBlockItem
from gui.condition_block_item import ConditionBlockItem
from gui.timer_block_item import TimerBlockItem
from gui.script_block_item import ScriptBlockItem
import os
from config.GUIconfig import GlobalPaths


class TabSensori(QWidget):
    """
    @brief Tab widget that allows visual configuration of ESPHome sensors and logic blocks.

    This tab provides a drag-and-drop canvas to manage sensors, actions, triggers,
    and other ESPHome components as modular blocks. Each block is configured via forms
    and can be serialized to YAML or reconstructed from it.

    The components are defined in JSON files and dynamically rendered on the canvas.

    @note This class is part of the GUI layer and uses `SensorCanvas` for rendering blocks.
    """    
    def __init__(self, yaml_editor, logger, tab_settings):
        """
        @brief Constructor that initializes the tab layout and sensor creation interface.

        Builds the canvas, buttons, and group boxes for adding sensors and related ESPHome
        logic components. Connects UI actions and styles elements accordingly.

        @param yaml_editor Reference to the shared YAML editor (QPlainTextEdit).
        @param logger Reference to the application-wide logger instance.
        @param tab_settings Reference to the settings tab, used for connection type inference.
        """        
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
        """
        @brief Returns the active YAML editor instance from the main window.

        This utility method accesses the editor safely by checking its availability and existence.

        @return QTextEdit instance if valid, otherwise None.
        """        
        main = self.window()
        if hasattr(main, "yaml_editor") and main.yaml_editor:
            return main.yaml_editor
        return None


    def aggiorna_yaml_da_blocchi(self):
        """
        @brief Updates the YAML editor by extracting only the sensor-related blocks.

        Parses the current sensor canvas and generates an updated YAML string
        containing just the `sensor:` section while preserving other parts.

        Logs a warning for each block skipped due to incomplete fields.

        @note Uses `YAMLHandler.generate_yaml_sensors_only_with_log()`.
        """
        try:
            main = self.window()
            editor = self._editor()
            if editor is None:
                return

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
            try:
                if hasattr(self, "logger"):
                    self.logger.log(Translator.tr("yaml_update_crash_sensors").format(error=str(e)), "error")
                elif hasattr(main, "logger"):
                    main.logger.log(Translator.tr("yaml_update_crash_sensors").format(error=str(e)), "error")
                else:
                    from core.log_handler import GeneralLogHandler as log
                    log.error(f"[TabSensori] YAML update crash: {e}")
            except Exception:
                pass  # fallback assoluto


    def get_sensor_canvas(self):
        """
        @brief Returns the SensorCanvas instance used to manage visual blocks.

        @return Pointer to the SensorCanvas instance.
        """        
        return self.sensor_canvas
    
    def aggiorna_blocchi_da_yaml(self, yaml_content):
        """
        @brief Parses the provided YAML content and reconstructs visual sensor blocks.

        Clears all existing blocks, then loads sensor definitions from the JSON file
        and instantiates them as visual blocks within the canvas.

        @param yaml_content YAML content as string.
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
        json_path = GlobalPaths.SENSORS_JSON_PATH
        dialog = SensorSelectionDialog(sensors_json_path=json_path)
        sensor_defs = dialog.sensors

        # 4. Ricrea ogni blocco
        for sensor in data["sensor"]:
            platform = sensor.get("platform", "").lower()
            name = sensor.get("name", Translator.tr("new_sensor"))

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
        """
        @brief Updates all UI text labels in the tab based on the active translation.

        Also updates the labels of existing blocks in the scene, if available.
        """        
        self.sensor_canvas.setToolTip(Translator.tr("sensors_creation"))
        self.add_sensor_btn.setText("➕ " + Translator.tr("add_sensor"))
        self.update_yaml_btn.setText("🔁 " + Translator.tr("update_yaml"))
        # Aggiorna i blocchi già presenti nel canvas (se ce ne sono)
        for item in self.sensor_canvas.scene().items():
            if hasattr(item, "aggiorna_label"):
                item.aggiorna_label()

    def aggiungi_blocco_sensore(self):
        """
        @brief Opens the sensor selection dialog and adds the selected sensor block to the canvas.

        The block is dynamically built from JSON metadata and configured accordingly.
        """
        json_path = GlobalPaths.SENSORS_JSON_PATH

        dialog = SensorSelectionDialog(sensors_json_path=json_path, parent=self)
        if dialog.exec():
            selected = dialog.get_selected_sensor()
            if selected:
                label = selected.get("label", Translator.tr("new_sensor"))
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
        @brief Opens the action selection dialog and adds the selected action block to the canvas.

        Dynamically builds parameters from the JSON action definition.
        """
        json_path = GlobalPaths.ACTIONS_JSON_PATH

        dialog = ActionSelectionDialog(actions_json_path=json_path, parent=self)
        if dialog.exec():
            selected = dialog.get_selected_action()
            if selected:
                label = selected.get("label", Translator.tr("new_action"))
                solo_nome = label.split(" (")[0]
                blocco = ActionBlockItem(title=solo_nome)

                # Costruzione dinamica dei parametri
                param_list = selected.get("params", [])
                blocco.build_from_params(param_list)

                self.sensor_canvas.add_sensor_block(blocco)

    def aggiungi_blocco_trigger(self):
        """
        @brief Opens the trigger selection dialog and adds the selected trigger block to the canvas.

        Parameters are set based on trigger metadata in the JSON file.
        """
        json_path = GlobalPaths.TRIGGERS_JSON_PATH

        dialog = TriggerSelectionDialog(triggers_json_path=json_path, parent=self)
        if dialog.exec():
            selected = dialog.get_selected_trigger()
            if selected:
                label = selected.get("label", Translator.tr("new_trigger"))
                solo_nome = label.split(" (")[0]
                blocco = TriggerBlockItem(title=solo_nome)

                param_list = selected.get("params", [])
                blocco.build_from_params(param_list)

                self.sensor_canvas.add_sensor_block(blocco)


    def aggiungi_blocco_condizione(self):
        """
        @brief Opens the condition selection dialog and adds the selected condition block to the canvas.

        Automatically builds input fields using metadata from the `conditions.json` file.
        """
        json_path = GlobalPaths.CONDITIONS_JSON_PATH

        dialog = ConditionSelectionDialog(conditions_json_path=json_path, parent=self)
        if dialog.exec():
            selected = dialog.get_selected_condition()
            if selected:
                label = selected.get("label", Translator.tr("new_condition"))
                solo_nome = label.split(" (")[0]
                blocco = ConditionBlockItem(title=solo_nome)

                param_list = selected.get("params", [])
                blocco.build_from_params(param_list)

                self.sensor_canvas.add_sensor_block(blocco)


    def aggiungi_blocco_timer(self):
        """
        @brief Opens the timer selection dialog and adds the selected timer block to the canvas.

        Populates block parameters using the associated JSON definition.
        """
        json_path = GlobalPaths.TIMERS_JSON_PATH

        dialog = TimerSelectionDialog(timers_json_path=json_path, parent=self)
        if dialog.exec():
            selected = dialog.get_selected_timer()
            if selected:
                label = selected.get("label", Translator.tr("new_timer"))
                solo_nome = label.split(" (")[0]
                blocco = TimerBlockItem(title=solo_nome)

                param_list = selected.get("params", [])
                blocco.build_from_params(param_list)

                self.sensor_canvas.add_sensor_block(blocco)


    def aggiungi_blocco_script(self):
        """
        @brief Opens the script selection dialog and adds the selected script block to the canvas.

        The block is customized based on the structure defined in `scripts.json`.
        """
        json_path = GlobalPaths.SCRIPTS_JSON_PATH

        dialog = ScriptSelectionDialog(scripts_json_path=json_path, parent=self)
        if dialog.exec():
            selected = dialog.get_selected_script()
            if selected:
                label = selected.get("label", Translator.tr("new_script"))
                solo_nome = label.split(" (")[0]
                blocco = ScriptBlockItem(title=solo_nome)

                param_list = selected.get("params", [])
                blocco.build_from_params(param_list)

                self.sensor_canvas.add_sensor_block(blocco)

