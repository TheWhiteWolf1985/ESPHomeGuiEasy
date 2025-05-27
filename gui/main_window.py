"""
@file main_window.py
@brief Definisce la finestra principale dell'applicazione esphomeGuieasy.

Contiene il layout base suddiviso tra editor YAML, console, comandi di connessione,
e strumenti di creazione dei sensori, strutturato in modo modulare.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from core.yaml_highlighter import YamlHighlighter
from core.yaml_handler import YAMLHandler
from core.log_handler import LOGHandler
from gui.yaml_editor import YamlCodeEditor
from gui.sensor_canvas import SensorCanvas
from gui.sensor_block_item import SensorBlockItem
from core.compile_manager import CompileManager
from core.log_handler import LOGHandler
from gui.tab_settings import TabSettings
from gui.tab_sensori import TabSensori
from gui.tab_command import TabCommand
import config.GUIconfig as conf


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
        

        self.logger = LOGHandler(self.console_output)
        self.compiler = CompileManager(self.logger.log)
        self.logger.log("Console avviata...", "info")  

        left_bottom = QHBoxLayout()
        left_bottom.addWidget(self.console_output)

        left_pane.addLayout(left_top)
        left_pane.addLayout(left_bottom)

        # --- RIGHT PANE ---
        right_pane = QVBoxLayout()

        self.tab_widget = QTabWidget()
        # --- TAB 1: SETTAGGI PROGETTO ---
        self.tab_settings = TabSettings(
            yaml_editor=self.yaml_editor,
            logger=self.logger
        )
        self.tab_widget.addTab(self.tab_settings, "🛠️ Settaggi")
        self.tab_settings.get_update_yaml_btn().clicked.connect(self.tab_settings.aggiorna_layout_da_dati)


        # --- TAB 2: SENSORI ---
        self.tab_sensori = TabSensori(
            yaml_editor=self.yaml_editor,
            logger=self.logger,
            tab_settings=self.tab_settings
        )
        self.tab_widget.addTab(self.tab_sensori, "🧩 Sensori")

        # --- TAB 3: COMPILAZIONE/CARICAMENTO ---
        self.tab_command = TabCommand(
            yaml_editor=self.yaml_editor,
            logger=self.logger,
            compiler=self.compiler,
            flash_callback=None,  # Potrai aggiungerli dopo!
            ota_callback=None
        )
        self.tab_widget.addTab(self.tab_command, "⬆️ Compila/Carica")

        # --- INSERISCI IL QTabWidget NEL RIGHT_PANE ---
        right_pane.addWidget(self.tab_widget)

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

