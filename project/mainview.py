import numpy as np
from PySide6.QtCore import Qt, QRect, QPoint, QSize, QLineF, QPointF, Signal
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsLineItem, 
        QRubberBand, QGraphicsItem)
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QUndoStack, QPixmap

from project.graphitems import NodeItem, LineItem
from project.commands import *


class MainView(QGraphicsView):
    wheel_event = Signal(int)
    def __init__(self, scene):
        super().__init__(scene)
        self.scene = scene
        self.command_stack = QUndoStack()
        
        self.mouse_flag = 0 # 0 when no click, 1 when click and 2 when dragged
        self.node_flag = 0
        self.star_flag = 0
        self.zoom_level = 0
        self.diameter = 16

        self.band_origin = QPoint(0, 0)

        self.rubber_band = None
        self.img_link = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_flag = 1
            point = self.mapToScene(event.position().toPoint())
            collision_point = self.detect_collision(point)

            if collision_point:
                point = collision_point

            self.add_node(point, self.node_flag)

        elif event.button() == Qt.RightButton:
            self.band_origin = event.position().toPoint()
            self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
            self.rubber_band.setGeometry(QRect(self.band_origin, QSize()))
            self.rubber_band.show()

        elif event.button() == Qt.MiddleButton:
            pass

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.node_flag == 0:
            if self.mouse_flag == 2:
                self.scene.removeItem(self.first_line())
                self.scene.removeItem(self.scene.items()[0])
            else:
                self.mouse_flag = 2

            point = self.mapToScene(event.position().toPoint())

            collision_point = self.detect_collision(point)
            if collision_point:
                point = collision_point
            self.add_node(point, self.node_flag)
            self.add_line(self.scene.items()[1].scenePos(), point)

        elif event.buttons() == Qt.RightButton:
            point = event.position().toPoint()  
            self.rubber_band.setGeometry(QRect(self.band_origin, point).normalized())       

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.mouse_flag == 2:
                cmds = []
                line = self.first_line()
                node1 = self.scene.items()[0]
                node2 = self.scene.items()[1]

                col_lines = [col_line for col_line in self.scene.collidingItems(line) if isinstance(col_line, LineItem)]
                col_points = [self.scene.collidingItems(col_line) for col_line in col_lines]

                items = [node1]
                if node2.scenePos() != node1.scenePos():
                    items.append(node2)
                else:
                    self.scene.removeItem(node2)

                points = list(map(QGraphicsItem.scenePos, items))
                items.append(line)

                for item in items:
                    self.scene.removeItem(item)
                mapped_scene = list(map(QGraphicsItem.scenePos, self.scene.items()))

                if len(points) > 1 and points[0] != points[1]:
                    pointer = 0 # accounts for list shifting when points are removed
                    for i, point in enumerate(points):                   
                        if mapped_scene.count(point) != 0:
                            items.pop(i-pointer)
                            pointer += 1

                elif mapped_scene.count(node1.scenePos()) == 0:
                    items = [node1]
                else:
                    items = []

                if len(col_points) > 0:
                    line_p1, line_p2 = line.line().p1(), line.line().p2()
                    for col_line, col_point in zip(col_lines, col_points):
                        for item in col_point:
                            if isinstance(item, NodeItem):
                                node_pos = item.pos()
                                p1, p2 = col_line.line().p1(), col_line.line().p2()
                                if (p1 == line_p1 and p2 == line_p2) or (p2 == line_p1 and p1 == line_p2):
                                    items.remove(line)
                                    break

                                if node_pos != p1 and node_pos != p2:
                                    line1 = self.get_line(p1, node_pos)
                                    line2 = self.get_line(node_pos, p2)
                                    items.append(line1)
                                    items.append(line2)
                                    cmds.append(RemoveItemsCommand(self.scene, [col_line]))

                if len(items) > 0:
                    add_command = AddItemsCommand(self.scene, items)
                    cmds.append(add_command)
                    self.push_to_stack(cmds)

                self.mouse_flag = 0

            elif self.mouse_flag == 1:
                cmds = []
                items = [self.scene.items()[0]]
                item_pos = items[0].scenePos()    
                item_state = items[0].state
                self.scene.removeItem(items[0])

                item = items[0]
                if items[0].state == 1:                    
                    item.swap_polygon()
                    collision = self.scene.collidingItems(item)
                    item.swap_polygon()
                else:
                    collision = self.scene.collidingItems(item)
                mapped_scene = list(map(QGraphicsItem.scenePos, self.scene.items()))

                if mapped_scene.count(item_pos) == 0:
                    if collision and isinstance(collision[0], LineItem):
                        old_line = collision[0]
                        p1, p2 = old_line.line().p1(), old_line.line().p2()
                        line1 = self.get_line(p1, item_pos) # QLineF(p1, item_pos) 
                        line2 = self.get_line(item_pos, p2) #  QLineF(item_pos, p2)
                        cmds.append(RemoveItemsCommand(self.scene, [old_line]))
                        items.append(line1)
                        items.append(line2)

                    add_command = AddItemsCommand(self.scene, items)
                    cmds.append(add_command)
                    if self.node_flag == 1 and self.star_count() > 1:
                        state_command = SetStateCommand(self.scene, self.last_star())
                        cmds.append(state_command)

                    self.push_to_stack(cmds)

                elif collision:
                    if item_state != collision[0].state:
                        state_command = SetStateCommand(self.scene, collision[0])
                        cmds.append(state_command)
                        if self.node_flag == 1 and self.star_count() > 1:
                            # Improve star updating logic
                            state_command2 = SetStateCommand(self.scene, self.first_star())
                            cmds.append(state_command2)

                    self.push_to_stack(cmds)

                self.mouse_flag = 0

        elif event.button() == Qt.RightButton:
            rect = self.rubber_band.geometry()
            rect = self.mapToScene(rect)
            if rect.size() == 0:
                point = self.mapToScene(event.position().toPoint())
                ellipse = self.add_node(point, 0)
                collision = self.scene.collidingItems(ellipse)
                self.scene.removeItem(ellipse)
                if collision:
                    items = [collision[0]]
                else:
                    items = []

            else:
                items = self.scene.items(rect)

            for item in items:
                if isinstance(item, NodeItem):
                    collision = self.scene.collidingItems(item)
                    for line in collision:
                        if line not in items:
                            items.append(line)

            remove_command = RemoveItemsCommand(self.scene, items)
            self.command_stack.push(remove_command)   
            
            self.rubber_band.hide()


    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            self.wheel_event.emit(event.angleDelta().y())
        else:
            return super().wheelEvent(event) 

    def drawBackground(self, painter, _):
        self.set_background(painter)

    def reset_scene(self):
        self.scene.clear()
        self.command_stack.clear()

    def set_image(self, link):
        self.img_link = link
        self.set_background(QPainter())
        self.reset_scene()
        #self.update()
        # code which warns the user to be added later

    def set_background(self, painter):
        if self.img_link:
            pic = QPixmap(self.img_link)
            pic_rect = pic.rect()
            self.setSceneRect(pic_rect)
            
            painter.drawPixmap(pic_rect, pic, pic_rect)
        else:
            self.setSceneRect(self.viewport().geometry())

    def detect_collision(self, point):
        ellipse = self.add_node(point, 0)
        collision = self.scene.collidingItems(ellipse)
        ellipse_pos = ellipse.scenePos()
        self.scene.removeItem(ellipse)
        if len(collision) > 0 and isinstance(collision[0], NodeItem): # QGraphicsEllipseItem
            point = collision[0].scenePos()
            return point
        elif len(collision) > 0 and isinstance(collision[0], LineItem):
            line = collision[0].line()
            p1, p2 = line.p1(), line.p2()
            p1 = np.array([p1.x(), p1.y(), 1])
            p2 = np.array([p2.x(), p2.y(), 1])
            point = ellipse_pos.toTuple()
            # matrix to rotate 90 degrees about point
            rot_matrix = np.array([[0,-1,point[1]+point[0]], [1,0,(-point[0])+point[1]], [0,0,1]])
            
            h_line = np.cross(p1, p2)
            n_line = np.matmul(h_line, rot_matrix)

            snap_point = np.cross(h_line, n_line)
            x, y = snap_point[0:2]/snap_point[2]
            return QPointF(x, y)
        else:
            return None

    def add_node(self, point: QPointF, state):
        brush = QBrush(QColor(255, 255, 255))
        node = NodeItem(state, self.diameter/2)        
        node.setBrush(brush)
        node.setPos(point)
        node.setZValue(1)

        self.scene.addItem(node)
        return node

    def add_line(self, p1: QPointF, p2: QPointF):
        self.scene.addItem(self.get_line(p1, p2))

    def get_line(self, p1: QPointF, p2: QPointF) -> LineItem:
        line = QLineF(p1, p2)
        pen = QPen()
        pen.setColor(QColor(255, 255, 255))
        pen.setWidth(4)
        line_item = LineItem(line, pen)
        return line_item
        
    def push_to_stack(self, cmds: list):        
        if len(cmds) > 1:
            self.command_stack.beginMacro('')
            for cmd in cmds:
                self.command_stack.push(cmd)
            self.command_stack.endMacro()
        elif len(cmds) > 0:
            self.command_stack.push(cmds[0])

    def first_line(self):
        for item in self.scene.items():
            if isinstance(item, LineItem):
                return item

    def first_star(self):
        for item in self.scene.items():
            if isinstance(item, NodeItem) and item.state == 1:
                return item
    
    def last_star(self):
        for item in self.scene.items()[::-1]:
            if isinstance(item, NodeItem) and item.state == 1:
                return item

    def get_undo_action(self):
        return self.command_stack.createUndoAction(self, "Undo")

    def get_redo_action(self):
        return self.command_stack.createRedoAction(self, "Redo")

    def set_node_flag_normal(self):
        self.node_flag = 0

    def set_node_flag_terminal(self):
        self.node_flag = 1

    def set_zoom_level(self, level):
        diff = level - self.zoom_level 
        self.zoom_level = level
        sf = 2**diff        
        self.scale(sf, sf)

    def star_count(self) -> int:
        count = 0
        for item in self.scene.items():
            if isinstance(item, NodeItem) and item.state == 1:
                count += 1

        return count
    
    def get_node_count(self):
        a = np.sum([1 for item in self.scene.items() if isinstance(item, NodeItem)])
        return int(a)
    
    def get_line_count(self):
        a = np.sum([1 for item in self.scene.items() if isinstance(item, LineItem)])
        return int(a)

    def get_graph(self):
        graph = {}
        # letters = ascii_uppercase
        t_nodes = [item.pos() for item in self.scene.items() if isinstance(item, NodeItem) and item.state == 1]
        if len(t_nodes) == 2:
            nodes = [item.pos() for item in self.scene.items() if isinstance(item, NodeItem)]
            arcs = [item.line() for item in self.scene.items() if isinstance(item, LineItem)]

            for arc in arcs:
                p1, p2 = arc.p1(), arc.p2()
                length = arc.length()
                c_nodes = (nodes.index(p1), nodes.index(p2)) #
                for i in range(2):
                    if c_nodes[i] in graph:
                        graph[c_nodes[i]].update({c_nodes[1-i]:length})                
                    else:
                        graph[c_nodes[i]] = {c_nodes[1-i]:length}

            start, end = nodes.index(t_nodes[0]), nodes.index(t_nodes[1]) # letters
            nodes_tuple = [node.toTuple() for node in nodes]
            return graph, start, end, nodes_tuple
        else:
            return None, None, None, None
    
    def highlight_path(self, items):
        colour = QColor(255, 0, 0)
       # item_points = [QPointF(item[0], item[1]) for item in items]
        item_points = [QPointF(*item) for item in items]
        # brush = QBrush(colour) # used for nodes if their colour is to be changed
        
        scene_items = self.scene.items()
        mapped_scene = list(map(QGraphicsItem.scenePos, scene_items))
        # sets all lines to default colour
        [i.set_colour_default() for i in scene_items if isinstance(i, LineItem)]

        selected_lines = []

        for node1, node2 in zip(item_points, item_points[1:]):
            current_node = scene_items[mapped_scene.index(node1)]
            # next_node = item_points[i+1] #  was used for nodes, not functional
            # current_node.setBrush(brush) #  was used for nodes, not functional
            collision = self.scene.collidingItems(current_node) 
            col_lines = [i for i in collision if isinstance(i, LineItem)]
            
            for line in col_lines:
                if line.line().p1() == node2 or line.line().p2() == node2:
                    selected_lines.append(line)
                    # line.set_colour(colour)
                    break
        
        self.push_to_stack([HighlightPathCommand(selected_lines, colour)])
        
        route_length = np.sum([line.line().length() for line in selected_lines])
        return route_length

    def get_scene_state(self):
        items = {'nodes':{}, 't_nodes':{},'lines':{}, 'image':''}
        node_count, t_node_count, line_count = 0, 0, 0
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                if item.state == 0:
                    node_count += 1              
                    node_data = {f'node{node_count}':{'pos': item.pos().toTuple()}}
                    items['nodes'].update(node_data)# , 'state': item.state}}
                    
                else:
                    t_node_count += 1
                    node_data = {f't_node{t_node_count}':{'pos': item.pos().toTuple()}}
                    items['t_nodes'].update(node_data)
               # items['nodes'].update(node_data)

            elif isinstance(item, LineItem):
                line = item.line()
                line_count += 1
                line_data = {f'line{line_count}':{'p1': line.p1().toTuple(), 'p2': line.p2().toTuple()}}
              #  line_data = {f'line{line_count}':{'line': line.toTuple()}}
                items['lines'].update(line_data)

        if self.img_link:
            items['image'] = self.img_link
        return items
    
    def load_scene_state(self, data):
        self.reset_scene()
        nodes, t_nodes, lines = data['nodes'], data['t_nodes'], data['lines']

        if data['image']:
            self.set_image(data['image'])
        else:
            self.set_image('')
        
        for node in nodes:
            pos = nodes[node]['pos']
            self.add_node(QPointF(*pos), 0)
        
        for t_node in t_nodes:
            pos = t_nodes[t_node]['pos']
            self.add_node(QPointF(*pos), 1)

        for line in lines:
            p1, p2 = lines[line]['p1'], lines[line]['p2']
            self.add_line(QPointF(*p1) , QPointF(*p2))
