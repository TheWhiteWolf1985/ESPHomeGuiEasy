# -*- coding: utf-8 -*-
"""
@file sensor_canvas.py
@brief Provides the graphical scene to host sensor blocks (SensorBlockItem).

@defgroup gui GUI Modules
@ingroup main
@brief GUI elements: windows, dialogs, blocks, and widgets.

Implements an interactive workspace based on QGraphicsScene/QGraphicsView,
allowing users to add, position, and remove sensor blocks visually.

@version \ref PROJECT_NUMBER
@date July 2025
@license GNU Affero General Public License v3.0 (AGPLv3)
"""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter


class SensorCanvas(QGraphicsView):
    """
    @brief Graphical view containing sensor blocks within a QGraphicsScene.

    Supports dragging and smooth rendering with anti-aliasing.
    Sets a large fixed scene rectangle as workspace.
    """
    def __init__(self, parent=None):
        """
        @brief Initializes the SensorCanvas view and sets up the QGraphicsScene.

        Enables drag mode for panning and sets the background to dark gray.
        """
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
        @brief Adds a sensor block to the scene at a fixed initial position.

        @param block The SensorBlockItem object to add.
        """
        block.setPos(100, 100)  # posizione fissa iniziale
        self.scene().addItem(block)

    def clear_blocks(self):
        """
        @brief Removes all sensor blocks from the canvas.
        """
        self.scene().clear()        
