from collections import deque
import heapq
import math
"""
------------------------
-      PRIMITIVES      -
________________________
"""


class State(object):
    def __init__(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError

    def __str__(self):
        return ""


class Problem(object):
    def __init__(self, initial: State = None, goal: State = None):
        self.goal = goal
        self.initial = initial

    def actions(self, state: State):
        raise NotImplementedError

    def result(self, state: State, action) -> State:
        raise NotImplementedError

    def goal_test(self, state: State):
        return state == self.goal

    def cost(self, current_state: State, action, future_state):
        return 1

    def heuristic(self, state: State, action):
        return 0

    def __str__(self):
        return f"{type(self).__name__},{self.initial},{self.goal}"


class SimpleProblemSolvingAgentProgram:

    def __init__(self, initial_state: State = None):
        """State is an abstract representation of the state
        of the world, and seq is the list of actions required
        to get to a particular state from the initial state(root)."""
        self.state = initial_state
        self.seq = []

    def __call__(self, percept):
        """[Figure 3.1] Formulate a goal and problem, then
        search for a sequence of actions to solve it."""
        self.state = self.update_state(self.state, percept)
        if not self.seq:
            goal = self.formulate_goal(self.state)
            problem = self.formulate_problem(self.state, goal)
            self.seq = self.search(problem)
            if not self.seq:
                return None
        return self.seq.pop(0)

    def update_state(self, state, percept):
        raise NotImplementedError

    def formulate_goal(self, state):
        raise NotImplementedError

    def formulate_problem(self, state, goal):
        raise NotImplementedError

    def search(self, problem):
        raise NotImplementedError


"""
------------------------
-     DATA STRUCTS     -
________________________
"""


class Node(object):
    def __init__(self, state, parent=None, action=None, cost: float = 0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost

    def __repr__(self):
        return f"{self.state}"

    def __len__(self):
        return 0 if self.parent is None else (len(self.parent) + 1)

    def __lt__(self, other):
        return self.cost < other.cost

    @staticmethod
    def expand(problem: Problem, node):
        current_state = node.state
        for action in problem.actions(current_state):
            child_state = problem.result(current_state, action)
            cost = node.cost + problem.cost(current_state, action, child_state)
            yield Node(child_state, current_state, action, cost)

    @staticmethod
    def action_sequence(node):
        return [] if node.parent is None else Node.action_sequence(node.parent) + [node.action]

    @staticmethod
    def state_sequence(node):
        return [] if node.parent is None else Node.state_sequence(node.parent) + [node.state]


class PriorityQueue:
    """min-heap"""

    def __init__(self, elements=(), key=lambda i: i):
        self.key = key  # "priority value" used in priority heap evaluation
        self.elements = []  # The actual priority queue
        for e in elements:
            self.add(e)  # add starting elements, satisfying priority heap property

    def add(self, element):
        indexed_element = (self.key(element), element)
        heapq.heappush(self.elements, indexed_element)

    def pop(self):
        return heapq.heappop(self.elements)

    def top(self):
        return self.elements[0][1]

    def __len__(self):
        return len(self.elements)


class Stack:

    def __init__(self):
        self.stack = []

    def add(self,element):
        self.stack.append(element)

    def pop(self):
        return self.stack.pop()

    def isEmpty(self):
        return self.stack == []


"""
------------------------
-      ALGORITHMS      -
________________________
"""


def dfs(problem):
    """Depth First Search"""
    init_node = Node(problem.initial)
    frontier = Stack()
    frontier.append(init_node)
    searched_nodes = {hash(problem.initial): init_node}  # {hash(state):node}
    while frontier:
        current_node = frontier.pop()
        if problem.goal_test(current_node):
            return current_node
        for child in Node.expand(problem, current_node):
            result_state = child.state
            hashed_state = hash(result_state)
            if hashed_state not in searched_nodes:
                searched_nodes[hashed_state] = child
                frontier.add(child)
    return Node("FAILED", cost=math.inf)


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
