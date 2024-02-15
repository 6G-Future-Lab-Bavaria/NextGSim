from __future__ import annotations
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from mec.service import Service
    from mec.message import Message
    from mec.computation import Computation
    from mec.cpu import CPU

from typing import Dict
from networking.node import Node

# and entity has a CPU, and possibly other resources and is also part of the network


class Entity(Node):

    def __init__(self, sim, id, cpu_t: Type[CPU]):
        super().__init__(sim, id)
        self.deployed_services: Dict[str, Service] = {}
        self.env.process(self._handle_incoming_msgs())
        self.cpu: CPU = cpu_t(self)
        self.sim.orchestrator.register_entity(self)

    def _handle_incoming_msgs(self):
        while True:
            msg: Message = yield self.env.process(self._recv_data())  # can i do this w/o .process() wrap?
            self.deployed_services[msg.destination].context.recv_q.put(msg)

    def compute(self, computation: Computation):
        yield self.cpu.compute(computation)

    def send_msg(self, msg: Message):
        destination_sv = msg.destination
        # todo: if service runs on this entity: should even ask orchestrator or directly give to that?
        # contra: could be non-optimal under resource constraints

        entity: Entity = yield self.sim.orchestrator.get_entity_for_service(self, destination_sv)
        yield self._send_data(entity.id, msg, msg.size)

    def deploy_service(self, service: Service):
        self.deployed_services[service.id] = service
        service.context.bind_to_entity(self)

    def undeploy_service(self, service_id):
        self.deployed_services[service_id].context.unbind()
        del self.deployed_services[service_id]

