from interfaces import Problem, State


class VacuumProblem(Problem):
    def __init__(self):
        super().__init__()

    def actions(self, state: State):
        return []

    def result(self, state: State, action) -> State:
        return state

    def cost(self, current_state: State, action, future_state):
        return 1

    def heuristic(self, state: State, action):
        return 0