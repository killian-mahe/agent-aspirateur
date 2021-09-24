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

    def cost(self, state: State, action):
        return 1

    def heuristic(self, state: State, action):
        return 0

    def __str__(self):
        return f"{type(self).__name__},{self.initial},{self.goal}"
