import numpy as np

from PySide6.QtCore import QRect, QPoint, QSize, QLineF
from PySide6.QtGui import QPainterPath, QTransform, QPainterPath, QPen, QColor
from PySide6.QtWidgets import QGraphicsPolygonItem, QGraphicsLineItem


class NodeItem(QGraphicsPolygonItem):
    def __init__(self, state, radius):
        super().__init__()
        self.radius = radius
        self.state = state

        self.star = self.create_star()
        self.ellipse = self.create_ellipse()
        
        self.set_polygon(self.state)

    def create_star(self):
        star_path = QPainterPath()
        star_path.moveTo(0, 6.4)
        for i in range(1, 10):
            angle = (np.pi / 5)
            r = self.radius * (i % 2 + 0.8)
            x = np.sin(angle * i) * r;
            y = np.cos(angle * i) * r;
            star_path.lineTo(x, y)

        return star_path.toFillPolygon(QTransform())

    def create_ellipse(self):
        ellipse_path = QPainterPath()
        base_rect = QRect(QPoint(0, 0), QSize(self.radius * 2, self.radius * 2))
        coords = [coord - self.radius for coord in base_rect.getCoords()]        
        p1 = QPoint(coords[0], coords[1])
        p2 = QPoint(coords[2], coords[3])
        rect = QRect(p1, p2)
        ellipse_path.addEllipse(rect)

        return ellipse_path.toFillPolygon(QTransform())

    def set_polygon(self, state):
        if state == 0:            
            self.setPolygon(self.ellipse)
            self.state = 0
        elif state == 1:            
            self.setPolygon(self.star)
            self.state = 1

    def swap_polygon(self):
        if self.state == 0:
            self.setPolygon(self.star)
            self.state = 1
        else:
            self.setPolygon(self.ellipse)
            self.state = 0

class LineItem(QGraphicsLineItem):
    def __init__(self, line: QLineF, pen: QPen):
        super().__init__()
        self.setLine(line)
        

        self.pen = pen
        self.setPen(self.pen)
        self.default_colour = QColor(255, 255, 255)
        self.pen_colour = QColor(0, 0, 0)

    def paint(self, painter, option, widget):
        outline = QPainterPath()
        outline.moveTo(self.line().p1())
        outline.lineTo(self.line().p2())
        stroke_pen = QPen(self.pen_colour, 6)
        painter.strokePath(outline, stroke_pen)
        return super().paint(painter, option, widget)

    def set_colour(self, colour: QColor):
        # self.colour = colour # can be used to change outline colour
        # self.update(self.boundingRect()) # update needs manually calling in this case
        self.pen.setColor(colour)
        self.setPen(self.pen)
        
    def set_colour_default(self):
        self.set_colour(self.default_colour)

