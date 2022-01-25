import sys
from PySide6.QtWidgets import (QDockWidget, QMainWindow, QApplication, 
        QVBoxLayout, QGroupBox, QRadioButton, QGraphicsView, QGraphicsScene, 
        QGraphicsEllipseItem, QGraphicsLineItem)
from PySide6.QtCore import Qt, Signal, Slot, QRect, QPoint, QSize, QLineF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.main_view = MainView(self.scene)
        
        self.main_view.lclick_handler.connect(self.lclick_handler)
        self.main_view.rclick_handler.connect(self.rclick_handler)
        self.main_view.ghost_handler.connect(self.ghost_handler)

        self.right_groupbox = QGroupBox()
        self.rightdock = QDockWidget("Configuration")
        self.nodes = []
        self.left_drag = True
        self.diameter = 16

        self.config_ui()
        self.setCentralWidget(self.main_view)
        self.addDockWidget(Qt.RightDockWidgetArea, self.rightdock)

    @Slot(QPointF)
    def lclick_handler(self, point):
        collision_point = self.collision_checker(point)
        if self.left_drag == False: # ghost currently exists
            if collision_point:
                if collision_point in self.nodes:
                    self.nodes.append(self.nodes.pop(self.nodes.index(collision_point)))
                    self.scene.removeItem(self.scene.items()[0])
                else:
                    self.nodes.append(point)
            else:
                self.nodes.append(point)
            self.left_drag = True
        else:
            if collision_point:
                self.nodes.append(self.nodes.pop(self.nodes.index(collision_point)))
            else:
                self.add_ellipse(point, self.diameter)
                self.nodes.append(point)

    @Slot(QPointF)
    def rclick_handler(self, point):
        pass
    
    @Slot(QPointF)
    def ghost_handler(self, point):
        if self.nodes:
            if not self.left_drag:
                for item in self.scene.items():
                    if isinstance(item, QGraphicsLineItem):
                        self.scene.removeItem(item)
                        break
                self.scene.removeItem(self.scene.items()[0])
            else:
                self.left_drag = False
        
            collision_point = self.collision_checker(point)
            if collision_point:
                point = collision_point
            self.add_ellipse(point, self.diameter)
            self.add_line(self.nodes[-1], point)

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
    
    def collision_checker(self, point):
        ellipse = self.add_ellipse(point, self.diameter / 4)
        collision = self.scene.collidingItems(ellipse)
        self.scene.removeItem(ellipse)
        if len(collision) > 0 and isinstance(collision[0], QGraphicsEllipseItem):
            point = collision[0].scenePos()
            point = self.adjust_pos(point, True, self.diameter)
            return point
        else:
            return None

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

    def adjust_pos(self, point, positive, diameter):
        radius = diameter / 2
        if not positive:
            radius *= -1
        return QPointF(point.x() + radius, point.y() + radius)

    def main_view_updater(self):
        rect = QRect(QPoint(0, 0), self.main_view.size())# QSize(1920, 1080))
        self.scene.setSceneRect(rect)

    def resizeEvent(self, _): # override resizeEvent, _ to show event is unused
        self.main_view_updater()


# Custom view inheriting QGraphicsView
class MainView(QGraphicsView):
    lclick_handler = Signal(QPointF)
    rclick_handler = Signal(QPointF)
    ghost_handler = Signal(QPointF)
    def __init__(self, scene):
        super().__init__()
        super().setScene(scene)
        self.zoom_level = 0
        self.previous_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lclick_handler.emit(event.scenePosition())
        elif event.button() == Qt.RightButton:
            pass
        elif event.button() == Qt.MiddleButton:
            pass
            # self.previous_pos = event.scenePosition() <- testing

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:  
            self.ghost_handler.emit(event.scenePosition()) 
        elif event.buttons() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            pan = self.previous_pos - event.scenePosition()
            self.previous_pos = event.scenePosition()
          #  self.scroll(pan.x(), pan.y())

        if event.buttons() != Qt.MiddleButton:
            self.setDragMode(QGraphicsView.NoDrag)


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.NoDrag)
        elif event.button() == Qt.LeftButton:
            self.lclick_handler.emit(event.scenePosition())


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

# Main Function
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    window.main_view_updater()
    sys.exit(app.exec())
