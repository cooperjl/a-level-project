import sys
import json
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (QDockWidget, QMainWindow, QApplication, QVBoxLayout, 
        QGroupBox, QRadioButton, QGraphicsScene, QFileDialog, QMenu, QStatusBar, 
        QLabel, QPushButton, QMessageBox, QInputDialog)
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
        self.length_label = QLabel(f"Route Length: ? ")


        self.file_name = ''
        self.unit = 'm'
        self.scale = 0

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

        start_button = QPushButton('Find Path')
        start_button.pressed.connect(self.find_shortest_path)
        
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

        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_bar.zoom_in_event)

        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_bar.zoom_out_event)

        add_image_action = QAction('Add Image...', self)
        add_image_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_I))
        add_image_action.triggered.connect(self.image_file_dialog)

        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_action)

        save_as_action = QAction('Save As...', self)
        save_as_action.setShortcut(QKeySequence(Qt.CTRL | Qt.SHIFT |Qt.Key_S))
        save_as_action.triggered.connect(self.save_file_dialog)

        open_action = QAction('Load File...', self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.load_file_dialog)

        reset_action = QAction('Reset View', self)
        reset_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_R))
        reset_action.triggered.connect(self.reset_view)

        set_scale_action = QAction('Set Scale...', self)
        set_scale_action.triggered.connect(self.set_scale_dialogue)

        set_unit_action = QAction('Set Unit...', self)
        set_unit_action.triggered.connect(self.set_unit_dialogue)

        filemenu = QMenu('File', self)
        filemenu.addActions((reset_action, add_image_action, open_action, save_action, save_as_action))

        editmenu = QMenu('Edit', self)
        editmenu.addActions((undo_action, redo_action, set_scale_action, set_unit_action))

        viewmenu = QMenu('View', self)
        viewmenu.addActions((zoom_in_action, zoom_out_action))

        menubar = self.menuBar()
        menubar.addMenu(filemenu)
        menubar.addMenu(editmenu)
        menubar.addMenu(viewmenu)

        self.status_bar.addPermanentWidget(self.zoom_bar)
        self.status_bar.addWidget(self.arc_label)
        self.status_bar.addWidget(self.node_label)
        self.status_bar.addWidget(self.length_label)
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

    def find_shortest_path(self):
        graph, start, end, nodes = self.main_view.get_graph()
        if graph and start is not None and end is not None and nodes:
            path = astar_algoritm(start, end, graph, nodes)
            if path:
                n_nodes = [nodes[node] for node in path]
                route_length = self.main_view.highlight_path(n_nodes)
                if self.scale == 0:
                    msg = 'You should set a valid scale to get the route length.'
                    self.length_label.setText(f"Route Length: ? ")
                else:
                    route_length_str = f'{route_length*self.scale:.2f}{self.unit}'
                    msg = f'Route length is {route_length_str}'
                    self.length_label.setText(f"Route Length: {route_length_str} ")
                
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Route Length")
                msg_box.setText(msg)
                msg_box.exec()

            else:
                self.show_error_box("No available route between the start and end node.")
        elif not graph and start and end and nodes:
            self.show_error_box("Not enough arcs are drawn.")
        else:
            self.show_error_box("A start and an end node are required.")

    @Slot(int)
    def wheel_slot(self, delta):
        if delta > 0:
            self.zoom_bar.zoom_in_event()
        else:
            self.zoom_bar.zoom_out_event()

    def image_file_dialog(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Images (*.png *.jpg *.bmp)")
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec():
            img = dialog.selectedFiles()[0]
            self.main_view.set_image(img)
            self.file_name = ''

    def save_file_dialog(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON (*.json)")
        if filename:
            self.save_event(filename)
            self.file_name = filename
    
    def load_file_dialog(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("JSON (*.json)")
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec():
            file = dialog.selectedFiles()[0]
            self.load_event(file)

    def save_event(self, filename):
        data = self.main_view.get_scene_state()
        with open(filename, "w") as f:
            json.dump(data, f)
    
    def load_event(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
        
        self.main_view.load_scene_state(data)

    def reset_view(self):
        self.main_view.set_image('')
        self.file_name = ''

    def save_action(self):
        if self.file_name:
            self.save_event(self.file_name)
        else:
            self.save_file_dialog()

    def show_error_box(self, error):
        msg_box = QMessageBox()
        # msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Error")
        msg_box.setText(error)
        msg_box.exec()

    def set_scale_dialogue(self):
        actual_size, _ = QInputDialog.getDouble(self, 'Scale', f'Width of the image or scene in {self.unit}:')
        scene_size = self.main_view.sceneRect().width()
        scale = actual_size/scene_size
        self.scale = scale
    
    def set_unit_dialogue(self):
        unit, _ = QInputDialog.getText(self, 'Unit', f'Unit:')
        self.unit = unit


# Main Function
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
