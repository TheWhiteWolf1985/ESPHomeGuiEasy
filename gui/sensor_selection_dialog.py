from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
    QDialogButtonBox, QLabel, QHBoxLayout, QComboBox, QSpinBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from gui.color_pantone import Pantone
import os, json


class SensorSelectionDialog(QDialog):
    def __init__(self, sensors_json_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleziona Sensore")
        self.setMinimumSize(400, 500)
        self.selected_sensor = None

        self.setStyleSheet(Pantone.DIALOG_STYLE)

        self.sensors = self.load_sensors(sensors_json_path)

        layout = QVBoxLayout(self)

        # Filtro di ricerca
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cerca sensore...")
        self.search_bar.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_bar)

        # Lista sensori
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(Pantone.LISTWIDGET_STYLE)
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)

        # Bottoni OK / Annulla
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept_selection)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.populate_list()

    def load_sensors(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("sensors", [])
        except Exception as e:
            print(f"Errore nel caricamento dei sensori: {e}")
            return []

    def populate_list(self):
        self.list_widget.clear()
        for sensor in self.sensors:
            label = sensor.get("label", "Sconosciuto")
            platform = sensor.get("platform", "?")
            conn_type = self.detect_connection_type(sensor)
            item = QListWidgetItem(QIcon(self.get_icon_path(platform)), f"{label} ({conn_type})")
            item.setData(Qt.ItemDataRole.UserRole, sensor)
            self.list_widget.addItem(item)

    def detect_connection_type(self, sensor):
        # Determina la connessione in base ai parametri
        keys = [p["key"] for p in sensor.get("params", [])]
        if any("i2c" in k.lower() for k in keys):
            return "I2C"
        elif "analog" in sensor.get("label", "").lower():
            return "Analogico"
        elif "gpio" in sensor.get("platform", "").lower():
            return "Digitale"
        return "Sconosciuto"

    def get_icon_path(self, platform):
        # Supponiamo di avere le icone in assets/icons/{platform}.png
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir, "..", "assets", "icons", f"{platform.lower()}.png")
        if os.path.exists(icon_path):
            return icon_path
        return os.path.join(base_dir, "..", "assets", "icons", "default.png")

    def filter_list(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def accept_selection(self):
        item = self.list_widget.currentItem()
        if item:
            self.selected_sensor = item.data(Qt.ItemDataRole.UserRole)
            self.accept()

    def get_selected_sensor(self):
        return self.selected_sensor
