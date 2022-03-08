import numpy as np

from PySide6.QtCore import QRect, QPoint, QSize
from PySide6.QtGui import QPainterPath, QTransform
from PySide6.QtWidgets import QGraphicsPolygonItem


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
        for i in range(11):
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
