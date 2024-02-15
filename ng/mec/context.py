from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mec.entity import Entity
    from mec.service import Service
    from ng.simulation import Simulation

from typing import Optional
import simpy

# this class represents an interface between entity and service
# when migrating, the context manages seamless switching

class Context:

    def __init__(self, sim: Simulation, service: Service):
        self.sim = sim
        self.entity: Optional[Entity] = None
        self.service = service

        self.fw_proc: Optional[simpy.Process] = None

        self.proc_q = simpy.Store(self.sim.env)
        self.send_q = simpy.Store(self.sim.env)
        self.recv_q = simpy.Store(self.sim.env)

    def _forward_process(self):
        def compute():
            try:
                while True:
                    [comp, ev] = yield self.proc_q.get()
                    yield self.entity.compute(comp)
                    ev.succeed()
            except simpy.Interrupt:
                pass

        def send_msgs():
            try:
                while True:
                    [msg, ev] = yield self.proc_q.get()
                    yield self.entity.send_msg(msg)
                    ev.succeed()
            except simpy.Interrupt:
                pass

        procs = [self.sim.env.process(compute()), self.sim.env.process(send_msgs())]

        try:
            yield simpy.AllOf(self.sim.env, procs)
        except simpy.Interrupt:
            for proc in procs:
                proc.interrupt()

    def compute(self, computation):
        # registers computation for processing
        # will wait for entity.process
        # may be interrupted by unbind, then restarts the computation once bound again
        ev = simpy.Event(self.sim.env)
        self.proc_q.put([computation, ev])
        return ev  # yield compute()

    def send_message(self, msg):
        ev = simpy.Event(self.sim.env)
        self.send_q.put([msg, ev])
        return ev  # s.t. you can yield send_message

    def recv_message(self):
        return self.recv_q.get()  # yield recv_message

    def bind_to_entity(self, entity):
        self.entity = entity
        self.fw_proc = self.sim.env.process(self._forward_process())

    def unbind(self):
        self.fw_proc.interrupt()
        self.entity = None
