from abc import ABC, abstractmethod

import simpy

from networking.interface.frame import Frame
from ng.simulation import Simulation


# mix of L1 and L2 (modelling physical latency but also managing node-to-node connectivity)

class Connection(ABC):

    # proxy element for each individual interface
    class End:

        def __init__(self, conn: "Connection", intf):
            self.conn = conn
            self.intf = intf

        def down(self):
            self.conn.disconnect(self.intf)

        def send(self, frame):
            yield self.conn.transfer(self.intf, frame)

    def __init__(self, sim: Simulation, ifs: "Interface"):
        ifs = list(ifs)
        self.sim = sim
        self.env = sim.env
        self.network = sim.network
        self.ifs = []
        self.q = simpy.Store(self.env)
        self.proc = self.env.process(self.transfer_frames())

        for intf in ifs:
            self.connect(intf)

    def _link(self, if0, if1):
        self.network.link(if0, if1)

    def _unlink(self, if0, if1):
        self.network.unlink(if0, if1)

    def connect(self, intf):
        if not self._is_compatible(intf):
            raise TypeError("Interface not compatible")
        if intf in self.ifs:
            raise RuntimeError("Already connected")
        self._handle_new_if(intf)  # adds links
        intf.connect(Connection.End(self, intf))
        self.ifs.append(intf)

    def disconnect(self, intf):
        if intf not in self.ifs:
            raise RuntimeError("Not connected")
        self._handle_remove_if(intf)  # removes links
        intf.handle_unlink()
        self.ifs.remove(intf)

        # if len(ifs) == 1: no connection exists => remove
        if len(self.ifs) == 1:
            self.disconnect(self.ifs[0])

    @abstractmethod
    def _handle_new_if(self, intf):
        pass

    @abstractmethod
    def _handle_remove_if(self, intf):
        pass

    @abstractmethod
    def _is_compatible(self, interface):
        pass

    def transfer(self, if0, frame: Frame):
        ev = simpy.Event(self.env)
        self.q.put([ev, if0, frame])
        return ev

    # todo: abstract this as serialconnection
    def transfer_frames(self):
        while True:
            [ev, from_if, frame] = yield self.q.get()
            yield self.env.process(self.transfer_frame(from_if, frame))
            ev.succeed()

    @abstractmethod
    def transfer_frame(self, if0, frame: Frame):
        pass
