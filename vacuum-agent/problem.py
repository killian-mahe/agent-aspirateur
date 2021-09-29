from interfaces import Problem


class VacuumProblem(Problem):
    def __init__(self):
        super().__init__()

    def actions(self, state):
        position = state.agent.position
        actions = ["NoOp", "Grab", "Suck"]
        if position.x != 0:
            actions += ["Left"]
        if position.x != state.x_max - 1:
            actions += ["Right"]
        if position.y != 0:
            actions += ["Up"]
        if position.y != state.y_max - 1:
            actions += ["Down"]
        return actions

    def result(self, state, action):
        state.execute_action(action)
        return state

    def cost(self, current_state, action, future_state):
        if action == "NoOp":
            return 0
        return 1

    def heuristic(self, state, action):
        return 0
