from ng.networking.interface.base import Interface
import simpy
from ng.networking.interface.connection import Connection


class RadioInterface(Interface):

    def __init__(self, sim, id):
        super().__init__(sim, id)


class RadioConnection(Connection):

    def __init__(self, sim, *ifs):
        super().__init__(sim, *ifs)

    def _is_compatible(self, interface):
        return isinstance(interface, RadioInterface)

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

    def transfer(self, from_if_idx, frame):
        yield self.env.timeout(5)
        yield simpy.AllOf(self.env, [intf.inbuf.put(frame) for intf in self.ifs if intf != self.ifs[from_if_idx]])
