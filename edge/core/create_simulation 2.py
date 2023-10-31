from entities.base_station import BaseStation, get_closest_base_station
from entities.edge_server import EdgeServer
from entities.gateway import Gateway
from entities.simple_device_1 import SimpleDevice1
from entities.entity import get_entity_by_id, get_entity_list
from network.link import Link, get_link_list
from network.network_topology import NetworkTopology
import numpy as np
import json


# def create_simulation_from_json(topology, num_of_users, area_boundaries):
def create_simulation_from_json(json_file):
    """

    Args:
        json_file():

    Returns:

    """
    with open(json_file) as jsonfile:
        json_data = json.load(jsonfile)

    entities = json_data["entities"]
    links = json_data["links"]
    topology = {'entities': entities, 'links': links}
    num_of_users = json_data["num_of_users"]
    area_boundaries = [json_data["area_length"], json_data["area_width"]]
    area_length = area_boundaries[0]
    area_width = area_boundaries[1]


    t = NetworkTopology()
    entities = topology["entities"]
    links = topology["links"]
    for entity_id in entities.keys():
        entity_descp = entities[entity_id]
        if entity_descp["model"] == "base_station":
            BaseStation(entity_id=entity_id, location=entity_descp["location"])
        elif entity_descp["model"] == "edge_server":
            EdgeServer(entity_id=entity_id, location=entity_descp["location"], )
        elif entity_descp["model"] == "gateway":
            Gateway(entity_id=entity_id, location=entity_descp["location"])

    for _ in range(num_of_users):
        rnd_user_location = [np.random.randint(0, area_length), np.random.randint(0, area_width)]
        mobile_device = SimpleDevice1(location=rnd_user_location)
        mobile_device.add_app('App1')
        mobile_device.attach_to_closest_bs()
        # closest_bs = get_closest_base_station(rnd_user_location)
        # mobile_device.attach_to_bs(closest_bs)

    for link in links:
        tmp_link = links[link]
        Link(get_entity_by_id(tmp_link['src']), get_entity_by_id(tmp_link['dst']), tmp_link['bw'],
             tmp_link['lat'])

    t_tmp = {"entities": get_entity_list(), "links": get_link_list()}
    t.load(t_tmp)
    return t
