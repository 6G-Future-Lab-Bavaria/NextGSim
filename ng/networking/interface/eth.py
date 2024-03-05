from metrics import ScalarMetric
from networking.interface.frame import Frame
from ng.networking.interface.base import Interface
import simpy
from ng.networking.interface.connection import Connection
from abc import abstractmethod

class EthernetInterface(Interface):

    def __init__(self, sim, id):
        super().__init__(sim, id)


class EthernetConnection(Connection):

    def __init__(self, sim, ifs):
        super().__init__(sim, ifs)

    def _is_compatible(self, interface):
        return isinstance(interface, EthernetInterface)

    def _handle_new_if(self, intf):
        for if1 in self.ifs:
            self._link(intf, if1)
            self._link(if1, intf)

    def _handle_remove_if(self, intf):
        for if1 in self.ifs:
            if if1 == intf:
                continue
            self._unlink(intf, if1)
            self._unlink(if1, intf)

        # todo: we need to manage connections in network object or somewhere
        # so that we can add ifs to them and remove if interface count is 1


class FiberConnection(EthernetConnection):

    def __init__(self, sim, length, ifs):
        super().__init__(sim, ifs)
        self.bw = 10e9                          # 1 Gbps
        self.latency = 0.00333 * length         # milliseconds per meter * meter = ms

    # note: not modelled correctly: multiple frames can overlap, but latency is always 100%
    def transfer_frame(self, from_if, frame: Frame):
        bits = frame.size
        transmit = (bits / self.bw) * 1e3       # milliseconds
        propagation = self.latency              # milliseconds
        latency = transmit + propagation
        yield self.sim.wait_ms(latency)
        yield simpy.AllOf(self.env, [intf.inbuf.put(frame) for intf in self.ifs if intf != from_if])
