import io
from abc import ABC, abstractmethod
from numbers import Number
import json

from typing import List, Tuple, Any


class Metric(ABC):

    def __init__(self, sim, comp, name):
        self.sim = sim
        sim.metric_writer.register_metric(self)
        self.comp = comp
        self.name = name
        self.values = []

    def __repr__(self):
        return "Metric[%s, %s]" % (self.comp, self.name)

    def record(self, value):
        t = self.sim.now()
        self.values.append([t, value])

    @abstractmethod
    # must return values in some standard form ... to be displayed, or have some visualize method?
    def get_values(self) -> List[Tuple[Number, Any]]:
        pass

    @staticmethod
    @abstractmethod
    def serialize_values(f: io.IOBase, values: List[Tuple[Number, Any]]):
        pass

    # must not contain a ','
    @staticmethod
    @abstractmethod
    def deserialize_values(f: io.IOBase) -> List[Tuple[Number, Any]]:
        pass


class FloatMetric(Metric):

    def __init__(self, sim, comp, name):
        super().__init__(sim, comp, name)

    def get_values(self):
        return self.values

    @staticmethod
    def serialize_values(f: io.IOBase, values: List[Tuple[Number, Any]]):
        json.dump(values, f)

    @staticmethod
    def deserialize_values(f: io.IOBase) -> List[Tuple[Number, Any]]:
        return json.load(f)

class IntegratedFloatMetric(Metric):

    def __init__(self, sim, comp, name):
        super().__init__(sim, comp, name)
        self.d_x = 5

    def get_values(self):
        if (self.values == []):
            return self.values

        minT = min([el[0] for el in self.values])
        maxT = max([el[0] for el in self.values])

        vals_integrated = []

        v = self.values

        t = minT
        while t <= maxT:
            currY = 0
            if len(v) > 0 and v[0][0] < t:
                currY += v[0][1]
                v = v[1:]
            vals_integrated.append([t, currY])
            t += self.d_x

        return vals_integrated

    @staticmethod
    def serialize_values(f: io.IOBase, values: List[Tuple[Number, Any]]):
        json.dump(values, f)

    @staticmethod
    def deserialize_values(f: io.IOBase) -> List[Tuple[Number, Any]]:
        return json.load(f)

class MetricWriter:

    def __init__(self, sim):
        self.metrics = []
        self.sim = sim

    def register_metric(self, metric):
        self.metrics.append(metric)
