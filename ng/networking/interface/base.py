import simpy
from typing import Optional
from abc import ABC

from metrics import ScalarMetric, IntegratedScalarMetric
from ng.networking.node import Node
from ng.networking.interface.connection import Connection
from ng.simulation import Simulation
from ng.networking.interface.frame import Frame

# interface can have one or multiple links
# => links only 1:1
# BUS, MIMO same abstraction (interface differentiates)
# => link is created when two interfaces are connected to the same "thing"
# "thing": eg cable, switch, radio channel,
# modeled as an edge in network graph

# physical
# Connection
# - handles physical transfer, time slicing, syncing etc
# - 1 connection : n interfaces
# - can add / remove interfaces
# - is the "thing" from above
# - adds / removes links => needs access to network graph
# user defined transfer function to transfer from if0 to if1

# interface.send(mgs) calls connection.transfer
# connection is created by something else, eg through SD-RAN controller or from simulation config
# Connection(if0, if1)
# connection checks if intefaces are compatible using inheritance
#


# receives and returns packets (not frames)

class Interface(ABC):

    def __init__(self, sim: Simulation, id):
        self.node: Optional[Node] = None
        self.id = id
        self.sim = sim
        self.env = sim.env
        self.conn: Optional[Connection.End] = None
        self.recv_proc = None
        self.inbuf = simpy.Store(self.env)  # interfaces buffer messages, could be modeled differently ...
        self.up_ev = simpy.Event(self.env)
        self.m_tx = IntegratedScalarMetric(self.sim, self, "TX")
        self.m_rx = IntegratedScalarMetric(self.sim, self, "RX")

    def __repr__(self):
        return "%s.if%s" % (self.node, self.id)

    def bind_to_node(self, node):
        if self.node is not None:
            raise RuntimeError("Interface already bound")
        self.node = node

    def connect(self, conn: Connection.End):
        self.conn = conn
        self.up_ev.succeed()
        self.sim.eventlog.register_event(self, "UP")

    def wait_for_up(self):
        if self.conn is not None:
            return
        yield self.up_ev

    # called by connection
    def handle_unlink(self):
        self.conn = None
        if self.recv_proc:
            self.recv_proc.interrupt()
            self.recv_proc = None
        self.up_ev = simpy.Event(self.env)
        self.sim.eventlog.register_event(self, "DOWN")

    def disconnect(self):
        self.conn.down()

    def recv(self):
        def receive_data():
            frame = yield self.inbuf.get()
            self.m_rx.record(frame.size)
            data = frame.data

            while not frame.is_last:
                frame = yield self.inbuf.get()
                if frame.data != data:
                    raise RuntimeError("Missing packet for data " + str(data))

            return data

        self.recv_proc = self.env.process(receive_data())
        packet = yield self.recv_proc
        self.sim.eventlog.register_event(self, "PACKET_RECV", str(packet))
        return packet

    def send(self, packet, size, if1):
        if self.conn is None:
            raise ConnectionError("Interface down")
        for frame in self._frames_from_packet(packet, size, if1):
            self.env.process(self.conn.send(frame))
            self.m_tx.record(frame.size)
        self.sim.eventlog.register_event(self, "PACKET_SENT", str(packet))
        yield simpy.Event(self.env).succeed()

    # this method can be overwritten to use custom frames
    # actually, does this even make sense? e.g. shouldn't the upstream make sure packet fits into single frame
    def _frames_from_packet(self, data, size, if1):
        return [Frame(self.id, if1, size, 0, True, data)]
