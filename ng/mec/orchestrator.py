from __future__ import annotations
from typing import TYPE_CHECKING

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
    @abstractmethod
    def get_entity_for_service(self, sender, service):
        pass

    @abstractmethod
    def handle_entity_connected(self):
        pass

    # todo: orchestrator must track network changes
    @abstractmethod
    def handle_entity_network_changed(self):
        pass


class SimpleOrchestrator(Orchestrator):

    def get_entity_for_service(self, sender, service):
        for e_id, ent in self.entities.items():
            for s_id, sv in ent.deployed_services.items():
                if isinstance(sv, service):
                    return ent
        raise RuntimeError("No entity for service " + service) # must not happen ...

    def handle_entity_connected(self):
        pass

    def handle_entity_network_changed(self):
        pass

