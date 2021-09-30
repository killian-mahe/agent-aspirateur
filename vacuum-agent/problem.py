from interfaces import Problem


class VacuumProblem(Problem):
    def __init__(self, initial, goal):
        super().__init__(initial, goal)

    def actions(self, state):
        x, y = state.agent.position.to_tuple()  # Agent position
        actions = ["NoOp", "Grab", "Suck"]
        if x != 0:
            actions += ["Left"]
        if x != 4:
            actions += ["Right"]
        if y != 0:
            actions += ["Up"]
        if y != 4:
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
