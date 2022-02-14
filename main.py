import sys
import numpy as np
from PySide6.QtWidgets import (QDockWidget, QMainWindow, QApplication, 
        QVBoxLayout, QGroupBox, QRadioButton, QGraphicsView, QGraphicsScene, 
        QGraphicsEllipseItem, QGraphicsLineItem, QRubberBand)
from PySide6.QtCore import Qt, Signal, Slot, QRect, QPoint, QSize, QLineF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QTransform


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.main_view = MainView(self.scene)

        self.right_groupbox = QGroupBox()
        self.rightdock = QDockWidget("Configuration")

        self.config_ui()
        self.setCentralWidget(self.main_view)
        self.addDockWidget(Qt.RightDockWidgetArea, self.rightdock)

    def config_ui(self):
        self.setWindowTitle("Chart Test")
        self.main_view.setRenderHint(QPainter.Antialiasing)
        self.main_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        vbox = QVBoxLayout()
        vbox.addWidget(QRadioButton("Radio Button 1", checked=True))
        vbox.addWidget(QRadioButton("Radio Button 2"))
        vbox.addStretch(1)
        self.right_groupbox.setLayout(vbox)

        self.rightdock.setAllowedAreas(Qt.LeftDockWidgetArea |
                Qt.RightDockWidgetArea)
        self.rightdock.setFeatures(QDockWidget.DockWidgetFloatable |
                            QDockWidget.DockWidgetMovable)
        self.rightdock.setWidget(self.right_groupbox)

    def main_view_updater(self):
        rect = QRect(QPoint(0, 0), self.main_view.size())# QSize(1920, 1080))
        self.scene.setSceneRect(rect)

    def resizeEvent(self, _): # override resizeEvent, _ to show event is unused
        self.main_view_updater()


# Custom view inheriting QGraphicsView
class MainView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.scene = scene

        self.nodes = []
        
        self.mouse_flag = 0 # 0 when no click, 1 when click and 2 when dragged
        self.zoom_level = 0
        self.diameter = 16
        
        self.band_origin = QPointF(0, 0)
        
        self.rubber_band = None
        self.previous_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_flag = 1
            point = event.scenePosition()
            collision_point = self.detect_collision(point)

            if collision_point:
                if self.nodes.count(collision_point) > 0:
                    self.nodes.append(self.nodes.pop(self.nodes.index(collision_point)))
                else:
                    self.add_ellipse(collision_point, self.diameter)
                    self.nodes.append(collision_point)                    
            else:
                self.add_ellipse(point, self.diameter)
                self.nodes.append(point)

        elif event.button() == Qt.RightButton:
            self.band_origin = event.scenePosition().toPoint()
            self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
            self.rubber_band.setGeometry(QRect(self.band_origin, QSize()))
            self.rubber_band.show()

        elif event.button() == Qt.MiddleButton:
            pass

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.mouse_flag == 2:
                self.scene.removeItem(self.scene.items()[len(self.nodes)+1])
                self.scene.removeItem(self.scene.items()[0])
            else:
                self.mouse_flag = 2

            point = event.scenePosition()
            collision_point = self.detect_collision(point)
            if collision_point:
                point = collision_point
            self.add_ellipse(point, self.diameter)
            self.add_line(self.nodes[-1], point)

        elif event.buttons() == Qt.RightButton:
            point = event.scenePosition().toPoint()
            self.rubber_band.setGeometry(QRect(self.band_origin, point).normalized())

        elif event.buttons() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            pan = self.previous_pos - event.scenePosition()
            #  self.scroll(pan.x(), pan.y())
            self.previous_pos = event.scenePosition()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.mouse_flag == 2:
                point = event.scenePosition()
                collision_point = self.detect_collision(point)
                item = self.scene.itemAt(point, QTransform())
                if item:
                    collision = self.scene.collidingItems(item)
                else:
                    collision = []
                first_node = self.scene.items()[0]
                if len(collision) == 1 and first_node == self.scene.items()[1].scenePos():
                    self.scene.removeItem(self.scene.items()[len(self.nodes)+1])
                    self.scene.removeItem(first_node)
                elif collision_point in self.nodes:
                    self.scene.removeItem(first_node)
                else:
                    self.nodes.append(point)
                self.mouse_flag = 0

        elif event.button() == Qt.RightButton:
            rect = self.rubber_band.geometry()
            if rect.size() == QSize(0, 0):
                collision_point = self.detect_collision(event.scenePosition())
                item = self.scene.itemAt(collision_point, QTransform())
                self.remove_items(item)
            else:
                for item in self.scene.items(rect):
                    self.remove_items(item)

            self.rubber_band.hide()

        elif event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.NoDrag)
        
    def wheelEvent(self, event):
        new_zoom = self.zoom_level
        if event.angleDelta().y() > 0:
            sf = 1.25
            new_zoom += 1
        else:
            sf = 0.8
            new_zoom -= 1

        if new_zoom <= 5 and new_zoom >= 0:
            self.zoom_level = new_zoom
            self.scale(sf, sf)

    def detect_collision(self, point):
        ellipse = self.add_ellipse(point, self.diameter)
        collision = self.scene.collidingItems(ellipse)
        ellipse_pos = self.adjust_pos(ellipse.pos(), True, self.diameter)
        self.scene.removeItem(ellipse)
        if len(collision) > 0 and isinstance(collision[0], QGraphicsEllipseItem):
            point = collision[0].scenePos()
            point = self.adjust_pos(point, True, self.diameter)
            return point
        elif len(collision) > 0 and isinstance(collision[0], QGraphicsLineItem):
            line = collision[0].line()
            p1, p2 = line.p1(), line.p2()
            p1 = np.array([p1.x(), p1.y(), 1])
            p2 = np.array([p2.x(), p2.y(), 1])
            point = ellipse_pos.toTuple()
            # matrix to rotate 90 degrees about point
            rot_matrix = np.array([[0,-1,point[1]+point[0]], [1,0,(-point[0])+point[1]],[0,0,1]])
            
            h_line = np.cross(p1, p2)
            n_line = np.matmul(h_line, rot_matrix)

            snap_point = np.cross(h_line, n_line)
            x,y = snap_point[0:2]/snap_point[2]
            return QPointF(x, y)
        else:
            return None

    def add_ellipse(self, point: QPointF, diameter):
        colour = QColor(0, 0, 0)
        point = self.adjust_pos(point, False, diameter)
        rect = QRect(QPoint(0, 0), QSize(diameter, diameter))
        ellipse = self.scene.addEllipse(rect, QPen(), QBrush(colour))
        ellipse.setPos(point)
        ellipse.setZValue(1)
        return ellipse

    def add_line(self, p1: QPointF, p2: QPointF):
        line = QLineF(p1, p2)
        pen = QPen()
        pen.setColor(QColor(0, 0, 0))
        pen.setWidth(1)
        self.scene.addLine(line, pen)
        return line

    def adjust_pos(self, point, positive, diameter):
        radius = diameter / 2
        if not positive:
            radius *= -1
        return QPointF(point.x() + radius, point.y() + radius)

    def remove_items(self, item):
        if isinstance(item, QGraphicsEllipseItem):
            collision = self.scene.collidingItems(item)
            for line in collision:
                self.scene.removeItem(line)
            self.nodes.remove(self.adjust_pos(item.scenePos(), True, self.diameter))
        self.scene.removeItem(item)

# Main Function
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    window.main_view_updater()
    sys.exit(app.exec())
