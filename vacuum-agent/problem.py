from interfaces import Problem
from copy import deepcopy


class VacuumProblem(Problem):
    def __init__(self, initial, goal):
        super().__init__(initial, goal)

    def actions(self, state):
        (x, y) = state.agent.position.to_tuple()  # Agent position
        actions = ["Grab", "Suck"]
        if x != 0:
            actions += ["Left"]
        if x != 4:
            actions += ["Right"]
        if y != 0:
            actions += ["Up"]
        if y != 4:
            actions += ["Down"]
        return actions

    def goal_test(self, state):
        return len(state.map()) == 1

    def result(self, state, action):
        result = deepcopy(state)
        result.execute_action(action)
        return result

    def cost(self, current_state, action, future_state):
        return 1

    def heuristic(self, state, action=None):
        h = 0
        state_map = state.state.map()
        agent = state_map[0]
        for t in state_map[1::]:
            h += (abs(agent[0] - t[0][0]) + abs(agent[1] - t[0][1]))
        return h
