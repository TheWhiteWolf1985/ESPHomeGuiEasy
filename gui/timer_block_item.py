
"""
@file timer_block_item.py
@brief Blocco timer/interval (viola) espandibile per il canvas.
"""

from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsTextItem, QGraphicsProxyWidget,
    QComboBox, QLineEdit, QSpinBox, QPushButton, QLabel, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QBrush, QPen, QColor, QFont, QIcon
from PyQt6.QtCore import QRectF, Qt, QSize
from core.translator import Translator
import config.GUIconfig as conf
import os


class TimerBlockItem(QGraphicsItem):
    def __init__(self, title="Timer/Interval"):
        super().__init__()
        self.width = conf.BLOCK_WIDTH
        self.height = conf.BLOCK_HEIGHT
        self.title = title
        self.expanded = True
        self.param_widgets = {}

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )

        self.setup_ui()

    def setup_ui(self):
        self.title_item = QGraphicsTextItem(self.title, self)
        font = QFont("Consolas", 12, QFont.Weight.Bold)
        self.title_item.setFont(font)
        self.title_item.setDefaultTextColor(Qt.GlobalColor.white)
        self.title_item.setPos(10, 7)

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

        self.toggle_btn = QPushButton()
        self.toggle_btn.setIcon(QIcon(os.path.join(conf.ICON_PATH, "expand.png")))
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
        self.expanded = not self.expanded
        self.container.setVisible(self.expanded)
        self.toggle_btn.setIcon(QIcon(os.path.join(conf.ICON_PATH, "expand.png")))
        self.prepareGeometryChange()
        self.update()
        if self.scene():
            self.scene().update()

    def build_from_params(self, param_list):
        layout = self.container.layout()
        for param in param_list:
            key = param.get("key")
            tipo = param.get("type")
            label_text = param.get("label", key)
            default = param.get("default", "")

            label = QLabel(label_text)
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
        return QRectF(0, 0, self.width, self.height if self.expanded else conf.BLOCK_COLLAPSED_HEIGHT)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(QColor("#9b59b6")))  # Viola
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        height = int(self.boundingRect().height())
        painter.drawRoundedRect(0, 0, self.width, height, 10, 10)

    def remove_from_scene(self):
        scene = self.scene()
        if scene:
            scene.removeItem(self)
