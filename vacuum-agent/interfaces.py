import heapq

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
        # Hash is used to avoid searched nodes in graph search algorithms
        raise NotImplementedError


class Problem(object):
    def __init__(self, initial=None, goal=None):
        self.goal = goal
        self.initial = initial

    def actions(self, state):
        """returns a list of eligible actions for a given state"""
        raise NotImplementedError

    def result(self, state, action):
        """resolves the change to the state with a given action,returns a future state."""
        raise NotImplementedError

    def goal_test(self, state) -> bool:
        """checks if a state is a goal state."""
        return state == self.goal

    def cost(self, current_state, action, future_state):
        """The cost of the given action from current state to the resulting state """
        return 1

    def heuristic(self, state, action):
        """An estimation of how close a given state is to the goal state"""
        return 0

    def __str__(self):
        return f"{type(self).__name__},{self.initial},{self.goal}"


class SimpleProblemSolvingAgentProgram:

    def __init__(self, initial_state: State = None):
        self.state = initial_state  # The internal stored state of the agent
        self.seq = []

    def __call__(self, percept):
        """Main body of the problem solving process"""
        self.state = self.update_state(self.state, percept)  # The agent percepts
        if not self.seq:
            goal = self.formulate_goal(self.state)
            problem = self.formulate_problem(self.state, goal)  # The agent defines the problem
            self.seq = self.search(problem)  # The agent tries to solve the problem
            if not self.seq:
                return None
        try:
            return self.seq
        finally:
            self.seq = []

    def update_state(self, state, percept):
        """When agent percepts the environment, update the internal state"""
        raise NotImplementedError

    def formulate_goal(self, state):
        """The agent defines a goal state"""
        raise NotImplementedError

    def formulate_problem(self, state, goal):
        """The agent defines the problem"""
        raise NotImplementedError

    def search(self, problem):
        """The agent finds the solution using an algorithm"""
        raise NotImplementedError


"""
------------------------
-     DATA STRUCTS     -
________________________
"""


class Node(object):
    """A node is state + additional information e.g. relationship with other nodes and how to achieve this node."""
    def __init__(self, state, parent=None, action=None, cost: float = 0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost

    def __repr__(self):
        if self.state:
            return f"Node of {self.state}"
        return "Null node"

    def __len__(self):
        return 0 if self.parent is None else (len(self.parent) + 1)

    def __lt__(self, other):
        return self.cost < other.cost

    @staticmethod
    def expand(problem: Problem, node):
        """expands a node, returns child nodes"""
        current_state = node.state
        for action in problem.actions(current_state):
            child_state = problem.result(current_state, action)
            cost = node.cost + problem.cost(current_state, action, child_state)
            yield Node(child_state, node, action, cost)

    @staticmethod
    def action_sequence(node):
        """returns a sequence of actions needed to achieve a node"""
        return [] if node.parent is None else Node.action_sequence(node.parent) + [node.action]

    @staticmethod
    def state_sequence(node):
        """returns a sequence of states to achieve a node"""
        return [] if node.parent is None else Node.state_sequence(node.parent) + [node.state]


class PriorityQueue:
    """= A priority heap"""
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

    def add(self, element):
        self.stack.append(element)

    def pop(self):
        return self.stack.pop()

    def is_empty(self):
        return self.stack == []

    def __str__(self):
        return str(self.stack)
