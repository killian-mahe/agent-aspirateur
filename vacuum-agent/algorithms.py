import math
from collections import deque
from typing import Callable

from interfaces import Node, PriorityQueue, Stack, Problem

"""
------------------------
-      UNINFORMED      -
________________________
"""


def dfs(problem: Problem) -> Node:
    """
    Depth First Search algorithm.
    :param problem: Problem to solve.
    :return: Solution node or failed node if no solution is found.
    """
    init_node = Node(problem.initial)
    frontier = Stack()
    frontier.add(init_node)
    searched_nodes = {hash(problem.initial): init_node}  # {hash(state):node}
    while not frontier.is_empty():
        current_node = frontier.pop()
        if problem.goal_test(current_node.state):
            return current_node
        for child in Node.expand(problem, current_node):
            result_state = child.state
            hashed_state = hash(result_state)
            if hashed_state not in searched_nodes:
                searched_nodes[hashed_state] = child
                frontier.add(child)
    return Node("FAILED", cost=math.inf)


def breadth_first_search(problem: Problem) -> Node:
    """
    Breadth First Search algorithm.
    :param problem: Problem to solve.
    :return: Solution node or failed node if no solution is found.
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
    return Node("FAILED", cost=math.inf)


"""
------------------------
-       INFORMED       -
________________________
"""


def bfs(problem: Problem, func: Callable) -> Node:
    """
    Best First Search algorithm implementation.
    :param problem: Problem to solve.
    :param func: Evaluation function.
    :return: Solution node or failed node if no solution is found.
    """
    init_node = Node(problem.initial)
    frontier = PriorityQueue([init_node], key=func)
    searched_nodes = {hash(problem.initial): init_node}  # {hash(state):node}
    while frontier:
        current_node = frontier.pop()[1]
        if problem.goal_test(current_node.state):
            return current_node
        for child in Node.expand(problem, current_node):
            result_state = child.state
            hashed_state = hash(result_state)
            if hashed_state not in searched_nodes or child.cost < searched_nodes[hashed_state].cost:
                searched_nodes[hashed_state] = child
                frontier.add(child)
    return Node("FAILED", cost=math.inf)


def greedy_bfs(problem: Problem, heuristic: Callable = None) -> Node:
    """
    Greedy Best First Search algorithm implementation.
    :param problem: Problem to solve.
    :param heuristic: Evaluation function.
    :return: Solution node or failed node if no solution is found.
    """
    heuristic = heuristic or problem.heuristic
    return bfs(problem, heuristic)


def astar(problem: Problem, heuristic: Callable = None, cost: Callable = None):
    """
    A* algorithm implementation.
    :param problem: Problem to solve.
    :param heuristic:
    :param cost:
    :return: Solution node or failed node if no solution is found.
    """
    heuristic = heuristic or problem.heuristic
    cost = cost or problem.cost
    return bfs(problem, lambda n: heuristic(n) + cost(n))
