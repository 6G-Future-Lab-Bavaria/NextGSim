from abc import ABC, abstractmethod

class Metric(ABC):

    def __init__(self, sim, comp, name):
        self.sim = sim
        sim.metric_writer.register_metric(self)
        self.comp = comp
        self.name = name

    def __repr__(self):
        return "Metric[%s, %s]" % (self.comp, self.name)

    @abstractmethod
    def record(self, value):
        pass

    @abstractmethod
    # must return values in some standard form ... to be displayed, or have some visualize method?
    def get_values(self):
        pass


class ScalarMetric(Metric):

    def __init__(self, sim, comp, name):
        super().__init__(sim, comp, name)
        self.values = []

    def record(self, value):
        self.values.append([self.sim.now(), value])

    def get_values(self):
        return self.values

class IntegratedScalarMetric(Metric):

    def __init__(self, sim, comp, name):
        super().__init__(sim, comp, name)
        self.values = []
        self.d_x = 5

    def record(self, value):
        self.values.append([self.sim.now(), value])

    def get_values(self):
        if (self.values == []):
            return self.values

        minX = min([el[0] for el in self.values])
        maxX = max([el[0] for el in self.values])

        vals_integrated = []

        v = self.values

        i = minX
        while i <= maxX:
            currY = 0
            if len(v) > 0 and v[0][0] < i:
                currY += v[0][1]
                v = v[1:]
            vals_integrated.append([i, currY])
            i += self.d_x

        return vals_integrated

class MetricWriter:

    def __init__(self, sim):
        self.metrics = []
        self.sim = sim

    def register_metric(self, metric):
        self.metrics.append(metric)
