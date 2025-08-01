
# -*- coding: utf-8 -*-
"""
@file timer_block_item.py
@brief Expandable canvas block (purple) for ESPHome timer/interval configuration.

@defgroup canvas_blocks Visual Blocks
@ingroup gui
@brief Visual representation of a timer block within the ESPHomeGuiEasy canvas system.

This module defines a draggable and expandable block used in the canvas to represent
a `timer:` or `interval:` trigger. The block dynamically builds its UI from metadata.

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
from config.GUIconfig import conf, UIDimensions, GlobalPaths
import os


class TimerBlockItem(QGraphicsItem):
    """
    @brief Visual block representing an ESPHome `timer:` or `interval:` trigger.

    This QGraphicsItem subclass implements a canvas block that is:
    - Expandable/collapsible
    - Movable and selectable
    - Automatically built from parameter metadata

    The block uses violet color and includes a close button and an expand/collapse toggle.

    @note Parameters are rendered using PyQt6 widgets inside a QGraphicsProxyWidget container.
    """    
    def __init__(self, title="Timer/Interval"):
        super().__init__()
        """
        @brief Initializes the timer block with title and layout.

        Sets dimensions, flags, and prepares the internal layout including:
        - Title label
        - Expand/collapse button
        - Close (delete) button
        - Parameter container (initially empty)

        @param title Display title of the block (defaults to "Timer/Interval").
        """        
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
        @brief Builds the static visual structure of the block.

        Adds:
        - Title label (top-left)
        - Close button (top-right)
        - Expand/collapse button
        - Widget container for parameter input fields

        Called once during initialization.
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
                background-color: #9b59b6;
                border: none;
                border-radius: 11px;
            }
            QPushButton:hover {
                background-color: #7d3c98;
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
        @brief Toggles the expanded/collapsed state of the block.

        Hides or shows the parameter container and updates the expand icon.

        Also triggers a geometry update to the canvas scene.
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
        @brief Builds the parameter input fields dynamically from a metadata list.

        Accepts a list of dictionaries containing:
        - key: unique parameter identifier
        - type: one of ["text", "int", "combo"]
        - label: field label
        - default: default value
        - options (if combo): available items

        Supported widget types:
        - QLineEdit for text
        - QSpinBox for int
        - QComboBox for combo

        @param param_list List of parameter definitions in dictionary format.
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
        @brief Returns the bounding rectangle of the block item.

        Adjusts the height depending on whether the block is expanded or collapsed.

        @return QRectF representing the visual bounds of the item.
        """        
        return QRectF(0, 0, self.width, self.height if self.expanded else UIDimensions.BLOCK_COLLAPSED_HEIGHT)

    def paint(self, painter, option, widget=None):
        """
        @brief Custom painting method for the block background and border.

        Paints a rounded rectangle in violet with a black border.

        @param painter QPainter instance
        @param option Style options
        @param widget Optional widget context
        """        
        painter.setBrush(QBrush(QColor("#9b59b6")))  # Viola
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        height = int(self.boundingRect().height())
        painter.drawRoundedRect(0, 0, self.width, height, 10, 10)

    def remove_from_scene(self):
        """
        @brief Removes the block from the current scene.

        Called when the close (delete) button is clicked.
        """        
        scene = self.scene()
        if scene:
            scene.removeItem(self)
