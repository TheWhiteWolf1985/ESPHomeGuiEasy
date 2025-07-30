
# -*- coding: utf-8 -*-
"""
@file trigger_block_item.py
@brief Expandable canvas block (green) for ESPHome trigger logic.

@defgroup canvas_blocks Visual Blocks
@ingroup gui
@brief Visual representation of a trigger block in the ESPHomeGuiEasy canvas.

This module implements a draggable, expandable QGraphicsItem representing a
`trigger:` block (e.g. `on_press`, `on_boot`, `on_time`) in ESPHome YAML.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""
from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsTextItem, QGraphicsProxyWidget,
    QComboBox, QLineEdit, QSpinBox, QPushButton, QLabel, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QBrush, QPen, QColor, QFont, QIcon
from PyQt6.QtCore import QRectF, Qt, QSize
from core.translator import Translator
from config.GUIconfig import conf, GlobalPaths, UIDimensions
import os


class TriggerBlockItem(QGraphicsItem):
    """
    @brief Canvas block representing a trigger section in ESPHome.

    This class defines a green visual block with expandable parameter area.
    Parameters are loaded from JSON and rendered as widgets dynamically.

    Includes:
    - Title
    - Expand/Collapse toggle
    - Close button
    - Parameter widgets (text, int, combo)

    @note Used inside a QGraphicsScene for visual logic configuration.
    """    
    def __init__(self, title="Trigger"):
        """
        @brief Constructor initializing layout, title and buttons.

        Prepares graphical flags, default dimensions, and invokes setup_ui.

        @param title Displayed block title (default: "Trigger").
        """        
        super().__init__()
        self.width = UIDimensions.BLOCK_WIDTH
        self.height = UIDimensions.BLOCK_HEIGHT
        self.title = title
        self.expanded = True
        self.param_widgets = {}

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )

        self.setup_ui()

    def setup_ui(self):
        """
        @brief Creates the block layout: title, buttons, and parameter container.

        This method adds:
        - Title text
        - Close button (top right)
        - Expand/collapse button (toggles visibility of parameters)
        - Container for dynamic parameters

        @note Widgets are wrapped in QGraphicsProxyWidgets.
        """        
        self.title_item = QGraphicsTextItem(self.title, self)
        font = QFont("Consolas", 12, QFont.Weight.Bold)
        self.title_item.setFont(font)
        self.title_item.setDefaultTextColor(Qt.GlobalColor.white)
        self.title_item.setPos(10, 7)

        self.close_btn = QPushButton()
        self.close_btn.setIcon(QIcon(os.path.join(GlobalPaths.ICON_PATH, "close.png")))
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

        self.toggle_btn = QPushButton()
        self.toggle_btn.setIcon(QIcon(os.path.join(GlobalPaths.ICON_PATH, "expand.png")))
        self.toggle_btn.setIconSize(QSize(22, 22))
        self.toggle_btn.setFixedSize(25, 25)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #3cb44b;
                border: none;
                border-radius: 11px;
            }
            QPushButton:hover {
                background-color: #2d8e39;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_expand)

        self.toggle_proxy = QGraphicsProxyWidget(self)
        self.toggle_proxy.setWidget(self.toggle_btn)
        self.toggle_proxy.setPos(self.width - 74, 8)

        self.container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 40, 8, 8)
        self.container.setLayout(layout)
        self.container.setFixedWidth(self.width)

        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.container)
        self.proxy.setPos(0, 40)

    def toggle_expand(self):
        """
        @brief Switches the block between expanded and collapsed mode.

        Hides or shows the parameter area and updates the expand button icon.
        """        
        self.expanded = not self.expanded
        self.container.setVisible(self.expanded)
        self.toggle_btn.setIcon(QIcon(os.path.join(GlobalPaths.ICON_PATH, "expand.png")))
        self.prepareGeometryChange()
        self.update()
        if self.scene():
            self.scene().update()

    def build_from_params(self, param_list):
        """
        @brief Dynamically builds input widgets from a parameter metadata list.

        Accepts a list of dicts defining:
        - key: parameter identifier
        - type: one of ["text", "int", "combo"]
        - label: field label
        - default: default value
        - options (if combo): list of items

        Creates corresponding PyQt6 widgets and adds them to the block layout.

        @param param_list List of parameter dictionaries.
        """        
        layout = self.container.layout()
        for param in param_list:
            key = param.get("key")
            tipo = param.get("type")
            label_text = param.get("label", key)
            default = param.get("default", "")

            label = QLabel(Translator.tr(label_text))
            layout.addWidget(label)

            if tipo == "text":
                field = QLineEdit()
                field.setPlaceholderText(param.get("placeholder", ""))
                field.setText(str(default))
            elif tipo == "int":
                field = QSpinBox()
                field.setMinimum(0)
                field.setMaximum(100000)
                if isinstance(default, int):
                    field.setValue(default)
            elif tipo == "combo":
                field = QComboBox()
                options = param.get("options", [])
                field.addItems(options)
                if default in options:
                    field.setCurrentText(default)
            else:
                continue

            layout.addWidget(field)
            self.param_widgets[key] = field

    def boundingRect(self):
        """
        @brief Returns the bounding rectangle of the block.

        Height depends on whether the block is expanded or collapsed.

        @return QRectF with width and height.
        """        
        return QRectF(0, 0, self.width, self.height if self.expanded else UIDimensions.BLOCK_COLLAPSED_HEIGHT)

    def paint(self, painter, option, widget=None):
        """
        @brief Custom rendering of the block background and borders.

        Paints a rounded rectangle in green with black outline.

        @param painter QPainter instance
        @param option QStyleOptionGraphicsItem options
        @param widget Optional widget
        """        
        painter.setBrush(QBrush(QColor("#3cb44b")))  # Verde
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        height = int(self.boundingRect().height())
        painter.drawRoundedRect(0, 0, self.width, height, 10, 10)

    def remove_from_scene(self):
        """
        @brief Removes this block from the canvas scene.

        Called when the close button is pressed.
        """        
        scene = self.scene()
        if scene:
            scene.removeItem(self)
