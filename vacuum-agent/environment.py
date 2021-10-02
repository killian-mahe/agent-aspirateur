from random import random, randint
from math import sqrt, pow
from time import sleep
from typing import Union, List, Tuple

from copy import deepcopy

from PyQt5.QtCore import QObject, pyqtSignal

from interfaces import State, SimpleProblemSolvingAgentProgram, Node, Problem
from problem import VacuumProblem, Agent, Thing, Dirt, Jewel, Position
from algorithms import breadth_first_search, dfs, greedy_bfs, astar


class Screen(QObject):
    """Make the link between the environment and the GUI."""
    thing_spawn = pyqtSignal('PyQt_PyObject')
    thing_deleted = pyqtSignal('PyQt_PyObject')
    thing_moved = pyqtSignal('PyQt_PyObject')
    performance_updated = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QObject.__init__(self)

    def move_thing(self, thing: Thing):
        """
        Move thing on the map.
        :param thing:
        :return:
        """
        self.thing_moved.emit(thing)

    def spawn_thing(self, thing: Thing):
        """
        Create a new thing on the map.
        :param thing:
        :return:
        """
        self.thing_spawn.emit(thing)

    def delete_thing(self, thing: Thing):
        """
        Delete an existing thing on the map
        :param thing:
        :return:
        """
        self.thing_deleted.emit(thing)

    def update_performance(self, performance: int):
        """
        Update the performance label.
        :param performance:
        :return:
        """
        self.performance_updated.emit(performance)


SCREEN = Screen()


class Environment(State):
    """Represent the environment with the rooms, dirt and jewels."""

    def __init__(self):
        self.things = []
        self.agent = None
        self.x_max = 5
        self.y_max = 5
        self.dirt_probability = 0.05
        self.jewel_probability = 0.02
        self.performance = 10

    def __eq__(self, other):
        if isinstance(other, Environment):
            return self.__hash__() == other.__hash__()
        raise NotImplementedError

    def __hash__(self):
        return hash(self.map())

    def run(self):
        """Run the environment."""
        while True:
            if random() <= self.dirt_probability:
                SCREEN.spawn_thing(self.generate_dirt())
            if random() <= self.jewel_probability:
                SCREEN.spawn_thing(self.generate_jewel())
            sleep(0.2)

    def something_at(self, location: Position, thing_class: List = None) -> Union[list[Thing], bool]:
        """
        Search for Thing or Agent at the given location.
        :param location: Location where to search.
        :param thing_class: Classes to search.
        :return:
        """
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

    def map(self) -> Tuple:
        """
        Get the map corresponding to the current state.
        :return: The map.
        """
        sensor_map = []
        for thing in self.things:
            sensor_map.append((thing.position.to_tuple(), "Dirt" if isinstance(thing, Dirt) else "Jewel"))
        if self.agent:
            return tuple([self.agent.position.to_tuple()] + sensor_map)
        return tuple(sensor_map)

    def nearest_dirt(self, agent: Agent) -> Tuple:
        """
        Get the nearest dirty room position.
        :param agent:
        :return: Position of the nearest dirty room.
        """
        def distance(t):
            return sqrt(pow(agent.position.x - t.position.x, 2) + pow(agent.position.y - t.position.y, 2))

        for thing in sorted(self.things, key=distance):
            if isinstance(thing, Dirt):
                return thing.position.x, thing.position.y

    def percept(self):
        return self

    def set_performance(self, performance: int, update_screen=False):
        """
        Set the performance of the agent.
        :param performance: Performance to set.
        :param update_screen: Update or not the GUI.
        :return:
        """
        self.performance = performance
        if update_screen:
            SCREEN.update_performance(performance)

    def execute_action(self, action: str, update_screen=False):
        """
        Execute the given action on the environment.
        :param action: Action to execute.
        :param update_screen: Update or not the GUI.
        :return:
        """
        if not isinstance(action, str):
            raise NotImplementedError

        if action == "Left" and self.agent.position.x > 0:
            self.agent.position.x -= 1
            self.set_performance(self.performance - 1, update_screen)
        elif action == "Right" and self.agent.position.x < self.x_max - 1:
            self.agent.position.x += 1
            self.set_performance(self.performance - 1, update_screen)
        elif action == "Up" and self.agent.position.y > 0:
            self.agent.position.y -= 1
            self.set_performance(self.performance - 1, update_screen)
        elif action == "Down" and self.agent.position.y < self.y_max - 1:
            self.agent.position.y += 1
            self.set_performance(self.performance - 1, update_screen)
        elif action == "Grab":
            deleted_things = self.delete_thing_at(self.agent.position, Jewel, update_screen)
            if Jewel in deleted_things:
                self.set_performance(self.performance + 10, update_screen)
        elif action == "Suck":
            deleted_things = self.delete_thing_at(self.agent.position, [Dirt, Jewel], update_screen)
            if Dirt in deleted_things:
                self.set_performance(self.performance + 5, update_screen)
            if Jewel in deleted_things:
                self.set_performance(self.performance - 1, update_screen)
        if update_screen:
            SCREEN.move_thing(self.agent)

    def random_location(self) -> Position:
        """
        Generate a random position on the map.
        :return: Random position.
        """
        x = randint(0, self.x_max - 1)
        y = randint(0, self.y_max - 1)
        return Position(x, y)

    def generate_dirt(self) -> Dirt:
        """
        Generate dirt at a random position.
        :return: Generated dirt.
        """
        position = self.random_location()
        while self.something_at(position, Dirt):
            position = self.random_location()
        return self.add_thing(Dirt(position))

    def add_thing(self, thing: Thing):
        """
        Add a Thing to the environment.
        :param thing: Thing to add.
        :return: Added thing.
        """
        if issubclass(type(thing), Agent):
            self.agent = thing
            self.agent.position = self.random_location()
            SCREEN.spawn_thing(thing)
            return self.agent
        elif isinstance(thing, Thing):
            self.things.append(thing)
            return thing
        raise NotImplementedError

    def delete_thing(self, thing_to_delete, update_screen=False):
        """
        Delete a thing.
        :param thing_to_delete:
        :param update_screen: Update or not the GUI.
        :return:
        """
        if thing_to_delete in self.things:
            if update_screen:
                SCREEN.delete_thing(thing_to_delete)
            self.things.remove(thing_to_delete)

    def delete_thing_at(self, position, things_class: Thing = Dirt, update_screen=False):
        """
        Delete a thing at a specific location.
        :param position: Position where to delete the specified classes.
        :param things_class: Classes to delete.
        :param update_screen: Update or not the GUI.
        :return:
        """
        if not isinstance(things_class, list):
            things_class = [things_class]
        for thing_class in things_class:
            things = self.something_at(position, thing_class)
            if things:
                self.delete_thing(things[0], update_screen)
                yield thing_class

    def generate_jewel(self) -> Jewel:
        """
        Generate a jewel at a random position.
        :return: Generated jewel.
        """
        position = self.random_location()
        while self.something_at(position, Jewel):
            position = self.random_location()
        return self.add_thing(Jewel(position))


class VacuumAgent(Agent, SimpleProblemSolvingAgentProgram):

    def __init__(self):
        Thing.__init__(self)
        SimpleProblemSolvingAgentProgram.__init__(self)
        self.alive = True
        self.performance = 0

    def update_state(self, state: State, percept) -> State:
        """
        Update the state in the agent memory with what the agent can perceive.
        :param state: State of the environment in the agent memory.
        :param percept: Percept.
        :return: New state in the agent memory.
        """
        return deepcopy(percept)

    def formulate_goal(self, state: State) -> any:
        """
        Formulate the goal of the agent.
        :param state: Environment state in agent memory.
        :return: Goal.
        """
        goal = deepcopy(state)
        return goal.map()[0]

    def formulate_problem(self, state: State, goal) -> any:
        """
        Formulate the problem.
        :param state: Environment state in agent memory.
        :param goal: Goal.
        :return: Formulated problem.
        """
        problem = VacuumProblem(state, goal)
        return problem

    def search(self, problem: Problem) -> List[str]:
        """
        Search for a solution to the given problem.
        :param problem: Given problem.
        :return: A sequence of actions.
        """
        print("Searching for a solution")
        final_node = astar(problem)
        seq = Node.action_sequence(final_node)
        if seq:
            print("Solution found : %s" % seq)
        return seq
