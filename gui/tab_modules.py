# -*- coding: utf-8 -*-
"""
@file tab_modules.py
@brief GUI tab managing ESPHome modules configuration.

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Provides an interface to enable, configure, and disable ESPHome modules
such as Logger, OTA, API, and others defined in the modules schema.

Loads module definitions from JSON, dynamically creates controls,
and synchronizes UI with YAML configuration.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QCheckBox, QComboBox, QPushButton, QScrollArea, QSpinBox, QMessageBox
from PyQt6.QtCore import Qt
import json
from .collapsible_section import CollapsibleSection
from gui.color_pantone import Pantone 
from core.translator import Translator
from core.log_handler import GeneralLogHandler as logger
from core.yaml_handler import YAMLHandler
from config.GUIconfig import conf

class TabModules(QWidget):
    """
    @brief Tab widget that manages ESPHome modules configuration through a dynamic form.

    Handles loading modules schema, populating UI widgets, reading from and writing to YAML,
    and tracking enabled/disabled states for modules.

    Supports user interaction to toggle module enablement and edit parameters.
    """
    def __init__(self, yaml_editor, logger=None, parent=None):
        """
        @brief Initializes the modules tab, loads schema, and builds UI components.

        Connects signals for handling user interaction and state changes.
        """
        super().__init__(parent)
        self.logger = logger

        # 1. Crea un container widget e il suo layout verticale
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        container_layout.setSpacing(8)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self.widget_map = {}
        self.sections_map = {}

        # 2. Aggiungi le sezioni accordion
        with open("config/modules_schema.json", encoding="utf-8") as f:
            modules_schema = json.load(f)

        for module_name, module_info in modules_schema.items():
            icon = module_info.get("icon", "")
            fields = module_info["fields"]
            content = QWidget()
            form = QFormLayout()
            form.setSpacing(4)
            form.setContentsMargins(8, 0, 8, 0)
            widget_dict = {}
            for field in fields:
                if field["type"] == "checkbox":
                    cb = QCheckBox(Translator.tr(field["label"]))
                    cb.setChecked(field.get("default", False))
                    cb.setStyleSheet(Pantone.CHECKBOX_STYLE)
                    form.addRow(cb)
                    widget_dict[field["key"]] = cb
                elif field["type"] == "combo":
                    combo = QComboBox()
                    combo.addItems([Translator.tr(opt) for opt in field["options"]])
                    combo.setCurrentText(field.get("default", ""))
                    combo.setStyleSheet(Pantone.COMBO_STYLE)
                    form.addRow(Translator.tr(field["label"]) + ":", combo)
                    widget_dict[field["key"]] = combo
                elif field["type"] == "text":
                    line = QLineEdit()
                    if field.get("is_password", False):
                        line.setEchoMode(QLineEdit.EchoMode.Password)
                    if field.get("placeholder"):
                        line.setPlaceholderText(field["placeholder"])
                    line.setText(field.get("default", ""))
                    line.setStyleSheet(Pantone.LINEEDIT_STYLE)
                    form.addRow(field["label"] + ":", line)
                    widget_dict[field["key"]] = line
                elif field["type"] == "int":
                    from PyQt6.QtWidgets import QSpinBox
                    spin = QSpinBox()
                    spin.setRange(field.get("min", 1), field.get("max", 3600))  # puoi gestire min/max nel json
                    spin.setValue(field.get("default", 1))
                    spin.setStyleSheet(Pantone.SPINBOX_STYLE)
                    form.addRow(field["label"] + ":", spin)
                    widget_dict[field["key"]] = spin            
            content.setLayout(form)
            content.setStyleSheet(Pantone.LABEL_STYLE)
            section = CollapsibleSection(Translator.tr(module_name), content, icon)
            container_layout.addWidget(section)
            self.widget_map[module_name] = widget_dict
            self.sections_map[module_name] = section

        # 3. Pulsante in fondo
        self.update_yaml_btn = QPushButton("🔁 " + Translator.tr("update_yaml"))
        self.update_yaml_btn.setStyleSheet(Pantone.UPDATE_YAML_BTN_STYLE)
        self.update_yaml_btn.clicked.connect(self.aggiorna_yaml_da_moduli)

        # 4. Crea la scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("background: transparent; border: none;")

        # 5. Aggiungi la scroll area al layout principale
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)

        # Contenitore per fissare il bottone in basso a destra
        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.addWidget(self.update_yaml_btn, alignment=Qt.AlignmentFlag.AlignRight)
        btn_layout.setContentsMargins(10, 10, 10, 10)

        layout.addWidget(btn_container, alignment=Qt.AlignmentFlag.AlignBottom)



    def _editor(self):
        """
        @brief Returns the YAML editor instance from the main window, if still valid.

        This method ensures that the YAML editor has not been destroyed or detached from the main window.
        It performs a parent chain check to avoid using destroyed widgets.

        @return QTextEdit pointer to the YAML editor or None if not available.
        """
        main = self.window()
        if hasattr(main, "yaml_editor"):
            return main.yaml_editor
        return None        


    def aggiorna_yaml_da_moduli(self):
        """
        @brief Updates the YAML content in the editor by reading the active module configurations.

        Extracts module values from the UI widgets (accordion form),
        generates a new YAML string using `YAMLHandler`, and replaces the current YAML in the editor.

        If the operation is successful, a success message is logged.
        On error, appropriate fallback logging is performed using the logger.

        @note This method assumes that the editor is valid and the schema file is available.
        """
        try:
            main = self.window()
            if not hasattr(main, "yaml_editor") or main.yaml_editor is None:
                return  # editor non disponibile

            editor = main.yaml_editor
            from core.yaml_handler import YAMLHandler
            modules_schema_path = conf.MODULE_SCHEMA_PATH
            current_yaml = editor.toPlainText()
            modules_dict = YAMLHandler.extract_module_sections_from_widgets(
                self.widget_map,
                modules_schema_path
            )
            new_yaml = YAMLHandler.generate_yaml_with_modules(
                current_yaml,
                modules_dict,
                modules_schema_path
            )
            editor.setPlainText(new_yaml)
            if self.logger:
                self.logger.log(Translator.tr("yaml_updated_from_modules"), "success")

        except RuntimeError as e:
            try:
                if hasattr(self, "logger"):
                    self.logger.log(f"❌ YAML update crash: {e}", "error")
                elif hasattr(main, "logger"):
                    main.logger.log(f"❌ YAML update crash: {e}", "error")
                else:
                    logger.error(f"[TabModules] YAML update crash: {e}")
            except Exception:
                pass  # Ultimo fallback



    def carica_dati_da_yaml(self, yaml_string):
        """
        @brief Loads and parses YAML content, updating the UI module widgets accordingly.

        For each module defined in the YAML, this method:
        - Enables the module section (checkbox)
        - Sets the correct values for fields like text, combo, checkbox, or spinbox

        If a module is not found in the YAML, its section remains disabled.

        @param yaml_string YAML configuration as a string to be parsed and reflected in the UI.
        """
        modules_schema_path = "config/modules_schema.json"
        modules_data = YAMLHandler.extract_modules_from_yaml(
            yaml_string,
            modules_schema_path
        )
        # Estrai i moduli PRESENTI nel file yaml (chiavi minuscole, underscore)
        import ruamel.yaml
        yaml = ruamel.yaml.YAML()
        data = yaml.load(yaml_string) or {}
        yaml_moduli_presenti = set(data.keys())

        for module_name, values in modules_data.items():
            widget_dict = self.widget_map.get(module_name, {})
            # Ricava la chiave yaml di questo modulo (debug, logger, ...)
            yaml_key = module_name.lower().replace(" ", "_")
            # --- GESTIONE CHECKBOX "ENABLED" ---
            enabled_checkbox = widget_dict.get("enabled")
            if isinstance(enabled_checkbox, QCheckBox):
                enabled_checkbox.setChecked(yaml_key in yaml_moduli_presenti)
            # --- Altri campi ---
            for key, val in values.items():
                widget = widget_dict.get(key)
                if widget is None or key == "enabled":
                    continue
                if isinstance(widget, QSpinBox):
                    if isinstance(val, str) and val.endswith("s"):
                        try:
                            val = int(val.rstrip("s"))
                        except Exception:
                            val = 1
                    try:
                        widget.setValue(int(val))
                    except Exception:
                        pass
                elif isinstance(widget, QLineEdit):
                    widget.setText(str(val))
                elif isinstance(widget, QComboBox):
                    idx = widget.findText(str(val))
                    if idx != -1:
                        widget.setCurrentIndex(idx)

    def reset_fields(self):
        """
        @brief Resets all module widgets in the UI to their default states.

        This includes:
        - Clearing text fields
        - Unchecking checkboxes
        - Resetting combo boxes to the first item
        - Setting spinboxes to their minimum value

        It does not modify or clear the YAML editor.
        """        
        for widget_dict in self.widget_map.values():
            for key, widget in widget_dict.items():
                if isinstance(widget, QLineEdit):
                    widget.clear()
                elif isinstance(widget, QCheckBox):
                    # di default, puoi mettere checked/unchecked (scegli tu)
                    widget.setChecked(False)
                elif isinstance(widget, QComboBox):
                    if widget.count() > 0:
                        widget.setCurrentIndex(0)
                elif isinstance(widget, QSpinBox):
                    widget.setValue(widget.minimum())


    def aggiorna_label(self):
        """
        @brief Updates all translatable UI labels within the Modules tab.

        This includes:
        - The "Update YAML" button
        - Titles of collapsible module sections
        - Field labels inside each module section
        - Placeholder texts where applicable

        The translations are pulled from the active language using `Translator.tr`.
        """        
        # Aggiorna il bottone "Aggiorna YAML"
        self.update_yaml_btn.setText("🔁 " + Translator.tr("update_yaml"))
        # Aggiorna ogni modulo accordion (header/campi)
        for module_name, widget_dict in self.widget_map.items():
            section = self.sections_map.get(module_name)
            if section:
                section.set_title(Translator.tr(module_name))
            # Aggiorna label dei campi dentro ciascun modulo
            for key, widget in widget_dict.items():
                if isinstance(widget, QCheckBox) or isinstance(widget, QLabel):
                    widget.setText(Translator.tr(key))
                elif isinstance(widget, QLineEdit):
                    if hasattr(widget, "setPlaceholderText"):
                        widget.setPlaceholderText(Translator.tr(key))
                elif isinstance(widget, QComboBox):
                    # Se vuoi aggiornare anche le opzioni della combo
                    pass
