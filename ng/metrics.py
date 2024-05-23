import io
from abc import ABC, abstractmethod
from numbers import Number
import json
import numpy as np

from typing import List, Tuple, Any

class MetricViewGenerator(ABC):

    @staticmethod
    @abstractmethod
    def generate_view(metric: "Metric", from_ts: float, to_ts: float, **kwargs) -> [str, any]:
        pass


class SimpleScalarViewGenerator(MetricViewGenerator):
    COMPONENT = "BinnedTimeseriesViewer"

    # Discretises time series in bin_count blocks, returns min, mean and max for each, n for each
    # kwargs contains bin_count
    @staticmethod
    def generate_view(values: List[Tuple[float, float]], from_ts: float, to_ts: float, **kwargs) -> [str, any]:
        if len(values) == 0:
            return [SimpleScalarViewGenerator.COMPONENT, None]

        arr = np.array(values)
        in_bounds = (arr[:,0] >= from_ts) & (arr[:,0] <= to_ts)
        arr = arr[in_bounds]

        bin_count: int = int(kwargs["bin_count"])

        bins = np.linspace(from_ts, to_ts, bin_count - 1)
        indices = np.digitize(arr[:,0], bins)

        binned = []

        for b in range(bin_count):
            vals: np.ndarray = arr[indices == b, 1]
            if vals.size == 0:
                min, max, mean = None,None,None
            else:
                min = vals.min()
                max = vals.max()
                mean = vals.mean()
            binned.append({
                "from_ts": bins[b-1] if b > 0 else None,
                "to_ts": bins[b] if b < bin_count-1 else None,
                "count": vals.size,
                "min": min,
                "max": max,
                "mean": mean,
            })

        return [SimpleScalarViewGenerator.COMPONENT, binned]


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

    # This method is used by the frontend in order. In order not to overload the frontend (and possibly
    # the network connection), metrics shall be filtered and reduced at the server side to send a possibly
    # coarsened view on the data to be rendered by the frontend.
    # Returns the view as well as an identifier for the component that should be used to render the view
    @staticmethod
    @abstractmethod
    def generate_view(values, from_ts, to_ts, **kwargs) -> [str, any]:
        pass

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

    def get_values(self) -> List[Tuple[float, float]]:
        return self.values

    @staticmethod
    def generate_view(values, from_ts, to_ts, **kwargs):
        return SimpleScalarViewGenerator.generate_view(values, from_ts, to_ts, **kwargs)

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

    def get_values(self) -> List[Tuple[float, float]]:
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
    def generate_view(values, from_ts, to_ts, **kwargs):
        return SimpleScalarViewGenerator.generate_view(values, from_ts, to_ts, **kwargs)

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
