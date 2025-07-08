# -*- coding: utf-8 -*-
"""
@file sensor_block_item.py
@brief Defines a collapsible and expandable sensor block in the canvas.

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Represents a movable and selectable sensor block with configurable header and body,
including dynamic parameter and output widgets.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsTextItem, QGraphicsProxyWidget,
    QComboBox, QLineEdit, QSpinBox, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout
)
from PyQt6.QtGui import QBrush, QPen, QColor, QFont, QIcon
from PyQt6.QtCore import QRectF, Qt, QSize
from core.translator import Translator
import config.GUIconfig as conf
import os


class SensorBlockItem(QGraphicsItem):
    """
    @brief A collapsible sensor block with header and configurable body.

    Supports dynamic UI generation from sensor parameters and outputs,
    handles expand/collapse, and updates title dynamically based on sensor name.
    """
    def __init__(self, title="Nuovo Sensore"):
        super().__init__()
        self.width = conf.BLOCK_WIDTH
        self.height = conf.BLOCK_HEIGHT
        self.title = title
        self.expanded = True  # stato iniziale: espanso
        self.conn_type_display = None
        self.output_links = {}  # dizionario per tracciare le uscite collegate
        self.required_fields = {}


        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )

        self.setup_ui()

    def setup_ui(self):
        """
        @brief Initializes the UI with a header and configurable body.

        Creates title label, close and toggle buttons, and parameter containers,
        including sensor type display and name input.
        """
        # HEADER: titolo
        self.title_item = QGraphicsTextItem(self.title, self)
        font = QFont("Consolas", 12, QFont.Weight.Bold)
        self.title_item.setFont(font)
        self.title_item.setDefaultTextColor(Qt.GlobalColor.white)
        self.title_item.setPos(10, 7)

        # Bottone chiusura
        self.close_btn = QPushButton()
        self.close_btn.setIcon(QIcon(os.path.join(conf.ICON_PATH, "close.png")))
        self.close_btn.setIconSize(QSize(22, 22))
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5f56;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #ff2d20;
            }
        """)
        self.close_btn.clicked.connect(self.remove_from_scene)

        self.close_proxy = QGraphicsProxyWidget(self)
        self.close_proxy.setWidget(self.close_btn)
        self.close_proxy.setPos(self.width - 35, 8)

        # Bottone espandi/riduci
        self.toggle_btn = QPushButton()
        self.toggle_btn.setIcon(QIcon(os.path.join(conf.ICON_PATH, "expand.png")))
        self.toggle_btn.setIconSize(QSize(22, 22))
        self.toggle_btn.setFixedSize(25, 25)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a9dda;
                border: none;
                border-radius: 11px;
            }
            QPushButton:hover {
                background-color: #2277aa;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_expand)

        self.toggle_proxy = QGraphicsProxyWidget(self)
        self.toggle_proxy.setWidget(self.toggle_btn)
        self.toggle_proxy.setPos(self.width - 74, 8)

        # CONTENITORE COMPLETO DEL BLOCCO (parametri + outputs)
        self.container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 30, 8, 8)

        # Tipo sensore (solo lettura)
        layout.addWidget(QLabel(Translator.tr("sensor_type")))
        self.conn_type_display = QLineEdit()
        self.conn_type_display.setReadOnly(True)
        self.conn_type_display.setStyleSheet("background-color: #2a2d2e; color: #d4d4d4; border: 1px solid #444; border-radius: 5px;")
        layout.addWidget(self.conn_type_display)

        # Nome sensore
        layout.addWidget(QLabel(Translator.tr("sensor_name")))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(Translator.tr("placeholder_sensor_name"))
        self.name_edit.textChanged.connect(self.update_title)
        layout.addWidget(self.name_edit)

        self.container.setLayout(layout)
        self.container.setFixedWidth(self.width)

        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.container)
        self.proxy.setPos(0, 40)

    def update_title(self, text):
        """
        @brief Updates the block title text based on the sensor name field.

        If empty, sets a default placeholder title.
        """
        if text.strip():
            self.title_item.setPlainText(text)
        else:
            self.title_item.setPlainText(Translator.tr("new_sensor"))

    def toggle_expand(self):
        """
        @brief Shows or hides the block body and updates the toggle icon accordingly.
        """
        self.expanded = not self.expanded
        self.container.setVisible(self.expanded)
        self.toggle_btn.setIcon(QIcon(os.path.join(conf.ICON_PATH, "expand.png")))
        self.prepareGeometryChange()
        self.update()                 # forza il repaint dell'item
        self.scene().update()

    def remove_from_scene(self):
        """
        @brief Removes the block from the QGraphicsScene.
        """
        scene = self.scene()
        if scene:
            scene.removeItem(self)

    def boundingRect(self):
        """
        @brief Returns the bounding rectangle of the block.

        Considers whether the block is expanded or collapsed for height calculation.
        """
        if self.expanded:
            content_height = self.container.sizeHint().height()
        else:
            content_height = conf.BLOCK_COLLAPSED_HEIGHT

        return QRectF(0, 0, self.width, content_height + 40)

    def paint(self, painter, option, widget=None):
        """
        @brief Paints the block with a blue background and black border.
        """
        painter.setBrush(QBrush(QColor("#3c8dbc")))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        height = int(self.boundingRect().height())
        painter.drawRoundedRect(0, 0, self.width, height, 10, 10)

    def aggiorna_label(self):
        """
        @brief Updates labels and placeholders of UI fields to the current language.
        """
        # Cambia label dei campi
        self.container.layout().itemAt(0).widget().setText(Translator.tr("sensor_type"))
        self.container.layout().itemAt(2).widget().setText(Translator.tr("sensor_name"))
        self.container.layout().itemAt(4).widget().setText(Translator.tr("sensor_pin"))
        self.container.layout().itemAt(6).widget().setText(Translator.tr("sensor_update_interval"))
        # Placeholder dei campi
        self.name_edit.setPlaceholderText(Translator.tr("placeholder_sensor_name"))
        self.pin_edit.setPlaceholderText(Translator.tr("placeholder_sensor_pin"))

    def build_from_params(self, param_list):
        """
        @brief Dynamically adds parameter input fields to the block based on sensor JSON.

        @param param_list List of parameter dictionaries from sensors.json.
        """
        self.param_widgets = {}

        layout = self.container.layout()
        layout.addSpacing(10)

        for param in param_list:
            key = param.get("key")
            tipo = param.get("type")
            label_text = param.get("label", key)
            default = param.get("default", "")
            required = param.get("required", False)

            label = QLabel(label_text)
            layout.addWidget(label)

            if tipo == "text":
                field = QLineEdit()
                field.setPlaceholderText(param.get("placeholder", ""))
                field.setText(str(default))
                layout.addWidget(field)

            elif tipo == "int":
                field = QSpinBox()
                field.setMinimum(0)
                field.setMaximum(100000)
                if isinstance(default, int):
                    field.setValue(default)
                layout.addWidget(field)

            elif tipo == "combo":
                field = QComboBox()
                options = param.get("options", [])
                field.addItems(options)
                if default in options:
                    field.setCurrentText(default)
                layout.addWidget(field)

            else:
                continue  # Tipo non gestito (può essere esteso)

            self.param_widgets[key] = field  # Salva il riferimento
            self.required_fields[key] = required

    def build_from_returns(self, return_list):
        """
        @brief Creates output fields for the sensor with customizable names.

        @param return_list List of output dictionaries defining keys and labels.
        """
        if not return_list:
            return

        layout = self.container.layout()
        self.output_links = {}

        for ret in return_list:
            rid = ret.get("key", "output")
            label = ret.get("name", rid)

            name_edit = QLineEdit()
            name_edit.setPlaceholderText(f"{label} name")
            name_edit.setStyleSheet("background-color: #2a2d2e; color: #d4d4d4; border: 1px solid #444; border-radius: 5px;")

            hbox = QHBoxLayout()
            hbox.addWidget(QLabel("🔁"))
            hbox.addWidget(QLabel(label))
            hbox.addWidget(name_edit)

            container = QWidget()
            container.setLayout(hbox)
            layout.addWidget(container)

            self.output_links[rid] = name_edit  # ora è un QLineEdit per nome output

    def has_valid_data(self) -> bool:
        """
        @brief Checks that all required fields are filled in.

        Highlights missing fields in red.

        @return True if all required data is valid, False otherwise.
        """
        valid = True

        for key, widget in self.param_widgets.items():
            is_required = self.required_fields.get(key, False)

            value = None
            if isinstance(widget, QLineEdit):
                value = widget.text().strip()
            elif isinstance(widget, QComboBox):
                value = widget.currentText().strip()
            elif isinstance(widget, QSpinBox):
                value = widget.value()

            is_invalid = (
                is_required and (value in ["", None] or (isinstance(value, int) and value == 0))
            )

            # Colora in rosso se mancante, altrimenti stile normale
            if is_invalid:
                widget.setStyleSheet("background-color: #ffcccc; color: #000; border: 1px solid #a00; border-radius: 4px;")
                valid = False
            else:
                # Reset stile (stile scuro coerente)
                widget.setStyleSheet("background-color: #2a2d2e; color: #d4d4d4; border: 1px solid #444; border-radius: 5px;")

        return valid







