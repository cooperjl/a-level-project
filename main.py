from string import ascii_uppercase
import sys
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (QDockWidget, QMainWindow, QApplication, QVBoxLayout, 
        QGroupBox, QRadioButton, QGraphicsScene, QFileDialog, QMenu, QStatusBar, 
        QLabel, QPushButton)
from PySide6.QtGui import QPainter, QAction, QKeySequence

from project.mainview import MainView
from project.zoombar import ZoomBar
from project.astar import astar_algoritm

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.main_view = MainView(self.scene)

        self.right_groupbox = QGroupBox()
        self.rightdock = QDockWidget("Configuration")

        self.zoom_bar = ZoomBar()
        self.status_bar = QStatusBar(self)

        self.arc_label = QLabel(f" Arcs: 0 ")
        self.node_label = QLabel(f"Nodes: 0 ")

        self.config_ui()
        self.setCentralWidget(self.main_view)
        self.addDockWidget(Qt.RightDockWidgetArea, self.rightdock)
        self.setStatusBar(self.status_bar)

    def config_ui(self):
        self.setWindowTitle("Shortest Path Plotter")
        self.main_view.setRenderHint(QPainter.Antialiasing)

        normal_radio = QRadioButton("Normal Node", checked=True)
        terminal_radio = QRadioButton("Terminal Node")
        normal_radio.toggled.connect(self.main_view.set_node_flag_normal)
        terminal_radio.toggled.connect(self.main_view.set_node_flag_terminal)

        start_button = QPushButton('Button')
        start_button.pressed.connect(self.get_nodes)
        
        vbox = QVBoxLayout()
        vbox.addWidget(normal_radio)
        vbox.addWidget(terminal_radio)
        vbox.addWidget(start_button)
        vbox.addStretch(1)
        self.right_groupbox.setLayout(vbox)       

        self.rightdock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.rightdock.setWidget(self.right_groupbox)

        undo_action = self.main_view.get_undo_action()
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)

        redo_action = self.main_view.get_redo_action()
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)

        zoom_in_action = QAction('Zoom in', self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_bar.zoom_in_event)

        zoom_out_action = QAction('Zoom out', self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_bar.zoom_out_event)

        add_image_action = QAction('Add Image...', self)
        add_image_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_I))
        add_image_action.triggered.connect(self.open_file_dialog)

        filemenu = QMenu('File', self)
        filemenu.addAction(add_image_action)

        editmenu = QMenu('Edit', self)
        editmenu.addActions((undo_action, redo_action))

        viewmenu = QMenu('View', self)
        viewmenu.addActions((zoom_in_action, zoom_out_action))

        menubar = self.menuBar()
        menubar.addMenu(filemenu)
        menubar.addMenu(editmenu)
        menubar.addMenu(viewmenu)

        self.status_bar.addPermanentWidget(self.zoom_bar)
        self.status_bar.addWidget(self.arc_label)
        self.status_bar.addWidget(self.node_label)
        self.status_bar.setMaximumHeight(26)

        self.zoom_bar.zoomslider.valueChanged.connect(self.zoom_event)
        self.main_view.wheel_event.connect(self.wheel_slot)
        self.scene.changed.connect(self.scene_change)
    
    def scene_change(self):
        self.arc_label.setText(f" Arcs: {self.main_view.get_line_count()} ")
        self.node_label.setText(f"Nodes: {self.main_view.get_node_count()} ")
    
    def zoom_event(self, level):
        level -= 7 # level from bar is always positive but functions use 0 as the middle
        self.main_view.set_zoom_level(level)        

    def get_nodes(self):
        graph, start, end, nodes = self.main_view.get_graph()
        if graph and start and end and nodes:
            path = astar_algoritm(start, end, graph, nodes)
            print(path)
            print(nodes)
            n_nodes = [nodes[ascii_uppercase.index(node)] for node in path]
            print(n_nodes)
            self.main_view.colour_change(n_nodes)

    @Slot(int)
    def wheel_slot(self, delta):
        if delta > 0:
            self.zoom_bar.zoom_in_event()
        else:
            self.zoom_bar.zoom_out_event()

    def open_file_dialog(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Images (*.png *.jpg *.bmp)")
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec():
            img = dialog.selectedFiles()[0]
            self.main_view.set_image(img)


# Main Function
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
