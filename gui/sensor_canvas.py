"""
@file sensor_canvas.py
@brief Contiene la scena grafica per ospitare i blocchi sensore (SensorBlockItem).

Fornisce uno spazio interattivo basato su QGraphicsScene/QGraphicsView.
"""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter


class SensorCanvas(QGraphicsView):
    """
    @class SensorCanvas
    @brief Vista grafica contenente i blocchi dei sensori all'interno di una scena.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHints(self.renderHints() |
                            QPainter.RenderHint.Antialiasing |
                            QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setBackgroundBrush(Qt.GlobalColor.darkGray)
        self.setSceneRect(0, 0, 2000, 2000)  # spazio di lavoro grande

    def add_sensor_block(self, block):
        """
        @brief Aggiunge un blocco sensore alla scena in una posizione fissa.
        @param block Oggetto SensorBlockItem da aggiungere.
        """
        block.setPos(100, 100)  # posizione fissa iniziale
        self.scene().addItem(block)
