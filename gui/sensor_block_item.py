"""
@file sensor_block_item.py
@brief Definisce un blocco sensore compatto e riducibile nel canvas.

Ogni blocco può essere espanso o collassato e contiene campi configurabili.
"""

from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsTextItem, QGraphicsProxyWidget,
    QComboBox, QLineEdit, QSpinBox, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout
)
from PyQt6.QtGui import QBrush, QPen, QColor, QFont
from PyQt6.QtCore import QRectF, Qt
from core.translator import Translator


class SensorBlockItem(QGraphicsItem):
    """
    @class SensorBlockItem
    @brief Blocco sensore riducibile con header e corpo configurabile.
    """
    def __init__(self, title="Nuovo Sensore", width=200, height=200):
        super().__init__()
        self.width = width
        self.height = height
        self.title = title
        self.expanded = True  # stato iniziale: espanso

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )

        self.setup_ui()

    def setup_ui(self):
        """
        @brief Inizializza UI con header e corpo configurabile.
        """
        # HEADER: titolo
        self.title_item = QGraphicsTextItem(self.title, self)
        font = QFont("Consolas", 10, QFont.Weight.Bold)
        self.title_item.setFont(font)
        self.title_item.setDefaultTextColor(Qt.GlobalColor.white)
        self.title_item.setPos(10, 5)

        # Bottone chiusura
        self.close_btn = QPushButton("❌")
        self.close_btn.setFixedSize(22, 22)
        self.close_btn.setStyleSheet("QPushButton { background-color: #ff5f56; color: white; border: none; border-radius: 11px; }"
                                     "QPushButton:hover { background-color: #ff2d20; }")
        self.close_btn.clicked.connect(self.remove_from_scene)

        self.close_proxy = QGraphicsProxyWidget(self)
        self.close_proxy.setWidget(self.close_btn)
        self.close_proxy.setPos(self.width - 28, 4)

        # Bottone riduci/espandi
        self.toggle_btn = QPushButton("🔽")
        self.toggle_btn.setFixedSize(22, 22)
        self.toggle_btn.setStyleSheet("QPushButton { background-color: #3a9dda; color: white; border: none; border-radius: 11px; }"
                                      "QPushButton:hover { background-color: #2277aa; }")
        self.toggle_btn.clicked.connect(self.toggle_expand)

        self.toggle_proxy = QGraphicsProxyWidget(self)
        self.toggle_proxy.setWidget(self.toggle_btn)
        self.toggle_proxy.setPos(self.width - 54, 4)

        # CONTENITORE DEL CORPO
        self.container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 30, 8, 8)

        # Tipo sensore
        self.type_combo = QComboBox()
        self.type_combo.addItems(["DHT11", "DHT22", "GPIO", "Analogico"])
        layout.addWidget(QLabel(Translator.tr("sensor_type")))
        layout.addWidget(self.type_combo)

        # Nome sensore
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(Translator.tr("placeholder_sensor_name"))
        self.name_edit.textChanged.connect(self.update_title)
        layout.addWidget(QLabel(Translator.tr("sensor_name")))
        layout.addWidget(self.name_edit)

        # Pin
        self.pin_edit = QLineEdit()
        self.pin_edit.setPlaceholderText(Translator.tr("placeholder_sensor_pin"))
        layout.addWidget(QLabel(Translator.tr("sensor_pin")))
        layout.addWidget(self.pin_edit)

        # Update interval
        self.update_spin = QSpinBox()
        self.update_spin.setMinimum(1)
        self.update_spin.setMaximum(3600)
        self.update_spin.setSuffix(" s")
        layout.addWidget(QLabel(Translator.tr("sensor_update_interval")))
        layout.addWidget(self.update_spin)

        self.container.setLayout(layout)

        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.container)
        self.proxy.setPos(0, 30)

    def update_title(self, text):
        """
        @brief Aggiorna il titolo del blocco in base al campo nome.
        """
        if text.strip():
            self.title_item.setPlainText(text)
        else:
            self.title_item.setPlainText(Translator.tr("new_sensor"))

    def toggle_expand(self):
        """
        @brief Mostra o nasconde il corpo del blocco.
        """
        self.expanded = not self.expanded
        self.container.setVisible(self.expanded)
        self.toggle_btn.setText("🔽" if self.expanded else "🔼")

    def remove_from_scene(self):
        """
        @brief Rimuove il blocco dalla scena.
        """
        scene = self.scene()
        if scene:
            scene.removeItem(self)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height if self.expanded else 40)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(QColor("#3c8dbc")))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        height = int(self.boundingRect().height())
        painter.drawRoundedRect(0, 0, self.width, height, 10, 10)

    def aggiorna_label(self):
        from core.translator import Translator
        # Cambia label dei campi
        self.container.layout().itemAt(0).widget().setText(Translator.tr("sensor_type"))
        self.container.layout().itemAt(2).widget().setText(Translator.tr("sensor_name"))
        self.container.layout().itemAt(4).widget().setText(Translator.tr("sensor_pin"))
        self.container.layout().itemAt(6).widget().setText(Translator.tr("sensor_update_interval"))
        # Placeholder dei campi
        self.name_edit.setPlaceholderText(Translator.tr("placeholder_sensor_name"))
        self.pin_edit.setPlaceholderText(Translator.tr("placeholder_sensor_pin"))
