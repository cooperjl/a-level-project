import numpy as np
from string import ascii_uppercase

# using adj. list represented by a dict.:

# this will be fetched from mainview later, but for testing this is used

def letter_to_number(letter: chr) -> int:
    return ascii_uppercase.index(letter)

def heuristic_value(node: tuple, end: tuple) -> float:
    # distance from given node to end node
    return np.sqrt((node[0]-end[0])**2 + (node[1]-end[1])**2)


def cost_function(current_node, target_node, graph, heuristic):
    return graph[current_node][target_node] + heuristic if target_node in graph[current_node] else None

def astar_algoritm(start, end, graph, nodes):
    end_node = nodes[letter_to_number(end)]
    start_node = nodes[letter_to_number(end)]
    heuristic = heuristic_value(start_node, end_node)
    openlist = {start:{'g':0, 'h':heuristic,'f':0, 'previous': start}}
    closedlist = {}
    while len(openlist) > 0:
        current_node = min(openlist, key=lambda x: openlist[x]['f'])
        closedlist[current_node] = openlist.pop(current_node)
        if current_node == end:
            route = []
            current_key = end
            while current_key != start:
                route.append(current_key)
                current_key = closedlist[current_key]['previous']
                print(current_key)

            route.append(start)
            return route[::-1]
       
        else:
            for neighbour in graph[current_node]:
                
                # newg = openlist[current_node]['g'] + graph[current_node][neighbour]
                if neighbour not in closedlist:
                    new_g = closedlist[current_node]['g'] + graph[neighbour][current_node]
                    new_h = heuristic_value(nodes[letter_to_number(neighbour)], end_node)
                    new_f = new_g + new_h

                    if neighbour in openlist and new_g < openlist[neighbour]['g']:
                        openlist.pop(neighbour)

                    elif neighbour in closedlist and new_g < openlist[neighbour]['g']:
                        closedlist.pop(neighbour)

                    elif neighbour not in openlist:
                        openlist[neighbour] = {'g':new_g, 'h':new_h,'f':new_f, 'previous': current_node}
                        # openlist[neighbour]['g'] = new_g
                        # openlist[neighbour]['h'] = new_h
                        # openlist[neighbour]['f'] = new_f
                        # openlist[neighbour]['previous'] = current_node

                    # if neighbour not in openlist:
                    #     openlist[neighbour] = {'g':new_g, 'f': new_g+heuristic, 'previous': current_node}
                    # elif new_g < openlist[neighbour]['g']:
                    #     openlist[neighbour]['g'] = new_g
                    #     openlist[neighbour]['f'] = new_g + heuristic
                    #     openlist[neighbour]['previous'] = current_node
    return None # No route
if __name__ == '__main__':
    graph = {
        'C': {'A': 184.91078930121952, 'B': 141.36477637657833, 'D': 160.52414148656894},
        'A': {'C': 184.91078930121952, 'B': 277.7048793233565, 'D': 261.457453517776}, 
        'B': {'A': 277.7048793233565, 'E': 264.3709515056448, 'C': 141.36477637657833}, 
        'D': {'A': 261.457453517776, 'C': 160.52414148656894, 'E': 206.81392603013947}, 
        'E': {'B': 264.3709515056448, 'D': 206.81392603013947}
    }
    start = 'A'
    end = 'E'
    nodes = [(455.0, 436.0), (399.0, 164.0), (339.0, 292.0), (201.0, 374.0), (135.0, 178.0)] # alphabetical
  #  print(nodes[letter_to_number('B')])
    print(astar_algoritm(start, end, graph, nodes)) # a* pointless with heuristic of 0 but for testing is being used
