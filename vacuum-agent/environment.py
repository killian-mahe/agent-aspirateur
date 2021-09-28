from random import random, randint
from math import sqrt, pow
from time import sleep
from copy import deepcopy

from PyQt5.QtCore import QObject, pyqtSignal

from interfaces import State, Problem, SimpleProblemSolvingAgentProgram


class Position:

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Position):
            raise NotImplementedError
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def __str__(self):
        return "(%s,%s)" % (self.x, self.y)

    def to_tuple(self):
        return self.x, self.y


class Thing:

    def __init__(self, position: Position = None, x=0, y=0):
        if position and isinstance(position, Position):
            self.position = position
        else:
            self.position = Position(x, y)


class Agent(Thing):
    pass


class Dirt(Thing):
    pass


class Jewel(Thing):
    pass


class Environment(State, QObject):
    thing_spawn = pyqtSignal('PyQt_PyObject')
    thing_deleted = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QObject.__init__(self)
        self.things = []
        self.agent = None
        self.x_max = 5
        self.y_max = 5
        self.dirt_probability = 0.01
        self.jewel_probability = 0.001

    def __eq__(self, other):
        if isinstance(other, Environment):
            return self.__hash__() == other.__hash__()
        raise NotImplementedError

    def __hash__(self):
        return hash(self.percept(self.agent).pop(0))

    def __str__(self):
        pass

    def run(self):
        while True:
            if random() <= self.dirt_probability:
                self.thing_spawn.emit(self.generate_dirt())
            if random() <= self.jewel_probability:
                self.thing_spawn.emit(self.generate_jewel())
            sleep(0.005)

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

    def percept(self, agent):
        """Return the percept that the agent sees at this point."""
        sensor_map = []
        for y in range(0, self.y_max):
            for x in range(0, self.x_max):
                things = self.something_at(Position(x, y), Dirt)
                if things:
                    sensor_map += [(x, y), "Dirty"]
                else:
                    sensor_map += [(x, y), "Clean"]
        return [
            agent.position.to_tuple() +
            sensor_map
        ]

    def nearest_dirt(self, agent):
        def distance(position):
            return sqrt(pow(agent.position.x - position.x, 2) + pow(agent.position.y - position.y, 2))
        for thing in sorted(self.things, key=distance):
            if isinstance(thing, Dirt):
                return thing.position.x, thing.position.y

    def execute_action(self, agent, action):
        """Change the world to reflect this action. (Implement this.)"""
        raise NotImplementedError

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
        if isinstance(thing, Thing):
            self.things.append(thing)
            return thing
        raise NotImplementedError

    def delete_thing(self, deleted_thing):
        if deleted_thing in self.things:
            self.thing_deleted.emit(deleted_thing)
            self.things.remove(deleted_thing)

    def delete_thing_at(self, position, thing_class=Dirt):
        things = self.something_at(position, thing_class)
        if things:
            self.delete_thing(things[0])
        else:
            raise RuntimeError

    def generate_jewel(self):
        position = self.random_location()
        while self.something_at(position, Jewel):
            position = self.random_location()
        return self.add_thing(Jewel(position))


class VacuumAgent(Agent, SimpleProblemSolvingAgentProgram):
    """An Agent is a subclass of Thing with one required instance attribute
    (aka slot), .program, which should hold a function that takes one argument,
    the percept, and returns an action. (What counts as a percept or action
    will depend on the specific environment in which the agent exists.)
    Note that 'program' is a slot, not a method. If it were a method, then the
    program could 'cheat' and look at aspects of the agent. It's not supposed
    to do that: the program can only look at the percepts. An agent program
    that needs a model of the world (and of the agent itself) will have to
    build and maintain its own model. There is an optional slot, .performance,
    which is a number giving the performance measure of the agent in its
    environment."""

    def __init__(self):
        Thing.__init__(self)
        SimpleProblemSolvingAgentProgram.__init__(self)
        self.alive = True
        self.performance = 0

    def can_grab(self, thing):
        """Return True if this agent can grab this thing.
        Override for appropriate subclasses of Agent and Thing."""
        if isinstance(thing, (Dirt, Jewel)):
            return True
        return False

    def update_state(self, state, percept):
        return deepcopy(state)

    def formulate_goal(self, state):
        state = deepcopy(state)
        nearest_dirty_room = state.nearest_dirt(self)
        state.delete_thing_at(Position(nearest_dirty_room[0], nearest_dirty_room[1]))
        return state

    def formulate_problem(self, state, goal):
        problem = Problem(state, goal)
        return problem

    def search(self, problem):
        raise NotImplementedError
