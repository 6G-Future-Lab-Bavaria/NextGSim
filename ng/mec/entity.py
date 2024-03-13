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

    def __init__(self, sim, id, cpu: CPU, dns=None, services=None, ifs=None):
        super().__init__(sim, id, ifs)
        self.deployed_services: Dict[str, Service] = {}
        self.env.process(self._handle_incoming_msgs())
        self.cpu: CPU = cpu
        self.dns_cache: Dict[str, str] = {}
        self.sim.orchestrator.register_entity(self)

        if services:
            for service in services:
                self.deploy_service(service)

        if dns:
            self.dns_cache = dns

    def _handle_incoming_msgs(self):
        while True:
            msg: Message = yield self.env.process(self._recv_data())  # can i do this w/o .process() wrap?
            self.sim.eventlog.register_event(self, "MSG_RECV", str(msg))
            self.deployed_services[msg.destination].context.recv_q.put(msg)

    def _query_dns(self, sv_name):
        if sv_name not in self.dns_cache:
            print("Failed dns query for", sv_name, "on", str(self))
            return None
        return self.dns_cache[sv_name]

    def compute(self, computation: Computation):
        def d():
            t = self.sim.env.now
            yield self.cpu.compute(computation)
            td = self.sim.env.now - t
            self.sim.eventlog.register_event(self, "COMP", "[c=%s,t=%s]" % (computation, str(td)))
        return self.env.process(d())

    def send_msg(self, msg: Message):
        def d():
            destination_sv = msg.destination
            entity_id = self._query_dns(destination_sv)
            if entity_id is not None:
                yield self._send_data(entity_id, msg, msg.size)
                self.sim.eventlog.register_event(self, "MSG_SENT", str(msg))
        return self.env.process(d())

    def deploy_service(self, service: Service):
        self.sim.eventlog.register_event(self, "DEPLOY_SV", str(service))
        self.deployed_services[service.name] = service
        service.context.bind_to_entity(self)

    def undeploy_service(self, service):
        self.sim.eventlog.register_event(self, "UNDEPLOY_SV", str(service))
        self.deployed_services[service.name].context.unbind()
        del self.deployed_services[service.name]

