from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QCheckBox, QComboBox
from PyQt6.QtCore import Qt
import json
from .collapsible_section import CollapsibleSection
from gui.color_pantone import Pantone 

class TabModules(QWidget):
   def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget_map = {}  # {modulo: {key: widget}}
        # Carica lo schema
        with open("config/modules_schema.json", encoding="utf-8") as f:
            modules_schema = json.load(f)
        # Per ogni modulo del json
        for module_name, module_info in modules_schema.items():
            icon = module_info.get("icon", "")
            fields = module_info["fields"]
            # Crea il widget interno
            content = QWidget()
            form = QFormLayout()
            form.setSpacing(4)
            form.setContentsMargins(8, 0, 8, 0)
            widget_dict = {}
            for field in fields:
                # Genera il widget giusto in base al tipo
                if field["type"] == "checkbox":
                    cb = QCheckBox(field["label"])
                    cb.setChecked(field.get("default", False))
                    cb.setStyleSheet(Pantone.CHECKBOX_STYLE)
                    form.addRow(cb)
                    widget_dict[field["key"]] = cb
                elif field["type"] == "combo":
                    combo = QComboBox()
                    combo.addItems(field["options"])
                    combo.setCurrentText(field.get("default", ""))
                    combo.setStyleSheet(Pantone.COMBO_STYLE)
                    form.addRow(field["label"] + ":", combo)
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
            content.setLayout(form)
            content.setStyleSheet(Pantone.LABEL_STYLE)
            section = CollapsibleSection(module_name, content, icon)
            layout.addWidget(section)
            self.widget_map[module_name] = widget_dict
