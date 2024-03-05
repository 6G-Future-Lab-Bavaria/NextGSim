# device has CPU, Interfaces
# children are UEs, Sensors, EdgeServers, Routers, ...
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ng.simulation import Simulation
    from ng.networking.interface.base import Interface

import simpy
from ng.networking.packet import Packet


class Node:

    def __init__(self, sim: Simulation, id, ifs):
        self.sim = sim
        self.env = sim.env
        self.id = id
        self.net_proc = self.env.process(self._handle_networking())
        self.interfaces = {}
        sim.network.register_node(self)
        self.routing_table = sim.routing.get_routing_table(self.id)
        self.incoming_packets = simpy.Store(self.env)

        if ifs is not None:
            for intf in ifs:
                self.attach_if(intf)

    def __repr__(self):
        return "n%s" % self.id

    def __del__(self):
        self.sim.network.remove_node(self.id)

    def attach_if(self, interface):
        idx = len(self.interfaces)
        self.interfaces[interface.id] = interface
        interface.bind_to_node(self)
        return interface.id

    def intf(self, intf_id) -> Interface:
        return self.interfaces[intf_id]

    def get_active_interfaces(self):
        return [intf for intf in self.interfaces if intf.link is not None]

    def _recv_data(self):                   # actually, would need to assemble data
        packet = yield self.incoming_packets.get()
        return packet.data

    def _send_data(self, n1, data, size):   # actually, would need to split into multiple packets here
        packet = Packet(self.id, n1, size, 0, True, data)
        return self._send_packet(packet)

    def _send_packet(self, packet):
        n1  = packet.node1
        link = self.routing_table.get_next_hop(n1)  # l3 -> l2

        if link is None:
            # todo: no error, but record event, return normally
            raise RuntimeError("No route from %s to %s" % (self.id, n1))

        [if0, if1] = link
        intf = self.intf(if0)
        return self.env.process(intf.send(packet, packet.size, if1))  # TODO: yield or not?

    # this process receives l3 packets and either forwards them to the next node
    # or puts them in self.incoming_packets
    def _handle_networking(self):
        def handle(intf_id):
            while True:
                yield self.env.process(self.interfaces[intf_id].wait_for_up())

                try:
                    packet: Packet = yield self.env.process(self.intf(intf_id).recv())
                except simpy.Interrupt:  # unlink while recv
                    continue

                if packet.node1 == self.id:
                    yield self.incoming_packets.put(packet)
                    continue

                # otherwise, forward

                print("%d [%s] forwarding packet from %s to %s" %
                      (self.env.now, self.id, packet.node0, packet.node1))
                try:
                    yield self._send_packet(packet)
                except RuntimeError as e:
                    print("Failed to forward packet")

        self.procs = [self.env.process(handle(intf_id)) for intf_id in self.interfaces.keys()]

        yield simpy.AllOf(self.env, self.procs)
