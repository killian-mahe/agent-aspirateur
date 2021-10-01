from time import sleep
import sys

from environment import Environment, Dirt, Jewel, Position, VacuumAgent, SCREEN

from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView
from PyQt5.QtCore import QThread, QRectF, Qt, QPointF
from PyQt5.QtGui import QBrush, QPolygonF, QPen

sys.setrecursionlimit(10000)


class EnvironmentThread(QThread):

    def __init__(self, environment: Environment):
        QThread.__init__(self)
        self.environment = environment

    def run(self):
        self.environment.run()


class AgentThread(QThread):

    def __init__(self, agent, environment):
        QThread.__init__(self)
        self.environment = environment
        self.agent = agent

    def run(self):
        while self.agent.alive:
            print(self.agent.position)
            print(self.environment.map())
            seq = self.agent(self.environment.percept())
            if seq:
                self.environment.execute_action(seq, True)

            sleep(0.1)


def convert_position(position: Position):
    return Position(100 * position.x + 50, 100 * position.y + 50)


class Window(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.central_widget = self.centralWidget()
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        self.environment = Environment()
        self.agent = VacuumAgent()

        self.env_thread = EnvironmentThread(self.environment)
        self.env_thread.finished.connect(app.exit)

        self.agent_thread = AgentThread(self.agent, self.environment)

        SCREEN.thing_spawn.connect(self.spawn_handler)
        SCREEN.thing_deleted.connect(self.deleted_thing_handler)
        SCREEN.thing_moved.connect(self.moved_handler)

        self.dirt_rects = []
        self.jewel_rects = []
        self.agent_rect = None

        self.setup_ui()
        self.view.show()

        self.environment.add_thing(self.agent)

        self.env_thread.start()
        self.agent_thread.start()

    def moved_handler(self, thing):
        if isinstance(thing, VacuumAgent):
            self.draw_agent(thing.position)
        else:
            raise NotImplementedError

    def spawn_handler(self, thing):
        if isinstance(thing, Dirt):
            self.draw_dirt(thing.position)
        elif isinstance(thing, Jewel):
            self.draw_jewel(thing.position)
        elif isinstance(thing, VacuumAgent):
            self.draw_agent(thing.position)

    def deleted_thing_handler(self, thing):
        position = convert_position(thing.position)
        if isinstance(thing, Dirt):
            for i in range(0, len(self.dirt_rects)):
                if self.dirt_rects[i].contains(QPointF(position.x, position.y)):
                    self.scene.removeItem(self.dirt_rects.pop(i))
                    return
        elif isinstance(thing, Jewel):
            for i in range(0, len(self.jewel_rects)):
                if self.jewel_rects[i].contains(QPointF(position.x, position.y)):
                    self.scene.removeItem(self.jewel_rects.pop(i))
                    return

    def draw_jewel(self, position: Position):
        position = convert_position(position)
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(Qt.cyan)

        self.jewel_rects.append(self.scene.addPolygon(QPolygonF([
            QPointF(position.x - 10, position.y),
            QPointF(position.x, position.y - 10),
            QPointF(position.x + 10, position.y),
            QPointF(position.x, position.y + 20)
        ]), brush=brush))

    def draw_dirt(self, position: Position):
        position = convert_position(position)
        brush = QBrush()
        brush.setStyle(Qt.Dense5Pattern)
        brush.setColor(Qt.gray)
        self.dirt_rects.append(self.scene.addRect(QRectF(position.x - 50, position.y - 50, 100, 100),
                                                  brush=brush))

    def draw_agent(self, position: Position):
        position = convert_position(position)
        pen = QPen()
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(3)
        pen.setColor(Qt.red)
        if self.agent_rect:
            self.agent_rect.setRect(QRectF(position.x - 40, position.y - 40, 80, 80))
        else:
            self.agent_rect = self.scene.addRect(QRectF(position.x - 40, position.y - 40, 80, 80),
                                                 pen=pen)

    def setup_ui(self):
        self.setWindowTitle("Vacuum Agent")
        self.resize(1000, 800)
        self.setCentralWidget(self.view)

        # Build scene
        self.scene.addRect(QRectF(0, 0, 500, 500))

        for y in range(0, self.environment.y_max):
            for x in range(0, self.environment.x_max):
                self.scene.addRect(QRectF(100 * x, 100 * y, 100, 100))


app = QApplication(sys.argv)
win = Window()
win.show()
sys.exit(app.exec())
