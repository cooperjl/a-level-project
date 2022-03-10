import numpy as np

# using and adjacency list represented by a dict
# this will be fetched from mainview 

def distance_between(node: tuple, end: tuple) -> float:
    # distance from given node to end node
    return np.sqrt((node[0]-end[0])**2 + (node[1]-end[1])**2)

def trace_route(closedlist: dict, start: int, end: int) -> list:
    route = []
    current_key = end
    while current_key != start:
        route.append(current_key)
        current_key = closedlist[current_key]['previous']
    route.append(start)
    return route[::-1]

def astar_algoritm(start: str, end: str, graph: dict, nodes: list):
    end_node = nodes[end]
    start_node = nodes[end]
    heuristic = distance_between(start_node, end_node)
    openlist = {start:{'g':0, 'f':heuristic, 'previous': start}} # f = (g + h) = (0 + h) = h
    closedlist = {}

    while len(openlist) > 0:
        current_node = min(openlist, key=lambda x: openlist[x]['f'])
        closedlist[current_node] = openlist.pop(current_node)
        
        if current_node == end:
            route = trace_route(closedlist, start, end)
            return route
        else:
            if current_node in graph:
                for neighbour in graph[current_node]:
                    if neighbour not in closedlist:                    
                        new_g = closedlist[current_node]['g'] + distance_between(nodes[current_node], nodes[neighbour])
                        new_f = new_g + distance_between(nodes[neighbour], end_node)
                        
                        if neighbour not in openlist or new_g < openlist[neighbour]['g']:
                            openlist[neighbour] = {'g':new_g, 'f':new_f, 'previous': current_node}
            else:
                return None # start node not connected
    return None # No route


if __name__ == '__main__':
    # does not work due to using integers as labels
    graph = {
        'C': {'A': 184.91078930121952, 'B': 141.36477637657833, 'D': 160.52414148656894},
        'A': {'C': 184.91078930121952, 'B': 277.7048793233565, 'D': 261.457453517776}, 
        'B': {'A': 277.7048793233565, 'E': 264.3709515056448, 'C': 141.36477637657833}, 
        'D': {'A': 261.457453517776, 'C': 160.52414148656894, 'E': 206.81392603013947}, 
        'E': {'B': 264.3709515056448, 'D': 206.81392603013947}
    }
    start = 'A'
    end = 'E'
    nodes = [(455.0, 436.0), (399.0, 164.0), (339.0, 292.0), (201.0, 374.0), (135.0, 178.0)]
