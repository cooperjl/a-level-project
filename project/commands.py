from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QUndoCommand, QColor

from project.graphitems import NodeItem, LineItem

class AddItemsCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, items: list):
        super().__init__()
        self.scene = scene
        self.items = items
    
    def undo(self):
        for item in self.items:
            self.scene.removeItem(item)
    
    def redo(self):
        for item in self.items:
            self.scene.addItem(item)


class RemoveItemsCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, items: list):
        super().__init__()
        self.scene = scene
        self.items = items
        
    def undo(self):
        for item in self.items:
            self.scene.addItem(item)

    def redo(self):
        for item in self.items:
            self.scene.removeItem(item)


class SetStateCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, item: NodeItem):
        super().__init__()
        self.scene = scene
        self.item = item
    
    def undo(self):
        self.item.swap_polygon()

    def redo(self):
        self.item.swap_polygon()

class HighlightPathCommand(QUndoCommand):
    def __init__(self, items: list, colour = QColor):
        super().__init__()
        self.items = items
        self.colour = colour
        self.old_colour = items[0].default_colour # assuming all same colour
    
    def undo(self):
        for item in self.items:
            item.set_colour(self.old_colour)

    def redo(self):
        for item in self.items:
            item.set_colour(self.colour)
