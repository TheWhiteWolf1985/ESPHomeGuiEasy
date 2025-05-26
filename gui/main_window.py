"""
@file main_window.py
@brief Definisce la finestra principale dell'applicazione esphomeGuieasy.

Contiene il layout base suddiviso tra editor YAML, console, comandi di connessione,
e strumenti di creazione dei sensori, strutturato in modo modulare.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from core.yaml_highlighter import YamlHighlighter
from core.yaml_handler import YAMLHandler
from core.log_handler import LOGHandler
from gui.yaml_editor import YamlCodeEditor
from gui.sensor_canvas import SensorCanvas
from gui.sensor_block_item import SensorBlockItem
import config.GUIconfig as conf
import json
import os


class MainWindow(QMainWindow):
    """
    @class MainWindow
    @brief Finestra principale dell'applicazione GUI per ESPHome.

    La classe organizza l'interfaccia grafica in due pannelli principali:
    sinistro (editor YAML e console) e destro (configurazione progetto e sensori).
    """
    def __init__(self):
        """
        @brief Costruttore della finestra principale.
        Inizializza e organizza tutti i widget principali nel layout.
        """
        super().__init__()
        self.setWindowTitle(conf.APP_NAME)
        self.setMinimumSize(conf.MAIN_WINDOW_WIDTH, conf.MAIN_WINDOW_HEIGHT)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # --- LEFT PANE ---
        left_pane = QVBoxLayout()

        # YAML Toolbar
        menubar = self.menuBar()

        # Crea il menu "File"
        file_menu = menubar.addMenu("File")

        file_menu.addAction("Nuovo")
        file_menu.addAction("Apri")
        file_menu.addAction("Salva")
        file_menu.addAction("Esporta bin")

        # YAML Editor
        self.yaml_editor = YamlCodeEditor()
        self.highlighter = YamlHighlighter(self.yaml_editor.document())
        self.yaml_editor.setFixedHeight(500)
        self.yaml_editor.setPlaceholderText("Contenuto YAML qui...")
        self.yaml_editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, monospace;
                font-size: 12pt;
                padding: 8px;
                border: 5px ridge silver;
            }
        """)

        self.yaml_editor.setPlainText(YAMLHandler.load_default_yaml())


        left_top = QVBoxLayout()
        left_top.addWidget(self.yaml_editor)

        # Console Output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.console_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Cascadia Code', Consolas, monospace;
                font-size: 11pt;
                padding: 8px;
                border: 5px ridge silver;
            }
        """)
        LOGHandler.append_to_console(self.console_output, "Console avviata...", "info")

        # Connection & Command Group
        connection_group = QGroupBox("Connessione & Comandi")
        conn_layout = QVBoxLayout()
        conn_layout.addWidget(QPushButton("Compila"))
        conn_layout.addWidget(QPushButton("Flash USB"))
        conn_layout.addWidget(QPushButton("Flash OTA"))
        conn_layout.addWidget(QPushButton("Scan OTA"))
        conn_layout.addWidget(QComboBox())  # Porta seriale/IP
        connection_group.setLayout(conn_layout)

        left_bottom = QHBoxLayout()
        left_bottom.addWidget(self.console_output)
        left_bottom.addWidget(connection_group)

        left_pane.addLayout(left_top)
        left_pane.addLayout(left_bottom)

        # --- RIGHT PANE ---
        right_pane = QVBoxLayout()

        # Controller Image
        self.controller_image = QLabel("[Immagine Controller]")
        self.controller_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.controller_image.setStyleSheet("background-color: lightgray")
        self.controller_image.setFixedSize(400, 300)

        # General Project Data
        general_data = QGroupBox("Dati Generali Progetto")
        general_layout = QFormLayout()

        general_layout.addRow("Nome:", QLineEdit())

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

        # Layout
        board_layout = QVBoxLayout()
        board_layout.addWidget(self.board_search)
        board_layout.addWidget(self.board_combo)
        board_container = QWidget()
        board_container.setLayout(board_layout)

        general_layout.addRow("Board:", board_container)


        general_layout.addRow("SSID:", QLineEdit())
        general_layout.addRow("Password:", QLineEdit())
        general_data.setLayout(general_layout)

        right_top = QHBoxLayout()
        right_top.addWidget(self.controller_image, 2)
        right_top.addWidget(general_data, 1)

        # Sensor Creation (Canvas + Aggiungi bottone)
        sensor_creation = QGroupBox("Creazione Sensori")
        sensor_layout = QVBoxLayout()

        # Crea il canvas e salvalo come attributo per accesso futuro
        self.sensor_canvas = SensorCanvas()
        self.sensor_canvas.setMinimumHeight(400)  # imposta un’altezza minima

        # Pulsante per aggiungere nuovi blocchi
        add_sensor_btn = QPushButton("➕ Aggiungi Sensore")
        add_sensor_btn.clicked.connect(self.aggiungi_blocco_sensore)

        sensor_layout.addWidget(self.sensor_canvas)
        sensor_layout.addWidget(add_sensor_btn)
        sensor_creation.setLayout(sensor_layout)

        right_pane.addLayout(right_top, 1)
        right_pane.addWidget(sensor_creation, 2)

        # Splitter orizzontale principale tra left e right pane
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Crea contenitori QWidget per i due layout (left e right pane)
        left_widget = QWidget()
        left_widget.setLayout(left_pane)

        right_widget = QWidget()
        right_widget.setLayout(right_pane)

        # Aggiungi entrambi allo splitter
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([conf.MAIN_SPLITTER_LEFT_COLUMN, conf.MAIN_SPLITTER_RIGHT_COLUMN])

        # Aggiungi lo splitter al layout principale
        main_layout.addWidget(main_splitter)

        # Composizione finale
        main_layout.addLayout(left_pane, 1)
        main_layout.addLayout(right_pane, 1)



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
        
    def update_controller_image(self, board_value):
        """
        @brief Aggiorna l'immagine del controller in base alla board selezionata.
        """
        image_path = os.path.join("assets", "pinout", f"{board_value}.png")

        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled = pixmap.scaled(self.controller_image.size(),
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
            self.controller_image.setPixmap(scaled)
            self.controller_image.setText("")  # Rimuove il testo placeholder
        else:
            self.controller_image.setPixmap(QPixmap())  # Svuota
            self.controller_image.setText("[Immagine non disponibile]")   

    def aggiungi_blocco_sensore(self):
        """
        @brief Crea e aggiunge un nuovo blocco sensore nel canvas.
        """
        nuovo_blocco = SensorBlockItem("Nuovo Sensore")
        self.sensor_canvas.add_sensor_block(nuovo_blocco)            

