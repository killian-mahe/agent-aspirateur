from random import random, randint
from time import sleep

from PyQt5.QtCore import QObject, pyqtSignal

from logic import State


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


class Thing:

    def __init__(self, position: Position = None, x=0, y=0):
        if position and isinstance(position, Position):
            self.position = position
        else:
            self.position = Position(x, y)


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
        return hash({
            "things": self.things,
            "agent": self.agent
        })

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
            for thing in self.things:
                if thing.position == location and isinstance(thing, thing_class):
                    return thing
            return False
        else:
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

    def delete_thing(self, index):
        if index < len(self.things):
            self.thing_deleted.emit(self.things.pop(0))

    def generate_jewel(self):
        position = self.random_location()
        while self.something_at(position, Jewel):
            position = self.random_location()
        return self.add_thing(Jewel(position))


class Agent:

    def __init__(self, position=Position(0, 0)):
        self.position = position

    def run(self):
        pass

    def observe_environment_with_all_my_sensors(self):
        pass

    def update_my_state(self):
        pass

    def choose_an_action(self):
        pass

    def just_do_it(self):
        pass
