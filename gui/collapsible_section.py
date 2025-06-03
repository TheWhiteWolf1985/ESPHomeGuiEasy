from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QToolButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from gui.color_pantone import Pantone

class CollapsibleSection(QWidget):
    """
    Sezione collassabile/espandibile per uso in accordion custom.
    """
    def __init__(self, title: str, content: QWidget, icon: str = ""):
        super().__init__()
        self._icon = icon  # <--- salva l’icona come attributo di istanza
        self.toggle_button = QToolButton(text=f"{icon} {title}", checkable=True, checked=False)
        self.toggle_button.setStyleSheet(Pantone.ACCORDION_QTOOLBUTTON)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.toggled.connect(self.on_toggled)
        self.toggle_button.setStyleSheet(Pantone.ACCORDION_HEADER_STYLE)
        self.toggle_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.content_area = QFrame()
        self.content_area.setFrameShape(QFrame.Shape.NoFrame)
        self.content_area.setMaximumHeight(0)
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.content_area.setStyleSheet("background-color: #2a2d2e; border-radius: 0 0 8px 8px;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        # Set layout for content
        content_layout = QVBoxLayout()
        content_layout.addWidget(content)
        content_layout.setContentsMargins(0, 0, 0, 0)  # Imposta sempre a zero
        self.content_area.setLayout(content_layout)

    def on_toggled(self, checked):
        if checked:
            self.toggle_button.setArrowType(Qt.ArrowType.DownArrow)
            self.content_area.setMaximumHeight(16777215)
        else:
            self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
            self.content_area.setMaximumHeight(0)
        self.updateGeometry()

    def set_title(self, title):
        """Aggiorna il testo dell’accordion mantenendo l’icona."""
        self.toggle_button.setText(f"{self._icon} {title}")        

