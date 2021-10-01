from random import random, randint
from math import sqrt, pow
from time import sleep
from copy import deepcopy

from PyQt5.QtCore import QObject, pyqtSignal

from interfaces import State, SimpleProblemSolvingAgentProgram, Node
from problem import VacuumProblem, Agent, Thing, Dirt, Jewel, Position
from algorithms import breadth_first_search, dfs, greedy_bfs, astar


class Screen(QObject):
    thing_spawn = pyqtSignal('PyQt_PyObject')
    thing_deleted = pyqtSignal('PyQt_PyObject')
    thing_moved = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QObject.__init__(self)

    def move_thing(self, thing):
        self.thing_moved.emit(thing)

    def spawn_thing(self, thing):
        self.thing_spawn.emit(thing)

    def delete_thing(self, thing):
        self.thing_deleted.emit(thing)


SCREEN = Screen()


class Environment(State):

    def __init__(self):
        self.things = []
        self.agent = None
        self.x_max = 5
        self.y_max = 5
        self.dirt_probability = 0.05
        self.jewel_probability = 0.01
        self.performance = 0

    def __eq__(self, other):
        if isinstance(other, Environment):
            return self.__hash__() == other.__hash__()
        raise NotImplementedError

    def __hash__(self):
        return hash(self.map())

    def run(self):
        while True:
            if random() <= self.dirt_probability:
                SCREEN.spawn_thing(self.generate_dirt())
            if random() <= self.jewel_probability:
                SCREEN.spawn_thing(self.generate_jewel())
            sleep(0.2)

    def something_at(self, location, thing_class=None):
        if issubclass(thing_class, Agent) and self.agent.position == location:
            return self.agent
        if issubclass(thing_class, Thing):
            things = []
            for thing in self.things:
                if thing.position == location and isinstance(thing, thing_class):
                    things.append(thing)
            return things if things else False
        else:
            raise NotImplementedError

    def map(self):
        sensor_map = []
        for thing in self.things:
            sensor_map.append((thing.position.to_tuple(), "Dirt" if isinstance(thing, Dirt) else "Jewel"))
        if self.agent:
            return tuple([self.agent.position.to_tuple()] + sensor_map)
        return tuple(sensor_map)

    def nearest_dirt(self, agent):
        def distance(t):
            return sqrt(pow(agent.position.x - t.position.x, 2) + pow(agent.position.y - t.position.y, 2))

        for thing in sorted(self.things, key=distance):
            if isinstance(thing, Dirt):
                return thing.position.x, thing.position.y

    def percept(self):
        return self

    def execute_action(self, action, update_screen=False):
        if not isinstance(action, str):
            raise NotImplementedError

        if action == "Left" and self.agent.position.x > 0:
            self.agent.position.x -= 1
        elif action == "Right" and self.agent.position.x < self.x_max - 1:
            self.agent.position.x += 1
        elif action == "Up" and self.agent.position.y > 0:
            self.agent.position.y -= 1
        elif action == "Down" and self.agent.position.y < self.y_max - 1:
            self.agent.position.y += 1
        elif action == "Grab":
            deleted_things = self.delete_thing_at(self.agent.position, Jewel, update_screen)
            if Jewel in deleted_things:
                self.performance += 5
        elif action == "Suck":
            deleted_things = self.delete_thing_at(self.agent.position, [Dirt, Jewel], update_screen)
            if Dirt in deleted_things:
                self.performance += 1
            if Jewel in deleted_things:
                self.performance -= 1
        if update_screen:
            SCREEN.move_thing(self.agent)

    def random_location(self):
        x = randint(0, self.x_max - 1)
        y = randint(0, self.y_max - 1)
        return Position(x, y)

    def generate_dirt(self):
        position = self.random_location()
        while self.something_at(position, Dirt):
            position = self.random_location()
        return self.add_thing(Dirt(position))

    def add_thing(self, thing):
        if issubclass(type(thing), Agent):
            self.agent = thing
            self.agent.position = self.random_location()
            SCREEN.spawn_thing(thing)
            return self.agent
        elif isinstance(thing, Thing):
            self.things.append(thing)
            return thing
        raise NotImplementedError

    def delete_thing(self, deleted_thing, update_screen=False):
        if deleted_thing in self.things:
            if update_screen:
                SCREEN.delete_thing(deleted_thing)
            self.things.remove(deleted_thing)

    def delete_thing_at(self, position, things_class: Thing = Dirt, update_screen=False):
        if not isinstance(things_class, list):
            things_class = [things_class]
        for thing_class in things_class:
            things = self.something_at(position, thing_class)
            if things:
                self.delete_thing(things[0], update_screen)
                yield thing_class

    def generate_jewel(self):
        position = self.random_location()
        while self.something_at(position, Jewel):
            position = self.random_location()
        return self.add_thing(Jewel(position))


class Sensor:

    def __init__(self, environment):
        self.environment = environment

    def get_percept(self):
        return self.environment.percept()


class VacuumAgent(Agent, SimpleProblemSolvingAgentProgram):

    def __init__(self):
        Thing.__init__(self)
        SimpleProblemSolvingAgentProgram.__init__(self)
        self.alive = True
        self.performance = 0

    def can_grab(self, thing):
        if isinstance(thing, (Dirt, Jewel)):
            return True
        return False

    def update_state(self, state, percept):
        return deepcopy(percept)

    def formulate_goal(self, state):
        goal = deepcopy(state)
        return goal.map()[0]

    def formulate_problem(self, state, goal):
        problem = VacuumProblem(state, goal)
        return problem

    def search(self, problem):
        print("Searching for a solution")
        final_node = astar(problem)
        seq = Node.action_sequence(final_node)
        if seq:
            print("Solution found : %s" % seq)
        return seq
