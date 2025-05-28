from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QGroupBox, QFormLayout, QLineEdit, QComboBox, QDialog, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os
import json
from gui.color_pantone import Pantone

class TabSettings(QWidget):
    def __init__(self, yaml_editor, logger=None):
        super().__init__()
        self.yaml_editor = yaml_editor
        self.logger = logger
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)        

        # --- Controller Image ---
        self.controller_image = QLabel("[Immagine Controller]")
        self.controller_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.controller_image.setStyleSheet("background-color: lightgray")
        self.controller_image.setFixedHeight(350)
        self.controller_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)        

        # --- Pulsante ingrandisci pinout ---
        self.show_pinout_btn = QPushButton("🔍 Ingrandisci Pinout")
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
        general_data = QGroupBox("Dati Generali Progetto")
        general_layout = QFormLayout()
        general_data.setStyleSheet(Pantone.GROUPBOX_STYLE)

        self.device_name_edit = QLineEdit()
        general_layout.addRow("Nome:", self.device_name_edit)

        # Ricerca + Combo filtrabile
        self.board_list = self.load_board_list()

        self.board_search = QLineEdit()
        self.board_search.setPlaceholderText("Cerca board...")
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
        board_container = QWidget()
        board_container.setLayout(board_layout)

        general_layout.addRow("Board:", board_container)
        self.wifi_ssid_edit = QLineEdit()
        general_layout.addRow("SSID:", self.wifi_ssid_edit)
        self.wifi_pass_edit = QLineEdit()
        general_layout.addRow("Password:", self.wifi_pass_edit)
        general_data.setLayout(general_layout)

        self.update_yaml_btn = QPushButton("Aggiorna YAML")
        self.update_yaml_btn.setFixedWidth(390)
        self.update_yaml_btn.setStyleSheet("""
            QPushButton {
                background-color: #6A9955;
                color: white;
                border-radius: 8px;
                font-size: 12pt;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #4e7d44;
            }
        """)

        # --- Aggiungi widget a layout principale ---
        layout.addWidget(self.controller_image)
        layout.addWidget(self.show_pinout_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(divider)
        layout.addWidget(general_data)
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
        @brief Aggiorna l'immagine del controller in base alla board selezionata.
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
            self.controller_image.setText("[Immagine non disponibile]")       

    def mostra_immagine_grande(self):
        # Prendi la pixmap attuale della label
        pixmap = self.controller_image.pixmap()
        if pixmap is None or pixmap.isNull():
            return  # Niente da mostrare

        dlg = QDialog(self)
        dlg.setWindowTitle("Pinout Controller")
        dlg.setModal(True)
        dlg.setMinimumSize(600, 450)

        img_label = QLabel()
        img_label.setPixmap(pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        layout = QVBoxLayout()
        layout.addWidget(img_label)

        close_btn = QPushButton("Chiudi")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        dlg.setLayout(layout)
        dlg.exec()            

    def load_board_list(self):
        """
        @brief Carica la lista delle board supportate da un file JSON in /config.

        Il file deve avere una struttura:
        {
            "boards": [
                {"label": "Nome commerciale", "value": "nome_tecnico"},
                ...
            ]
        }

        @return lista di dizionari con chiavi 'label' e 'value'
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
            print(f"[Errore] Caricamento boards.json fallito: {e}")
            return []        
        
    def aggiorna_layout_da_dati(self):
        """
        @brief Aggiorna il contenuto YAML nell'editor leggendo SOLO i dati generali
            (nome, board, wifi, ecc) dal tab settings.
            NON tocca la parte sensori.
        """
        current_yaml = self.yaml_editor.toPlainText()

        # Prendi i dati dal form settings
        device_name = self.get_device_name()
        board_value = self.get_board()
        ssid = self.get_ssid()
        password = self.get_password()

        # Usa YAMLHandler per aggiornare solo le sezioni generali
        from core.yaml_handler import YAMLHandler

        new_yaml = YAMLHandler.generate_yaml_general_sections(
            current_yaml=current_yaml,
            device_name=device_name,
            board=board_value,
            ssid=ssid,
            password=password
        )

        self.yaml_editor.setPlainText(new_yaml)
        # Se vuoi loggare
        if hasattr(self, "logger"):  # Se hai logger collegato
            self.logger.log("✅ YAML aggiornato con i dati generali.", "success")

    def reset_fields(self):
        """Svuota tutti i campi del tab Settings (nome, board, wifi ecc.)."""
        self.device_name_edit.clear()
        self.board_combo.setCurrentIndex(0)
        self.wifi_ssid_edit.clear()
        self.wifi_pass_edit.clear()

    def carica_dati_da_yaml(self, yaml_content):
        """
        Legge lo YAML e aggiorna i campi del tab settings di conseguenza.
        """
        from ruamel.yaml import YAML
        yaml = YAML(typ="safe")
        try:
            data = yaml.load(yaml_content)
        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.log(f"Errore parsing YAML: {e}", "error")
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

