from edge.entities.Entity import Entity
from attic.radio.schedulers.dl_scheduler import DownlinkScheduler
from attic.radio.schedulers.ul_scheduler import UplinkScheduler
from edge.util.Util import closest_node
import numpy as np

BASE_STATIONS = []
BASE_STATION_LOCATIONS = {}


class BaseStation(Entity):
    """
    This class is used to create base stations.
    """

    def __init__(self, entity_id=None, model="base_station", location=None):
        super().__init__(entity_id=entity_id, model=model, location=location)
        add_base_station(self)
        self.connected_users = []
        self.dl_scheduler = DownlinkScheduler(self.entity_id)
        self.ul_scheduler = UplinkScheduler(self.entity_id)

    def set_scheduler_env(self, env):
        self.dl_scheduler.set_env(env)
        self.ul_scheduler.set_env(env)

    def start_schedulers(self):
        self.dl_scheduler.start_scheduler()
        self.ul_scheduler.start_scheduler()

    def receive_ul_scheduling_request(self, user_id, message):
        if user_id in self.ul_scheduler.user_scheduling_requests.keys():
            self.ul_scheduler.user_scheduling_requests[user_id].append(message)
        else:
            self.ul_scheduler.user_scheduling_requests[user_id] = []
            self.ul_scheduler.user_scheduling_requests[user_id].append(message)

    def schedule_dl_transmission(self, user_id, message):
        if user_id in self.dl_scheduler.user_scheduling_requests.keys():
            self.dl_scheduler.user_scheduling_requests[user_id].append(message)
        else:
            self.dl_scheduler.user_scheduling_requests[user_id] = []
            self.dl_scheduler.user_scheduling_requests[user_id].append(message)


def add_base_station(bs):
    BASE_STATIONS.append(bs)
    BASE_STATION_LOCATIONS[bs] = np.array(bs.location)


def get_base_stations():
    return BASE_STATIONS


def get_base_station_locations():
    return BASE_STATION_LOCATIONS


# def get_closest_base_station(location):
#     # bs_locations = list(get_base_station_locations().values())
#     bs_locations_unparsed = get_base_station_locations()
#     bs_locations = list(bs_locations_unparsed.values())
#     closest_bs_location = np.array(closest_node(bs_locations, location))
#     closest_bs = get_key_from_value(bs_locations_unparsed, closest_bs_location)
#     return closest_bs

def get_closest_base_station(node):
    # bs_locations = list(get_base_station_locations().values())
    # bs_locations_unparsed = get_base_station_locations()
    # bs_locations = list(bs_locations_unparsed.values())
    bs_arr = get_base_stations()
    closest_bs = np.array(closest_node(bs_arr, node))
    return closest_bs
