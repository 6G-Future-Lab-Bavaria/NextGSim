from __future__ import annotations
from typing import TYPE_CHECKING

from mec.service import Service

if TYPE_CHECKING:
    from ng.mec.entity import Entity
    from ng.simulation import Simulation

from abc import abstractmethod, ABC
from typing import Dict

# one orchestrator per simulation
class Orchestrator(ABC):

    def __init__(self, sim: Simulation):
        self.sim = sim
        self.entities: Dict[any, Entity] = {}

    def register_entity(self, entity: Entity):
        self.entities[entity.id] = entity

    # get entity whish the sending entity send a message to when it wants to use the service
    #@abstractmethod
    #def get_entity_for_service(self, sender, service) -> Entity:
    #    pass

    @abstractmethod
    def handle_entity_connected(self, entity):
        pass

    @abstractmethod
    def handle_entity_disconnected(self, entity):
        pass

    @abstractmethod
    def deploy(self, sdd: ServiceDeploymentDescriptor):
        pass


class ServiceDeploymentDescriptor:

    def __init__(self, services: list[Service], interlinks: Dict[str, any], sla: Dict[str, any]):
        self.services = services
        self.interlinks = interlinks
        self.sla = sla

# places services such that entities that have few services are considered first, no multiple instances per service
class SimpleOrchestrator(Orchestrator):

    def __init__(self, sim: Simulation):
        super().__init__(sim)

    def get_entity_for_service(self, sender, service):
        for e_id, ent in self.entities.items():
            for s_id, sv in ent.deployed_services.items():
                if isinstance(sv, service):
                    print(service, ent.id)
                    return ent
        raise RuntimeError("No entity for service " + str(service)) # must not happen ...

    def handle_entity_connected(self, entity):
        pass

    def handle_entity_disconnected(self):
        pass

    def deploy(self, sdd: ServiceDeploymentDescriptor):

        map: Dict[str, list[Entity]] = {}
        services: Dict[str, Service] = { sv.name : sv for sv in sdd.services }

        # returns whether map doesn't violate any sla measures
        def possible():
            for service in sdd.services:
                if service.name not in map:
                    continue
                instances = map[service.name]
                for entity in instances:
                    from_id = entity.id
                    for dep_sv_name in sdd.interlinks[service.name]:
                        if dep_sv_name not in map:
                            continue
                        for to_ent in map[dep_sv_name]:
                            to_id = to_ent.id
                            if self.sim.network.has_route(from_id, to_id):
                                break # interlink possible
                        else:
                            return False # interlink violated
            return True

        ent_sv_count = {e_id: 0 for e_id in self.entities.keys()}

        def place_services(services):
            if len(services) == 0: # all services placed => done
                return True
            service = services[0]
            map[service.name] = []

            for ent_id, entity in sorted(self.entities.items(), key=lambda item: ent_sv_count[item[0]]):
                map[service.name].append(entity)
                ent_sv_count[ent_id] += 1
                if possible() and place_services(services[1:]):
                    return True
                map[service.name] = map[service.name][:-1]
                ent_sv_count[ent_id] -= 1

            return False # no possible entity

        if not place_services(sdd.services):
            raise Exception("Cannot fulfill SDD")

        for sv_name, instances in map.items():
            for ent in instances:
                ent.deploy_service(services[sv_name])

        for e_id, ent in self.entities.items():
            for sv_name in ent.deployed_services.keys():
                for dep_sv_name in sdd.interlinks[sv_name]:
                    for entity in map[dep_sv_name]: # find best entity, here: take first reachable
                        if self.sim.network.has_route(e_id, entity.id):
                            ent.dns_cache[dep_sv_name] = entity.id
                            break

