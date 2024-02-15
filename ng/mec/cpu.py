from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mec.entity import Entity
    from mec.computation import Computation

from abc import ABC, abstractmethod
import simpy

# class models (singular) compute unit of a device
# could model multiple cores, threads etc


class CPU(ABC):

    def __init__(self, entity: Entity):
        self.sim = entity.sim
        self.proc_q = simpy.Store(self.sim.env)
        self.process = self.sim.env.process(self.run())

    def compute(self, computation: Computation):
        ev = simpy.Event(self.sim.env)
        self.proc_q.put([computation, ev])
        return ev

    # this method must implement an infinite loop waiting for computatinos in proc_q and processing them accordingly
    # upon completion, the corresponding event shall be raised
    @abstractmethod
    def run(self):
        pass


class SimpleSingleThreadedCPU(CPU):

    def __init__(self, clock_speed: float, entity):
        super().__init__(entity)
        self.clock_speed = clock_speed

    # clock_speed = cycles per second
    @staticmethod
    def create_type(clock_speed):
        return lambda entity: SimpleSingleThreadedCPU(clock_speed, entity)

    def run(self):
        while True:
            [comp, ev] = yield self.proc_q.get()
            cycles = comp.cycles
            seconds = cycles / self.clock_speed
            yield self.sim.wait_ms(seconds * seconds)
            comp.remaining_cycles = 0
            ev.succeed()
