import math
from collections import deque

from interfaces import Node, PriorityQueue, Stack

"""
------------------------
-      UNINFORMED      -
________________________
"""


def dfs(problem):
    """Depth First Search"""
    init_node = Node(problem.initial)
    frontier = Stack()
    frontier.add(init_node)
    searched_nodes = {hash(problem.initial): init_node}  # {hash(state):node}
    while not frontier.is_empty():
        current_node = frontier.pop()
        if problem.goal_test(current_node.state):
            print("Goal achieved !")
            return current_node
        for child in Node.expand(problem, current_node):
            result_state = child.state
            hashed_state = hash(result_state)
            if hashed_state not in searched_nodes:
                searched_nodes[hashed_state] = child
                frontier.add(child)
    return Node("FAILED", cost=math.inf)


def breadth_first_graph_search(problem):
    """[Figure 3.11]
    Note that this function can be implemented in a
    single line as below:
    return graph_search(problem, FIFOQueue())
    """
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
    frontier = deque([node])
    explored = set()
    while frontier:
        node = frontier.popleft()
        explored.add(node.state)
        for child in node.expand(problem, node):
            if child.state not in explored and child not in frontier:
                if problem.goal_test(child.state):
                    return child
                frontier.append(child)
    return None


"""
------------------------
-       INFORMED       -
________________________
"""


def bfs(problem, func):
    """Best first (graph) search"""
    init_node = Node(problem.initial)
    frontier = PriorityQueue([init_node], key=func)
    searched_nodes = {hash(problem.initial): init_node}  # {hash(state):node}
    while frontier:
        current_node = frontier.pop()
        if problem.goal_test(current_node):
            return current_node
        for child in Node.expand(problem, current_node):
            result_state = child.state
            hashed_state = hash(result_state)
            if hashed_state not in searched_nodes or child.cost < searched_nodes[hashed_state].cost:
                searched_nodes[hashed_state] = child
                frontier.add(child)
    return Node("FAILED", cost=math.inf)


def greedy_bfs(problem, heuristic=None):
    heuristic = heuristic or problem.heuristic
    return bfs(problem, heuristic)


def astar(problem, heuristic=None, cost=None):
    heuristic = heuristic or problem.heuristic
    cost = cost or problem.cost
    return bfs(problem, lambda n: heuristic(n) + cost(n))
