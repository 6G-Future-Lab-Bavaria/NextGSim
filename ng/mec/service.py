from __future__ import annotations
from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from ng.simulation import Simulation

from abc import ABC, abstractmethod
from typing import List
from simpy import Store

from mec.computation import Computation
from mec.context import Context
from mec.message import Message

# service is bound to node (active) or not
# if a service is inactive, no messages will recvd, sent or computation processed
# the run process will still continue! (but theoretically, it shouldn't be able to do anything)

# abstractly, the service is a process that can
# - send messages to other types of services
# - receive messages from other types of services
# - process a computation

# these three things are called context
# if the service is migrated, the context must be seamlessly migrated
# i.e. yield proc_f() must still return once new instance is done

# a service can simpy be identified by type (i.e. all instances in the network are considered same)
# or as service.instance => e.g. if we want to model some form of statefulness
# however, this is determined by the orchestrator and the run() function, so we dont care
# just need to be careful: entity can host multiple instances => here id must differentiate

# todo: actually, id should be reserved for global (simulation) id ...
# then consider some "address" or port for routing

class Service(ABC):

    def __init__(self, sim: Simulation, id):
        self.id = id
        self.sim = sim
        self.proc_q: Store[Computation] = Store(sim.env)
        self.network_q: Store[Message] = Store(sim.env)
        self.context = Context(sim, self)
        self.process = sim.env.process(self.run())

    @abstractmethod
    def get_dependencies(self) -> List[Type[Service]]:
        pass

    def send_message(self, msg):
        yield self.context.send_message(msg)

    def recv_message(self) -> Message:
        yield self.context.recv_message()

    def compute(self, comp: Computation):
        yield self.context.compute(comp)

    # process that is this app
    @abstractmethod
    def run(self):
        pass


class ExampleGen(Service):

    def get_dependencies(self) -> List[Type[Service]]:
        return [ GW ]

    def run(self):
        while True:
            yield self.sim.wait_ms(50)
            msg = Message(ExampleGen, GW, 10, "Hello")
            yield self.send_message(msg)
            print("Example msg sent:", msg)


class ExampleProc(Service):

    def get_dependencies(self) -> List[Type[Service]]:
        return []

    def run(self):
        while True:
            msg: Message = yield self.recv_message()
            print("Example msg recv:", msg)
            yield self.compute(Computation(100))
            # yield self.send_message(Message(self.id, msg.sender, 10, "hello"))

class GW(Service):

    def __init__(self):
        self.mapping = {}

    def get_dependencies(self) -> List[Type[Service]]:
        return [ExampleProc]

    def run(self):
        while True:
            msg = yield self.recv_message()
            newMsg = Message(msg.sender, istance, msg.data)


