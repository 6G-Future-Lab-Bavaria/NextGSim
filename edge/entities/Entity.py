import logging
from edge.network.NetworkTopology import NetworkTopology
from edge.network.MicroserviceTopology import MicroserviceTopology
from runtime.data_classes import EntityClass

ENTITY_LIST = {}
EDGE_SERVERS = []
BASE_STATIONS = []
DEVICES = []
CPUS = []
ROUTERS = []
ORCHESTRATORS = []
USER_LIST = {}
ENTITY_COUNTER = 0
USER_COUNTER = 0
DeviceID_to_EntityID_Map = {}
EntityID_to_DeviceID_Map = {}
BaseStationID_to_EntityID_Map = {}
EntityID_to_BaseStationID_Map = {}
logger = logging.getLogger(__name__)
SIM = 0


class Entity(object):
    """
        This class unifies any physical entity_id in the network such as base stations, edge servers, actuators, sensors,
        mobile entities, drones etc. Generic variables and methods are defined in the parent class, and it can be extended
        for each entity_id service_type.
    """

    def __init__(self, name=None, entity_id=None, location=None):
        global ENTITY_COUNTER
        global ENTITY_LIST
        self.name = name
        if entity_id is not None:
            self.entity_id = int(entity_id)
            ENTITY_COUNTER += 1
        else:
            self.entity_id = ENTITY_COUNTER
            ENTITY_COUNTER += 1

        ENTITY_LIST[self.entity_id] = self

        if location is not None:
            self.x = location[0]
            self.y = location[1]

        if not (hasattr(self, 'x') and hasattr(self, 'y')):
            self.x = None
            self.y = None

        if self.__class__.__name__ in EntityClass.physical_entities:
            NetworkTopology().add_node(self)

        if self.__class__.__name__ in EntityClass.application_entities:
            MicroserviceTopology().G.add_node(self)

        if self.__class__.__name__ == "GnB":
            add_bs(self)

        if self.__class__.__name__ == "Device":
            add_device(self)

        if self.__class__.__name__ == "EdgeOrchestrator":
            ORCHESTRATORS.append(self)

        if self.__class__.__name__ == "EdgeServer":
            EDGE_SERVERS.append(self)

        if self.__class__.__name__ == "Cpu":
            CPUS.append(self)

        if self.__class__.__name__ == "Router":
            ROUTERS.append(self)

    @property
    def location(self):
        return [float(self.x), float(self.y)]

    def __hash__(self):
        return hash(self.entity_id)

    def __eq__(self, other):
        if self.entity_id == other:
            return True
        else:
            return False

    def set_coordinates(self, x=None, y=None):
        self.x = x
        self.y = y
        NetworkTopology().G_pos[self.entity_id] = [x, y]

    def update_coordinates(self):
        NetworkTopology().G_pos[self.entity_id] = [self.x, self.y]


def set_sim(sim_inst):
    global SIM
    SIM = sim_inst


def get_sim():
    return SIM


def get_user_counter():
    global USER_COUNTER
    return USER_COUNTER


def get_and_increment_user_counter():
    global USER_COUNTER
    prev_user_counter = USER_COUNTER
    USER_COUNTER += 1
    return prev_user_counter


def get_entity_by_id(id_entity):
    if id_entity == -1:
        return None
    if isinstance(id_entity, str):
        id_entity = int(id_entity)
    return ENTITY_LIST[id_entity]


def get_entity_list():
    return ENTITY_LIST


def map_user_id_to_entity_id(user_id):
    return DeviceID_to_EntityID_Map[user_id]


def map_user_id_to_entity(user_id):
    return get_entity_by_id(DeviceID_to_EntityID_Map[user_id])


def map_entity_id_to_device_id(entity_id):
    if entity_id in EntityID_to_DeviceID_Map:
        return EntityID_to_DeviceID_Map[entity_id]
    else:
        return entity_id


def getDeviceID_to_EntityID_Map():
    return DeviceID_to_EntityID_Map


def getBaseStationID_to_EntityID_Map():
    return BaseStationID_to_EntityID_Map


def get_edge_servers():
    return EDGE_SERVERS


def get_cpus():
    return CPUS


def get_routers():
    return ROUTERS


def get_orchestrators():
    return ORCHESTRATORS


def get_base_stations():
    return BASE_STATIONS


def add_device(device):
    DEVICES.append(device)
    EntityID_to_DeviceID_Map[device.entity_id] = device.ID
    DeviceID_to_EntityID_Map[device.ID] = device.entity_id


def add_bs(bs):
    BASE_STATIONS.append(bs)
    BaseStationID_to_EntityID_Map[bs.ID] = bs.entity_id
    EntityID_to_BaseStationID_Map[bs.entity_id] = bs.ID
