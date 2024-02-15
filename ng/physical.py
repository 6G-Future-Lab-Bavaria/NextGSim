import math
import typing
from abc import ABC, abstractmethod
from ng.physical_node import PhysicalNode


class Coords(ABC):

    @abstractmethod
    def get_dist(self, other):
        pass

    @abstractmethod
    def serialize(self):
        pass


class Coords2D(Coords):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_dist(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def serialize(self):
        return { "x": self.x, "y": self.y }

# must be able to extend to 3 dims

class PhysicalEnvironment:

    def __init__(self, lower_corner: Coords, higher_corner: Coords):
        self.lower_corner = lower_corner
        self.higher_corner = higher_corner
        self.nodes: typing.List[PhysicalNode] = []

    def dist(self, c0: Coords, c1: Coords):
        return c0.get_dist(c1)


