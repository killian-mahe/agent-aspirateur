from numpy import sqrt, power
import random


class Thing:
    """This represents any physical object that can appear in an Environment.
    You subclass Thing to get the things you want. Each thing can have a
    .__name__  slot (used for output only)."""

    def __repr__(self):
        return '<{}>'.format(getattr(self, '__name__', self.__class__.__name__))

    def show_state(self):
        """Display the agent's internal state. Subclasses should override."""
        print("I don't know how to show_state.")

    def display(self, canvas, x, y, width, height):
        """Display an image of this Thing on the canvas."""
        # Do we need this?
        pass


class Dirt(Thing):
    pass


class Jewel(Thing):
    pass


class Agent(Thing):
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

    def __init__(self, program=None):
        self.alive = True
        self.bump = False
        self.holding = []
        self.performance = 0
        if program is None:
            print("Can't find a valid program for {}, falling back to default.".format(self.__class__.__name__))

            def program(percept):
                return eval(input('Percept={}; action? '.format(percept)))

        self.program = program

    def can_grab(self, thing):
        """Return True if this agent can grab this thing.
        Override for appropriate subclasses of Agent and Thing."""
        return False


class Environment:
    """Abstract class representing an Environment. 'Real' Environment classes
    inherit from this. Your Environment will typically need to implement:
        percept:           Define the percept that an agent sees.
        execute_action:    Define the effects of executing an action.
                           Also update the agent.performance slot.
    The environment keeps a list of .things and .agents (which is a subset
    of .things). Each agent has a .performance slot, initialized to 0.
    Each thing has a .location slot, even though some environments may not
    need this."""

    def __init__(self, width=25, height=25):
        self.things = []
        self.agents = []
        self.width = width
        self.height = height

    perceptible_distance = 1

    def things_near(self, location, radius=None):
        radius = self.perceptible_distance if radius is None else self.perceptible_distance
        return [thing for thing in self.things
                if sqrt(power(location[0]-thing.location[0], 2) + power(location[1]-thing.location[1], 2)) <= radius]

    def thing_classes(self):
        return [Dirt, Jewel, Agent]  # List of classes that can go into environment

    def percept(self, agent):
        """Return the percept that the agent sees at this point."""
        return 'Dirty' if self.some_things_at(agent.location, Dirt) else 'Clean'

    def execute_action(self, agent, action):
        """Change the world to reflect this action. (Implement this.)"""
        raise NotImplementedError

    def default_location(self, thing):
        """Default location to place a new thing with unspecified location."""
        location = self.random_location_inbounds()
        while self.some_things_at(location, Thing):
            location = self.random_location_inbounds()
        return location

    def is_inbounds(self, location):
        """Checks to make sure that the location is inbounds (within walls if we have walls)"""
        x, y = location
        return not (x < 0 or x > self.width or y < 0 or y > self.height)

    def random_location_inbounds(self, exclude=None):
        """Returns a random location that is inbounds."""
        location = (random.randint(0, self.width),
                    random.randint(0, self.height))
        if exclude is not None:
            while location == exclude:
                location = (random.randint(0, self.width),
                            random.randint(0, self.height))
        return location

    def exogenous_change(self):
        """If there is spontaneous change in the world, override this."""
        pass

    def step(self):
        """Run the environment for one time step. If the
        actions and exogenous changes are independent, this method will
        do. If there are interactions between them, you'll need to
        override this method."""
        actions = []
        for agent in self.agents:
            if agent.alive:
                actions.append(agent.program(self.percept(agent)))
            else:
                actions.append("")
        for (agent, action) in zip(self.agents, actions):
            self.execute_action(agent, action)
        self.exogenous_change()

    def run(self, steps=1000):
        """Run the Environment for given number of time steps."""
        for step in range(steps):
            self.step()

    def list_things_at(self, location, tclass=Thing):
        """Return all things exactly at a given location."""
        return [thing for thing in self.things
                if all(x == y for x, y in zip(thing.location, location)) and isinstance(thing, tclass)]

    def some_things_at(self, location, tclass=Thing):
        """Return true if at least one of the things at location
        is an instance of class tclass (or a subclass)."""
        return self.list_things_at(location, tclass) != []

    def add_thing(self, thing, location=None):
        """Add a thing to the environment, setting its location. For
        convenience, if thing is an agent program we make a new agent
        for it. (Shouldn't need to override this.)"""
        if not isinstance(thing, Thing):
            thing = Agent(thing)
        if thing in self.things:
            print("Can't add the same thing twice")
        else:
            thing.location = location if location is not None else self.default_location(thing)
            self.things.append(thing)
            if isinstance(thing, Agent):
                thing.performance = 0
                self.agents.append(thing)

    def delete_thing(self, thing):
        """Remove a thing from the environment."""
        if thing in self.agents:
            self.agents.remove(thing)
