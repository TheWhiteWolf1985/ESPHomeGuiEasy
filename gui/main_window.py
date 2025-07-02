"""
@file main_window.py
@brief Definisce la finestra principale dell'applicazione esphomeGuieasy.

Contiene il layout base suddiviso tra editor YAML, console, comandi di connessione,
e strumenti di creazione dei sensori, strutturato in modo modulare.
"""
import os, json
import shutil
import config.GUIconfig as conf
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QUrl, pyqtSlot
from PyQt6.QtGui import QPalette, QColor, QIcon
from core.yaml_highlighter import YamlHighlighter
from core.yaml_handler import YAMLHandler
from gui.yaml_editor import YamlCodeEditor
from gui.sensor_canvas import SensorCanvas
from gui.sensor_block_item import SensorBlockItem
from core.compile_manager import CompileManager
from core.log_handler import LOGHandler
from gui.tab_settings import TabSettings
from gui.tab_sensori import TabSensori
from gui.tab_command import TabCommand
from gui.menu_bar import MainMenuBar
from gui.tab_modules import TabModules
from gui.color_pantone import Pantone
from core.translator import Translator
from core.project_handler import ProjectHandler
from core.settings_db import add_recent_file, get_setting
from core.log_handler import GeneralLogHandler
from gui.new_project_dialog import NewProjectDialog
from core.new_project_handler import create_new_project

class MainWindow(QMainWindow):
    """
    @class MainWindowq
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
        self.setWindowIcon(QIcon(conf.SW_ICON_PATH))  
        logger = GeneralLogHandler() 

        logger.debug(f"DEBUG SLOT: {hasattr(self, 'log_from_thread')}")   

        self.last_save_path = None
        self.project_dir = None

        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor("#23272e"))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor("#d4d4d4"))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor("#23272e"))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor("#d4d4d4"))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor("#3a9dda"))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2a2d2e"))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))       

        common_input_style = """
            QLineEdit, QComboBox {
                background-color: #2a2d2e;
                color: #d4d4d4;
                border: 1px solid #444;
                border-radius: 5px;
                font-size: 11pt;
                padding: 4px 8px;
            }
            QLineEdit:disabled, QComboBox:disabled {
                background-color: #222;
                color: #888;
            }
        """  

        label_style = """
        QLabel {
            color: #d4d4d4;
            font-size: 11pt;
        }
        """        

        self.setStyleSheet(self.styleSheet() + common_input_style)
        self.setStyleSheet(self.styleSheet() + label_style)

        self.setPalette(dark_palette)
        self.setAutoFillBackground(True)        

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # --- LEFT PANE ---
        left_pane = QVBoxLayout()

        self.menu_bar = MainMenuBar(self)
        self.setMenuBar(self.menu_bar) 

        # YAML Editor
        self.yaml_editor = YamlCodeEditor()
        self.highlighter = YamlHighlighter(self.yaml_editor.document())
        self.yaml_editor.setFixedHeight(500)
        self.yaml_editor.setPlaceholderText(Translator.tr("yaml_placeholder"))
        self.yaml_editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, monospace;
                font-size: 12pt;
                padding: 8px;
                border: 2px solid #444;
                border-radius: 8px;
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
                border: 2px solid #444;
                border-radius: 8px;
            }
        """)
        

        self.logger = LOGHandler(self.console_output)
        self.compiler = CompileManager(self.logger.log)
        self.compiler.window = self
        self.logger.log(Translator.tr("console_started"), "info")  

        left_bottom = QHBoxLayout()
        left_bottom.addWidget(self.console_output)

        left_pane.addLayout(left_top)
        left_pane.addLayout(left_bottom)

        # --- RIGHT PANE ---
        right_pane = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(Pantone.TAB_WIDGET)
        # --- TAB 1: SETTAGGI PROGETTO ---
        self.tab_settings = TabSettings(
            yaml_editor=self.yaml_editor,
            logger=self.logger
        )
        self.tab_widget.addTab(self.tab_settings, Translator.tr("tab_settings"))
        self.tab_settings.get_update_yaml_btn().clicked.connect(self.tab_settings.aggiorna_layout_da_dati)

        # --- TAB 2: MODULI PROGETTO ---
        self.tab_modules = TabModules(self.yaml_editor, self.logger)
        self.tab_widget.addTab(self.tab_modules, Translator.tr("tab_modules"))  

        # --- TAB 3: SENSORI ---
        self.tab_sensori = TabSensori(
            yaml_editor=self.yaml_editor,
            logger=self.logger,
            tab_settings=self.tab_settings
        )
        self.tab_widget.addTab(self.tab_sensori, Translator.tr("tab_sensors"))

        # --- TAB 4: COMPILAZIONE/CARICAMENTO ---
        self.tab_command = TabCommand(
            yaml_editor=self.yaml_editor,
            logger=self.logger,
            compiler=self.compiler,
            flash_callback=None,  # Potrai aggiungerli dopo!
            ota_callback=None
        )
        self.tab_widget.addTab(self.tab_command, Translator.tr("tab_compile_upload"))

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

##########################################################################
#                          METODI MENU BAR                               #
##########################################################################
        # new_action gestito dentro al file new_project_dialog.py
        self.menu_bar.open_action.triggered.connect(lambda _: self.open_project_dialog())
        self.menu_bar.save_action.triggered.connect(self.salva_progetto)
        self.menu_bar.saveas_action.triggered.connect(self.salva_con_nome)
        self.menu_bar.import_action.triggered.connect(self.importa_yaml)
        self.menu_bar.export_action.triggered.connect(self.esporta_yaml)
        self.menu_bar.exit_action.triggered.connect(self.close)     

    def nuovo_progetto(self):

        dialog = NewProjectDialog(self)
        result = dialog.exec()
        print(f"[DEBUG] dialog.exec() returned: {result}")
        if result != QDialog.DialogCode.Accepted:
            GeneralLogHandler.debug("[DEBUG] Dialog chiuso con CANCEL, nessuna azione eseguita.")
            return


        data = dialog.get_data()
        result = create_new_project(
            data,
            yaml_editor=self.yaml_editor,
            logger=self.logger,
            compiler=self.compiler,
            reset_tabs_callback=self._reset_tabs,
            update_recent_callback=self.menu_bar._update_recent_files_menu
        )

        if not result:
            return

        project_dir, yaml_path = result
        self.last_save_path = yaml_path
        self.project_dir = project_dir

        # Apri automaticamente il progetto appena creato
        self.open_project(yaml_path)

    def open_project(self, yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.yaml_editor.setPlainText(content)
        # Prima aggiorna i campi settings leggendo dallo YAML!
        self.tab_settings.carica_dati_da_yaml(content)
        # Poi aggiorna i blocchi grafici
        self.tab_sensori.aggiorna_blocchi_da_yaml(content)
        #Poi aggiorna gli accordion
        self.tab_modules.carica_dati_da_yaml(content)
        self.logger.log(Translator.tr("project_opened").format(path=yaml_path), "success")
        # Salva anche la directory progetto!
        self.last_save_path = yaml_path
        self.project_dir = os.path.dirname(os.path.abspath(yaml_path))
        add_recent_file(yaml_path)
        self.menu_bar._update_recent_files_menu()

    def open_project_dialog(self):
        # Imposta la cartella iniziale: Documenti/ESPHomeGUIeasy
        initial_dir = Path.home() / "Documents" / "ESPHomeGUIeasy"
        initial_dir.mkdir(parents=True, exist_ok=True)

        # File dialog
        filename_tuple = QFileDialog.getOpenFileName(
            self,
            Translator.tr("open_project"),
            str(initial_dir),
            "YAML Files (*.yaml *.yml);;Tutti i file (*)"
        )
        if not filename_tuple or not isinstance(filename_tuple, tuple):
            return
        filename = filename_tuple[0]
        if filename and isinstance(filename, str):
            self.open_project(filename)

    def salva_progetto(self):
        """
        Salva il progetto sull’ultimo file usato (devi gestire un attributo path).
        Se non c’è, chiama salva_con_nome().
        """
        try:
            if not hasattr(self, "last_save_path") or not self.last_save_path:
                self.salva_con_nome()
                return
            content = self.yaml_editor.toPlainText()
            with open(self.last_save_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.log(Translator.tr("project_saved").format(path=self.last_save_path), "success")
        except Exception as e:
            self.logger.log(Translator.tr("save_error").format(e=e), "error")

    def salva_con_nome(self):
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Salva progetto come...", "", "YAML Files (*.yaml *.yml);;Tutti i file (*)")
        if filename:
            content = self.yaml_editor.toPlainText()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            self.last_save_path = filename
            self.logger.log(Translator.tr("project_saved_as").format(path=filename), "success")

    def importa_yaml(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Importa YAML", "", "YAML Files (*.yaml *.yml);;Tutti i file (*)")
        if filename:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                self.yaml_editor.setPlainText(content)
            # Puoi sincronizzare anche qui:
            self.tab_settings.carica_dati_da_yaml(content)
            self.tab_sensori.aggiorna_blocchi_da_yaml(content)
            self.tab_modules.carica_dati_da_yaml(content)
            self.logger.log(Translator.tr("yaml_imported").format(path=filename), "success")
            add_recent_file(filename)
            self.menu_bar._update_recent_files_menu()

    def esporta_yaml(self):
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Esporta YAML come...", "", "YAML Files (*.yaml *.yml);;Tutti i file (*)")
        if filename:
            content = self.yaml_editor.toPlainText()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.log(Translator.tr("yaml_exported").format(path=filename), "success")

    def aggiorna_tutte_le_label(self):
        # Aggiorna i titoli dei tab
        self.tab_widget.setTabText(0, Translator.tr("tab_settings"))
        self.tab_widget.setTabText(1, Translator.tr("tab_modules"))
        self.tab_widget.setTabText(2, Translator.tr("tab_sensors"))
        self.tab_widget.setTabText(3, Translator.tr("tab_compile_upload"))
        # Aggiorna menubar
        self.menu_bar.update_labels()
        # Aggiorna label/bottoni nei tab (aggiungi metodi aggiorna_label() nei tuoi tab)
        self.tab_settings.aggiorna_label()
        self.tab_modules.aggiorna_label()
        self.tab_sensori.aggiorna_label()
        self.tab_command.aggiorna_label()            

    def export_project(self):
        if not self.project_dir:
            self.logger.log("Nessun progetto attivo da esportare.", "warning")
            return
        ProjectHandler.export_project(
            self.project_dir, QFileDialog.getSaveFileName, self.logger.log
        )

    def import_project(self):
        ProjectHandler.import_project(
            QFileDialog.getOpenFileName, QFileDialog.getExistingDirectory,
            self.logger.log, self.open_project  # open_project = funzione per aprire un nuovo progetto in GUI
        )        
    
    @pyqtSlot(str, str)
    def log_from_thread(self, message: str, level: str):
        """
        Slot thread-safe per loggare messaggi nella console GUI.
        """
        self.logger.log(message, level)           


    def get_or_create_yaml_path(self) -> str:
        """
        Restituisce il percorso del file YAML da usare per upload/compile:
        - Se esiste un salvataggio → salva lì
        - Altrimenti crea un file temporaneo in una cartella scrivibile
        """
        yaml_text = self.yaml_editor.toPlainText()

        if self.last_save_path:
            with open(self.last_save_path, "w", encoding="utf-8") as f:
                f.write(yaml_text)
            self.logger.log(Translator.tr("file_saved_to").format(path=self.last_save_path), "success")
            return self.last_save_path

        # Se c'è un progetto, salva direttamente lì
        if self.project_dir:
            base_dir = self.project_dir
            temp_dir = os.path.join(base_dir, ".temp")
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, "__temp_upload.yaml")
        else:
            # Usa la cartella build centralizzata
            temp_path = os.path.join(conf.DEFAULT_BUILD_DIR, "__temp_upload.yaml")

        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, "__temp_upload.yaml")

        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(yaml_text)

        self.logger.log(Translator.tr("unsaved_project_temp_warning"), "warning")
        self.logger.log(Translator.tr("temp_file_generated").format(temp_path=temp_path), "info")
        return temp_path
    
    def _reset_tabs(self):
        self.tab_settings.reset_fields()
        self.tab_modules.reset_fields()
        self.tab_sensori.get_sensor_canvas().clear_blocks()


