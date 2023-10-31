"""
This service is a generic class to introduce whatever kind of generation_distribution in the simulator

"""
import random
import numpy as np
import warnings


class Distribution(object):
    """
    Abstract class
    """

    def __init__(self, name):
        self.name = name

    def next(self):
        None


class DeterministicDistribution(Distribution):
    def __init__(self, name=None, period=10):
        super().__init__(name)
        self.period = period

    def next(self):
        return self.period


class DeterministicDistributionWithStartingTime(Distribution):
    def __init__(self, starting_time, period, name=None):
        self.starting_time = starting_time
        self.time = period
        self.active = False
        self.name = name
        super(DeterministicDistributionWithStartingTime, self).__init__(name)

    def next(self):
        if not self.active:
            self.active = True
            return self.starting_time
        else:
            return self.time


class ExponentialDistribution(Distribution):
    def __init__(self, lambd, seed=1, **kwargs):
        super(ExponentialDistribution, self).__init__(**kwargs)
        self.lambd = lambd
        self.rnd = np.random.RandomState(seed)

    def next(self):
        value = int(self.rnd.exponential(self.lambd, size=1)[0])
        if value == 0:
            return 1
        return value


class ExponentialDistributionWithStartingPoint(Distribution):
    def __init__(self, start, lambd, **kwargs):
        self.lambd = lambd
        self.start = start
        self.started = False
        super(ExponentialDistributionWithStartingPoint, self).__init__(**kwargs)

    def next(self):
        if not self.started:
            self.started = True
            return self.start
        else:
            return int(np.random.exponential(self.lambd, size=1)[0])


class UniformDistribution(Distribution):
    def __init__(self, min, max, **kwargs):
        self.min = min
        self.max = max
        super(UniformDistribution, self).__init__(**kwargs)

    def next(self):
        return random.randint(self.min, self.max)
