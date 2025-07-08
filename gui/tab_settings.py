# -*- coding: utf-8 -*-
"""
@file tab_settings.py
@brief GUI tab for configuring general ESPHome project settings (device name, board, Wi-Fi).

@defgroup gui GUI Modules
@ingroup main
@brief Graphical interface components for project setup.

This module manages the user interface for setting basic ESPHome project details,
such as the board type, device name, and Wi-Fi credentials. It also allows updating
the visual pinout and synchronizing this data with the YAML editor.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

import os, json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QGroupBox, QFormLayout, QLineEdit, QComboBox, QDialog, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from gui.color_pantone import Pantone
from core.translator import Translator
from core.yaml_handler import YAMLHandler
from core.log_handler import GeneralLogHandler as logger
from ruamel.yaml import YAML

class TabSettings(QWidget):
    """
    @brief Tab widget for entering general ESPHome project settings.

    Provides UI elements to input the device name, select the board,
    configure Wi-Fi credentials, and preview the controller pinout image.

    Changes made in this tab can be synchronized with the YAML editor.

    @note The board list is loaded from a JSON file, and images are
          updated dynamically based on selection.
    """    
    def __init__(self, yaml_editor, logger=None):
        """
        @brief Initializes the settings tab with form inputs and image preview.

        Sets up the layout, including:
        - Device name input
        - Board search and selection combo
        - Wi-Fi SSID and password fields
        - Pinout image preview with zoom capability
        - YAML update button

        @param yaml_editor Reference to the shared YAML editor (QPlainTextEdit).
        @param logger Optional logger instance for event logging.
        """        
        super().__init__()
        self.logger = logger
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)        

        # --- Controller Image ---
        self.controller_image = QLabel(Translator.tr("controller_image"))
        self.controller_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.controller_image.setStyleSheet("background-color: lightgray")
        self.controller_image.setFixedHeight(350)
        self.controller_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)        

        # --- Pulsante ingrandisci pinout ---
        self.show_pinout_btn = QPushButton("🔍 " + Translator.tr("zoom_pinout"))
        self.show_pinout_btn.setFixedWidth(390)
        self.show_pinout_btn.clicked.connect(self.mostra_immagine_grande)
        self.show_pinout_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a9dda;
                color: white;
                border-radius: 8px;
                font-size: 13pt;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #2277aa;
            }
        """)        

        # Linea divisoria
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet("""
                              color: #777; 
                              background: #333; 
                              min-height:2px;
                              margin-top: 10px;
                              margin-bottom: 10px;
        """)


        # --- Wrapper verticale per immagine + pulsante ---
        img_box = QVBoxLayout()
        img_box.setAlignment(Qt.AlignmentFlag.AlignTop)
        img_box.addWidget(self.controller_image)
        img_box.addWidget(self.show_pinout_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        img_container = QWidget()
        img_container.setLayout(img_box)

        # --- General Project Data ---
        self.general_data = QGroupBox(Translator.tr("general_project_data"))
        self.general_form = QFormLayout()
        self.general_data.setStyleSheet(Pantone.GROUPBOX_STYLE)

        self.device_name_edit = QLineEdit()
        self.general_form.addRow(QLabel(Translator.tr("device_name")), self.device_name_edit)

        # Ricerca + Combo filtrabile
        self.board_list = self.load_board_list()

        self.board_search = QLineEdit()
        self.board_search.setPlaceholderText(Translator.tr("select_board"))
        self.board_combo = QComboBox()
        self.board_combo.currentIndexChanged.connect(
            lambda: self.update_controller_image(self.board_combo.currentData())
        )


        def filter_board_list(text):
            self.board_combo.clear()
            for board in self.board_list:
                if text.lower() in board["label"].lower():
                    self.board_combo.addItem(board["label"], board["value"])

        # Carica inizialmente tutte le board
        filter_board_list("")
        self.board_search.textChanged.connect(filter_board_list)

        # Layout per combo board
        board_layout = QVBoxLayout()
        board_layout.addWidget(self.board_search)
        board_layout.addWidget(self.board_combo)
        self.board_container = QWidget()
        self.board_container.setLayout(board_layout)

        self.general_form.addRow(QLabel(Translator.tr("board")), self.board_container)
        self.wifi_ssid_edit = QLineEdit()
        self.general_form.addRow(QLabel(Translator.tr("ssid")), self.wifi_ssid_edit)
        self.wifi_pass_edit = QLineEdit()
        self.general_form.addRow(QLabel(Translator.tr("password")), self.wifi_pass_edit)
        self.general_data.setLayout(self.general_form)

        self.update_yaml_btn = QPushButton("🔁 " + Translator.tr("update_yaml"))
        self.update_yaml_btn.setStyleSheet(Pantone.UPDATE_YAML_BTN_STYLE)

        # --- Aggiungi widget a layout principale ---
        layout.addWidget(self.controller_image)
        layout.addWidget(self.show_pinout_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(divider)
        layout.addWidget(self.general_data)
        layout.addStretch()
        layout.addWidget(self.update_yaml_btn, alignment=Qt.AlignmentFlag.AlignRight)


    # --- GETTER per accedere ai dati ---
    def get_device_name(self):
        return self.device_name_edit.text().strip()
    def get_board(self):
        return self.board_combo.currentData()
    def get_ssid(self):
        return self.wifi_ssid_edit.text().strip()
    def get_password(self):
        return self.wifi_pass_edit.text().strip()
    def get_controller_image(self):
        return self.controller_image
    def get_board_combo(self):
        return self.board_combo
    def get_update_yaml_btn(self):
        return self.update_yaml_btn    

    # --- Per settare la combo in automatico (es. ricarica board, ecc.) ---
    def set_board_list(self, boards):
        self.board_list = boards

    def update_controller_image(self, board_value):
        """
        @brief Updates the displayed controller image based on the selected board.

        Loads a PNG image from the assets/pinout folder matching the board's value,
        and scales it proportionally to fit the display area.

        If the image is not found, displays a fallback text.

        @param board_value The internal value of the selected board (used as filename).
        """
        image_path = os.path.join("assets", "pinout", f"{board_value}.png")

        label_width = self.controller_image.width()
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if label_width > 0:
                scaled = pixmap.scaled(
                    label_width,
                    self.controller_image.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.controller_image.setPixmap(scaled)
                self.controller_image.setText("")
            else:
                self.controller_image.setPixmap(pixmap)
                self.controller_image.setText("")
        else:
            self.controller_image.setPixmap(QPixmap())
            self.controller_image.setText(Translator.tr("image_not_available"))   

    def mostra_immagine_grande(self):
        """
        @brief Opens a dialog showing the enlarged version of the current controller image.

        This is typically used to better inspect the pinout diagram selected in the tab.
        """        
        # Prendi la pixmap attuale della label
        pixmap = self.controller_image.pixmap()
        if pixmap is None or pixmap.isNull():
            return  # Niente da mostrare

        dlg = QDialog(self)
        dlg.setWindowTitle(Translator.tr("pinout_dialog_title"))
        dlg.setModal(True)
        dlg.setMinimumSize(600, 450)

        img_label = QLabel()
        img_label.setPixmap(pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        layout = QVBoxLayout()
        layout.addWidget(img_label)

        close_btn = QPushButton(Translator.tr("close"))
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        dlg.setLayout(layout)
        dlg.exec()            

    def load_board_list(self):
        """
        @brief Loads the list of supported boards from a JSON file in the /config directory.

        The expected JSON structure is:
        {
            "boards": [
                {"label": "Commercial Name", "value": "internal_id"},
                ...
            ]
        }

        @return A list of dictionaries with 'label' and 'value' keys, sorted alphabetically.
        """
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_path, "../config/boards.json")

            with open(config_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                boards = data.get("boards", [])
                # Ordina alfabeticamente per label (giusto in caso il file non lo sia già)
                boards.sort(key=lambda x: x["label"].lower())
                return boards
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"[Errore] Caricamento boards.json fallito: {e}")
            return []        
        
    def aggiorna_layout_da_dati(self):
        """
        @brief Updates the YAML content in the editor using only the general project fields.

        Extracts device name, board, SSID and password from the tab inputs,
        then regenerates the corresponding sections in the YAML editor.

        @note This method does not modify the sensor section of the YAML.
        """
        main = self.window()
        if not hasattr(main, "yaml_editor"):
            if self.logger:
                self.logger.log(Translator.tr("yaml_editor_not_found"), "error")
            return

        editor = main.yaml_editor
        if editor is None:
            if self.logger:
               self.logger.log(Translator.tr("yaml_editor_is_none"), "error")
            return

        try:
            current_yaml = editor.toPlainText()
            device_name = self.get_device_name()
            board_value = self.get_board()
            ssid = self.get_ssid()
            password = self.get_password()

            new_yaml = YAMLHandler.generate_yaml_general_sections(
                current_yaml=current_yaml,
                device_name=device_name,
                board=board_value,
                ssid=ssid,
                password=password
            )
            editor.setPlainText(new_yaml)
            if self.logger:
                self.logger.log(Translator.tr("yaml_updated_general"), "success")

        except RuntimeError as e:
            if self.logger:
                self.logger.log(Translator.tr("yaml_editor_destroyed").format(error=str(e)), "error")

    def reset_fields(self):
        """
        @brief Clears all input fields in the Settings tab.

        This includes:
        - Device name
        - Board combo selection
        - Wi-Fi SSID and password fields
        """
        self.device_name_edit.clear()
        self.board_combo.setCurrentIndex(0)
        self.wifi_ssid_edit.clear()
        self.wifi_pass_edit.clear()

    def carica_dati_da_yaml(self, yaml_content):
        """
        @brief Parses the YAML content and updates the Settings tab accordingly.

        Extracts values from the YAML and populates:
        - Device name
        - Selected board
        - Wi-Fi SSID and password

        If the YAML is invalid or fields are missing, defaults are used.

        @param yaml_content YAML content as a string.
        """
        yaml = YAML(typ="safe")
        try:
            data = yaml.load(yaml_content)
        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.log(Translator.tr("yaml_parse_error") + f": {e}", "error")
            return

        # Aggiorna i campi se presenti
        if not data:
            return
        esphome = data.get("esphome", {})
        self.device_name_edit.setText(esphome.get("name", ""))

        esp32 = data.get("esp32", {})
        board = esp32.get("board", "")
        idx = self.board_combo.findData(board)
        if idx >= 0:
            self.board_combo.setCurrentIndex(idx)
        else:
            self.board_combo.setCurrentIndex(0)

        wifi = data.get("wifi", {})
        self.wifi_ssid_edit.setText(wifi.get("ssid", ""))
        self.wifi_pass_edit.setText(wifi.get("password", ""))

    def aggiorna_label(self):
        """
        @brief Updates all translatable labels and placeholders in the tab.

        This includes the groupbox title, input placeholders, and field labels
        based on the current selected language.
        """
        self.general_data.setTitle(Translator.tr("general_project_data"))
        self.show_pinout_btn.setText("🔍 " + Translator.tr("zoom_pinout"))
        self.device_name_edit.setPlaceholderText(Translator.tr("device_name"))
        self.board_search.setPlaceholderText(Translator.tr("select_board"))
        self.general_form.labelForField(self.device_name_edit).setText(Translator.tr("device_name"))
        self.general_form.labelForField(self.wifi_ssid_edit).setText(Translator.tr("ssid"))
        self.general_form.labelForField(self.wifi_pass_edit).setText(Translator.tr("password"))
        self.general_form.labelForField(self.board_container).setText(Translator.tr("board"))
        self.update_yaml_btn.setText("🔁 " + Translator.tr("update_yaml"))
        
    def _editor(self):
        """
        @brief Returns the active YAML editor instance from the main window, if valid.

        This method checks if the editor is still accessible and not destroyed.

        @return QTextEdit instance if valid, otherwise None.
        """
        main = self.window()
        if main is None or not hasattr(main, "yaml_editor"):
            return None

        editor = main.yaml_editor

        # controllo base: se è un QWidget e non ha più parent, è stato probabilmente distrutto
        if editor is None or editor.parent() is None:
            return None

        return editor


