from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QUndoCommand

from project.nodeitem import NodeItem

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
