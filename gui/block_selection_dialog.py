# -*- coding: utf-8 -*-
"""
@file block_selection_dialog.py
@brief Dialogs for selecting sensors, actions, triggers, conditions, timers, and scripts.

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Provides multiple QDialog classes each for selecting a specific block type from JSON data,  
including search/filter functionality and icon display.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
    QDialogButtonBox, QLabel, QHBoxLayout, QComboBox, QSpinBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from gui.color_pantone import Pantone
import os, json
from core.log_handler import GeneralLogHandler as logger

class SensorSelectionDialog(QDialog):
    """
    @brief Dialog window for selecting a sensor from the sensors JSON list.

    Supports search filtering and double-click/OK selection.
    """
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
            logger.error(f"Errore nel caricamento dei sensori: {e}")
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


class ActionSelectionDialog(QDialog):
    """
    @brief Dialog window for selecting an action from the actions JSON list.

    Supports search filtering and double-click/OK selection.
    """
    def __init__(self, actions_json_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleziona Azione")
        self.setMinimumSize(400, 500)
        self.selected_action = None

        self.setStyleSheet(Pantone.DIALOG_STYLE)
        self.actions = self.load_actions(actions_json_path)

        layout = QVBoxLayout(self)

        # Ricerca
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cerca azione...")
        self.search_bar.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_bar)

        # Lista
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(Pantone.LISTWIDGET_STYLE)
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)

        # Bottoni
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept_selection)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.populate_list()

    def load_actions(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("actions", [])
        except Exception as e:
            logger.error(f"Errore nel caricamento delle azioni: {e}")
            return []

    def populate_list(self):
        self.list_widget.clear()
        for action in self.actions:
            label = action.get("label", "Sconosciuta")
            tipo = action.get("type", "?")
            item = QListWidgetItem(QIcon(self.get_icon_path(tipo)), f"{label} ({tipo})")
            item.setData(Qt.ItemDataRole.UserRole, action)
            self.list_widget.addItem(item)

    def get_icon_path(self, tipo):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        platform = tipo.split(".")[0]
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
            self.selected_action = item.data(Qt.ItemDataRole.UserRole)
            self.accept()

    def get_selected_action(self):
        return self.selected_action

class TriggerSelectionDialog(QDialog):
    """
    @brief Dialog window for selecting a trigger from the triggers JSON list.

    Supports search filtering and double-click/OK selection.
    """
    def __init__(self, triggers_json_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleziona Trigger")
        self.setMinimumSize(400, 500)
        self.selected_trigger = None

        self.setStyleSheet(Pantone.DIALOG_STYLE)
        self.triggers = self.load_triggers(triggers_json_path)

        layout = QVBoxLayout(self)

        # Ricerca
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cerca trigger...")
        self.search_bar.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_bar)

        # Lista
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(Pantone.LISTWIDGET_STYLE)
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)

        # Bottoni
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept_selection)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.populate_list()

    def load_triggers(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("triggers", [])
        except Exception as e:
            logger.error(f"Errore nel caricamento dei trigger: {e}")
            return []

    def populate_list(self):
        self.list_widget.clear()
        for trigger in self.triggers:
            label = trigger.get("label", "Sconosciuto")
            tipo = trigger.get("type", "?")
            item = QListWidgetItem(QIcon(self.get_icon_path(tipo)), f"{label} ({tipo})")
            item.setData(Qt.ItemDataRole.UserRole, trigger)
            self.list_widget.addItem(item)

    def get_icon_path(self, tipo):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        source = tipo.split(".")[0]
        icon_path = os.path.join(base_dir, "..", "assets", "icons", f"{source.lower()}.png")
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
            self.selected_trigger = item.data(Qt.ItemDataRole.UserRole)
            self.accept()

    def get_selected_trigger(self):
        return self.selected_trigger

class ConditionSelectionDialog(QDialog):
    """
    @brief Dialog window for selecting a condition from the conditions JSON list.

    Supports search filtering and double-click/OK selection.
    """
    def __init__(self, conditions_json_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleziona Condizione")
        self.setMinimumSize(400, 500)
        self.selected_condition = None

        self.setStyleSheet(Pantone.DIALOG_STYLE)
        self.conditions = self.load_conditions(conditions_json_path)

        layout = QVBoxLayout(self)

        # Ricerca
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cerca condizione...")
        self.search_bar.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_bar)

        # Lista
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(Pantone.LISTWIDGET_STYLE)
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)

        # Bottoni
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept_selection)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.populate_list()

    def load_conditions(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("conditions", [])
        except Exception as e:
            logger.error(f"Errore nel caricamento delle condizioni: {e}")
            return []

    def populate_list(self):
        self.list_widget.clear()
        for condition in self.conditions:
            label = condition.get("label", "Sconosciuta")
            tipo = condition.get("type", "?")
            item = QListWidgetItem(QIcon(self.get_icon_path(tipo)), f"{label} ({tipo})")
            item.setData(Qt.ItemDataRole.UserRole, condition)
            self.list_widget.addItem(item)

    def get_icon_path(self, tipo):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        source = tipo.split(".")[0]
        icon_path = os.path.join(base_dir, "..", "assets", "icons", f"{source.lower()}.png")
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
            self.selected_condition = item.data(Qt.ItemDataRole.UserRole)
            self.accept()

    def get_selected_condition(self):
        return self.selected_condition

class TimerSelectionDialog(QDialog):
    """
    @brief Dialog window for selecting a timer or interval from the timers JSON list.

    Supports search filtering and double-click/OK selection.
    """
    def __init__(self, timers_json_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleziona Timer / Interval")
        self.setMinimumSize(400, 500)
        self.selected_timer = None

        self.setStyleSheet(Pantone.DIALOG_STYLE)
        self.timers = self.load_timers(timers_json_path)

        layout = QVBoxLayout(self)

        # Ricerca
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cerca intervallo...")
        self.search_bar.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_bar)

        # Lista
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(Pantone.LISTWIDGET_STYLE)
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)

        # Bottoni
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept_selection)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.populate_list()

    def load_timers(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("timers", [])
        except Exception as e:
            logger.error(f"Errore nel caricamento dei timer: {e}")
            return []

    def populate_list(self):
        self.list_widget.clear()
        for timer in self.timers:
            label = timer.get("label", "Sconosciuto")
            tipo = timer.get("type", "?")
            item = QListWidgetItem(QIcon(self.get_icon_path(tipo)), f"{label} ({tipo})")
            item.setData(Qt.ItemDataRole.UserRole, timer)
            self.list_widget.addItem(item)

    def get_icon_path(self, tipo):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        source = tipo.split(".")[0]
        icon_path = os.path.join(base_dir, "..", "assets", "icons", f"{source.lower()}.png")
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
            self.selected_timer = item.data(Qt.ItemDataRole.UserRole)
            self.accept()

    def get_selected_timer(self):
        return self.selected_timer


class ScriptSelectionDialog(QDialog):
    """
    @brief Dialog window for selecting a script from the scripts JSON list.

    Supports search filtering and double-click/OK selection.
    """
    def __init__(self, scripts_json_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleziona Script")
        self.setMinimumSize(400, 500)
        self.selected_script = None

        self.setStyleSheet(Pantone.DIALOG_STYLE)
        self.scripts = self.load_scripts(scripts_json_path)

        layout = QVBoxLayout(self)

        # Ricerca
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cerca script...")
        self.search_bar.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_bar)

        # Lista
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(Pantone.LISTWIDGET_STYLE)
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)

        # Bottoni
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept_selection)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.populate_list()

    def load_scripts(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("scripts", [])
        except Exception as e:
            logger.error(f"Errore nel caricamento degli script: {e}")
            return []

    def populate_list(self):
        self.list_widget.clear()
        for script in self.scripts:
            label = script.get("label", "Sconosciuto")
            tipo = script.get("type", "?")
            item = QListWidgetItem(QIcon(self.get_icon_path(tipo)), f"{label} ({tipo})")
            item.setData(Qt.ItemDataRole.UserRole, script)
            self.list_widget.addItem(item)

    def get_icon_path(self, tipo):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        source = tipo.split(".")[0]
        icon_path = os.path.join(base_dir, "..", "assets", "icons", f"{source.lower()}.png")
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
            self.selected_script = item.data(Qt.ItemDataRole.UserRole)
            self.accept()

    def get_selected_script(self):
        return self.selected_script


