from mesa import Agent, Model
from mesa.time import BaseScheduler
from mesa.space import Grid
from random import randint
import random
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


class Animal(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.group = None

    def move(self):
        possible_moves = self.model.grid.get_neighborhood(self.pos, moore=False)
        while True:
            next_move = random.choice(possible_moves)
            if self.model.grid.is_cell_empty(next_move):
                break
        self.model.grid.move_agent(self, next_move)

    def step(self, v=None):
        if v is None:
            self.move()
            for i in self.model.grid.get_neighbors(self.pos, moore=False):
                if i is not None:
                    if i.group is None:
                        self.group = self.model.schedule.groups + 1
                        i.group = self.model.schedule.groups + 1
                        self.model.schedule.groups += 1
                    else:
                        self.group = i.group
        else:
            self.model.grid.move_agent(self, tuple(map(lambda l, k: l + k, self.pos, v)))


class Scheduler(BaseScheduler):
    def __init__(self, model):
        super().__init__(model)
        self.groups = 0

    def step(self):
        for a in self.agents:
            if a.group is None:
                a.step()
        for g in range(1, self.groups):
            v = random.choice([(0, 0), (1, 0), (0, 1), (1, 1)])
            for a in self.agents:
                if a.group == g:
                    a.step(v)


class WalkingModel(Model):
    def __init__(self, agent_number):
        self.agent_number = 40
        self.width = agent_number
        self.height = agent_number
        self.schedule = Scheduler(self)
        self.grid = Grid(self.width, self.height, True)
        self.running = True
        for i in range(self.agent_number):
            while True:
                x = randint(0, self.width - 1)
                y = randint(0, self.height - 1)
                if self.grid.is_cell_empty((x, y)):
                    break
            a = Animal(model=self, pos=(x, y), unique_id=i)
            self.schedule.add(a)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()
        for a in self.schedule.agents:
            print(a.group)


def agent_portrayal(agent):
    if agent is None:
        return
    portrayal = {"Shape": "rect",
                 "w": 0.5,
                 "h": 0.5,
                 "Filled": "true",
                 "Color": "blue",
                 "Layer": 1}
    if agent.group is not None:
        portrayal["text"] = round(agent.group, 10)
        portrayal["text_color"] = "Black"

    return portrayal


element = CanvasGrid(agent_portrayal, 100, 100, 800, 800)
server = ModularServer(WalkingModel,
                       [element],
                       "WalkingModel",
                       {"agent_number": 100})

server.port = 8606
server.launch()

