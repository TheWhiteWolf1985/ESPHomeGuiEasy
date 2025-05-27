from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
from gui.sensor_canvas import SensorCanvas
from core.yaml_handler import YAMLHandler

class TabSensori(QWidget):
    def __init__(self, yaml_editor, logger, tab_settings):
        super().__init__()
        self.yaml_editor = yaml_editor
        self.logger = logger
        self.tab_settings = tab_settings

        common_btn_style = """
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
        """        

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- GroupBox per la creazione sensori ---
        sensor_creation = QGroupBox("Creazione Sensori")
        sensor_layout = QVBoxLayout()

        self.sensor_canvas = SensorCanvas()
        self.sensor_canvas.setMinimumHeight(400)

        self.add_sensor_btn = QPushButton("➕ Aggiungi Sensore")
        self.add_sensor_btn.setStyleSheet(common_btn_style)
        self.add_sensor_btn.setFixedWidth(180)
        self.add_sensor_btn.clicked.connect(self.aggiungi_blocco_sensore)

        self.update_yaml_btn = QPushButton("Aggiorna YAML")
        self.update_yaml_btn.setStyleSheet(common_btn_style)
        self.update_yaml_btn.setFixedWidth(180)
        self.update_yaml_btn.clicked.connect(self.aggiorna_yaml_da_blocchi)

        sensor_btn_layout = QHBoxLayout()
        sensor_btn_layout.addWidget(self.add_sensor_btn)
        sensor_btn_layout.addWidget(self.update_yaml_btn)

        sensor_btn_widget = QWidget()
        sensor_btn_widget.setLayout(sensor_btn_layout)

        sensor_layout.addWidget(self.sensor_canvas)
        sensor_layout.addWidget(sensor_btn_widget)
        sensor_creation.setLayout(sensor_layout)

        layout.addWidget(sensor_creation)

    def aggiungi_blocco_sensore(self):
        """
        @brief Crea e aggiunge un nuovo blocco sensore nel canvas.
        """
        from gui.sensor_block_item import SensorBlockItem
        nuovo_blocco = SensorBlockItem("Nuovo Sensore")
        self.sensor_canvas.add_sensor_block(nuovo_blocco)

    def aggiorna_yaml_da_blocchi(self):
        """
        @brief Aggiorna SOLO la sezione sensori nel file YAML, mantenendo il resto invariato.
        """
        current_yaml = self.yaml_editor.toPlainText()

        from core.yaml_handler import YAMLHandler

        new_yaml = YAMLHandler.generate_yaml_sensors_only(
            canvas=self.sensor_canvas.scene(),
            current_yaml=current_yaml
        )

        self.yaml_editor.setPlainText(new_yaml)
        if hasattr(self, "logger"):
            self.logger.log("✅ YAML aggiornato solo dalla sezione sensori.", "success")


    def get_sensor_canvas(self):
        return self.sensor_canvas
