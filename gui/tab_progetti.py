from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QSizePolicy, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from gui.color_pantone import Pantone

class TabProgetti(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # === Scroll Area ===
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.project_list_widget = QWidget()
        self.project_list_layout = QVBoxLayout()
        self.project_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.project_list_widget.setLayout(self.project_list_layout)

        self.scroll_area.setWidget(self.project_list_widget)
        main_layout.addWidget(self.scroll_area)

        # === Pulsanti finali ===
        button_layout = QHBoxLayout()
        self.reload_btn = QPushButton("🔄 Ricarica lista")
        self.import_btn = QPushButton("📥 Importa progetto")

        for btn in (self.reload_btn, self.import_btn):
            btn.setFixedHeight(36)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setStyleSheet(Pantone.BUTTON_STYLE)

        button_layout.addWidget(self.reload_btn)
        button_layout.addWidget(self.import_btn)
        main_layout.addLayout(button_layout)

        # Caricamento mock iniziale
        self.load_mock_projects()

    def load_mock_projects(self):
        # Dati di esempio, da sostituire con fetch GitHub
        mock_data = [
            {
                "label": "DHT22 Sensor",
                "version": "1.0",
                "description": "Basic temperature and humidity monitoring.",
                "author": "Juri"
            },
            {
                "label": "Energy Monitor",
                "version": "1.2",
                "description": "Monitors real-time voltage and current.",
                "author": "Alice"
            },
        ]

        for proj in mock_data:
            self.add_project_card(proj)

    def add_project_card(self, project):
        box = QGroupBox(project["label"])
        box.setStyleSheet(Pantone.GROUPBOX_STYLE)
        layout = QVBoxLayout()

        version = QLabel(f"Version: {project['version']}")
        description = QLabel(f"Description: {project['description']}")
        author = QLabel(f"Author: {project['author']}")

        for label in (version, description, author):
            label.setWordWrap(True)
            label.setStyleSheet(Pantone.LABEL_STYLE)
            layout.addWidget(label)

        box.setLayout(layout)
        self.project_list_layout.addWidget(box)

    def clear_projects(self):
        while self.project_list_layout.count():
            child = self.project_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
