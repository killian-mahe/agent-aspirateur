from collections import deque
import math

from interfaces import Node, PriorityQueue

"""
------------------------
-      UNINFORMED      -
________________________
"""


def breadth_first_tree_search(problem):
    """
    [Figure 3.7]
    Search the shallowest nodes in the search tree first.
    Search through the successors of a problem to find a goal.
    The argument frontier should be an empty queue.
    Repeats infinitely in case of loops.
    """

    frontier = deque([Node(problem.initial)])  # FIFO queue

    while frontier:
        node = frontier.popleft()
        if problem.goal_test(node.state):
            return node
        frontier.extend(node.expand(problem, node))
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
