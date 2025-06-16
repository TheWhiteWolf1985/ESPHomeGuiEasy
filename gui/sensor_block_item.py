"""
@file sensor_block_item.py
@brief Definisce un blocco sensore compatto e riducibile nel canvas.

Ogni blocco può essere espanso o collassato e contiene campi configurabili.
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
    @class SensorBlockItem
    @brief Blocco sensore riducibile con header e corpo configurabile.
    """
    def __init__(self, title="Nuovo Sensore"):
        super().__init__()
        self.width = conf.BLOCK_WIDTH
        self.height = conf.BLOCK_HEIGHT
        self.title = title
        self.expanded = True  # stato iniziale: espanso
        self.conn_type_display = None
        self.output_links = {}  # dizionario per tracciare le uscite collegate


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
        font = QFont("Consolas", 12, QFont.Weight.Bold)
        self.title_item.setFont(font)
        self.title_item.setDefaultTextColor(Qt.GlobalColor.white)
        self.title_item.setPos(10, 7)

        # Bottone chiusura (❌ -> icona close.png)
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

        # Bottone riduci/espandi (🔽 -> icona expand.png)
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

        # CONTENITORE DEL CORPO
        self.container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 30, 8, 8)

        # Tipo sensore (visualizzazione sola lettura)
        layout.addWidget(QLabel(Translator.tr("sensor_type")))
        self.conn_type_display = QLineEdit()
        self.conn_type_display.setReadOnly(True)
        self.conn_type_display.setStyleSheet("background-color: #2a2d2e; color: #d4d4d4; border: 1px solid #444; border-radius: 5px;")
        layout.addWidget(self.conn_type_display)

        # Nome sensore (fisso)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(Translator.tr("placeholder_sensor_name"))
        self.name_edit.textChanged.connect(self.update_title)
        layout.addWidget(QLabel(Translator.tr("sensor_name")))
        layout.addWidget(self.name_edit)

        self.container.setLayout(layout)
        self.container.setFixedWidth(self.width)

        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.container)
        self.proxy.setPos(0, 40)

        # # === FOOTER USCITE SEMPRE VISIBILE ===
        # self.footer = QWidget()
        # footer_layout = QVBoxLayout()
        # footer_layout.setContentsMargins(8, 4, 8, 8)
        # self.footer.setLayout(footer_layout)
        # self.footer.setFixedWidth(self.width)

        # self.footer_proxy = QGraphicsProxyWidget(self)
        # self.footer_proxy.setWidget(self.footer)
        # self.footer_proxy.setPos(0, self.height - 60)  # posizione approssimativa, puoi regolare

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
        @brief Mostra o nasconde il corpo del blocco e aggiorna l'icona.
        """
        self.expanded = not self.expanded
        self.container.setVisible(self.expanded)
        self.toggle_btn.setIcon(QIcon(os.path.join(conf.ICON_PATH, "expand.png")))
        self.prepareGeometryChange()
        self.update()                 # forza il repaint dell'item
        self.scene().update()

    def remove_from_scene(self):
        """
        @brief Rimuove il blocco dalla scena.
        """
        scene = self.scene()
        if scene:
            scene.removeItem(self)

    def boundingRect(self):
        height = self.height if self.expanded else conf.BLOCK_COLLAPSED_HEIGHT
        return QRectF(0, 0, self.width, height)  #+ self.footer.height()

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

    def build_from_params(self, param_list):
        """
        @brief Aggiunge dinamicamente i campi dal JSON al layout del blocco.
        @param param_list Lista di dizionari con i parametri (da sensors.json)
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

    def build_from_returns(self, return_list):
        """
        @brief Crea i collegamenti logici visibili per ogni valore restituito dal sensore.
        """
        footer_layout = self.footer.layout()
        for ret in return_list:
            rid = ret.get("id", "output")
            label = ret.get("label", rid)
            icon_label = QLabel("🔁")
            text_label = QLabel(label)
            combo = QComboBox()
            combo.addItem("Nessun collegamento")

            hbox = QHBoxLayout()
            hbox.addWidget(icon_label)
            hbox.addWidget(text_label)
            hbox.addWidget(combo)

            container = QWidget()
            container.setLayout(hbox)
            footer_layout.addWidget(container)

            self.output_links[rid] = combo  # salva per uso logico/serializzazione


