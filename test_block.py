from PyQt6.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView, QGraphicsTextItem,
    QGraphicsRectItem, QGraphicsProxyWidget, QGraphicsItem, QLineEdit,
    QGraphicsSimpleTextItem, QGraphicsEllipseItem, QGraphicsPathItem
)
from PyQt6.QtGui import QFont, QPainterPath, QColor, QPen, QPainter
from PyQt6.QtCore import Qt, QPointF
import sys

class IfBlock(QGraphicsRectItem):
    def __init__(self):
        super().__init__(0, 0, 240, 200)
        self.setBrush(QColor("#f1c40f"))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

        font_bold = QFont("Consolas", 10, QFont.Weight.Bold)

        # Titolo IF
        self.title = QGraphicsTextItem("IF", self)
        self.title.setFont(font_bold)
        self.title.setPos(10, 5)

        # Area CONDIZIONE
        self.cond_box = QGraphicsRectItem(10, 30, 220, 30, self)
        self.cond_box.setBrush(QColor("#ecf0f1"))
        self.cond_box.setPen(QPen(Qt.GlobalColor.darkGray))

        # Etichetta THEN
        then_label = QGraphicsSimpleTextItem("THEN:", self)
        then_label.setFont(font_bold)
        then_label.setPos(10, 70)

        # Area THEN
        self.then_box = QGraphicsRectItem(10, 90, 220, 30, self)
        self.then_box.setBrush(QColor("#ecf0f1"))
        self.then_box.setPen(QPen(Qt.GlobalColor.darkGray))

        # Etichetta ELSE
        else_label = QGraphicsSimpleTextItem("ELSE:", self)
        else_label.setFont(font_bold)
        else_label.setPos(10, 130)

        # Area ELSE
        self.else_box = QGraphicsRectItem(10, 150, 220, 30, self)
        self.else_box.setBrush(QColor("#ecf0f1"))
        self.else_box.setPen(QPen(Qt.GlobalColor.darkGray))

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawRoundedRect(self.rect(), 10, 10)

app = QApplication(sys.argv)
scene = QGraphicsScene()
view = QGraphicsView(scene)
view.setRenderHint(QPainter.RenderHint.Antialiasing)
view.setWindowTitle("Prototipo Blocco IF")
view.setGeometry(100, 100, 600, 400)

if_block = IfBlock()
scene.addItem(if_block)
if_block.setPos(150, 100)

view.show()
sys.exit(app.exec())
