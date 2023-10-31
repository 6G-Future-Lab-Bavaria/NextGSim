import json
import numpy as np
from config.config_python import *
from entities.entity import BaseStation, EdgeServer, ENTITY_LIST
from network.network_topology import add_link
from network.network_topology import NetworkTopology, link_does_exist, LINK_LIST
from util.util import ncr


def create_random_grid_topology():
    # Grid size definition
    grid_size_length = 30
    grid_size_width = 30
    base_station_length_spacing = 10
    base_station_width_spacing = 10
    num_of_rows = int(np.floor(grid_size_width / base_station_width_spacing))
    num_of_cols = int(np.floor(grid_size_length / base_station_length_spacing))
    num_of_base_stations = num_of_rows * num_of_cols
    base_station_list = [[0 for i in range(num_of_cols)]
                         for j in range(num_of_rows)]
    edge_server_list = []
    edge_bs_links_list = []
    inter_edge_links = []

    t = NetworkTopology()

    num_of_edge_servers = 5

    num_of_edge_server_connections = 3
    num_of_inter_edge_server_connections = 3
    base_station_links_list = []

    # Creation of base station instances
    for i in range(num_of_rows):
        for j in range(num_of_cols):
            grid_location = [base_station_length_spacing * (i + 1), base_station_width_spacing * (j + 1)]
            base_station_list[i][j] = BaseStation(location=grid_location)

    for i in range(num_of_edge_servers):
        edge_server_list.append(
            EdgeServer(location=[np.random.randint(0, grid_size_length), np.random.randint(0, grid_size_width)]))

    if num_of_edge_server_connections > num_of_edge_servers * num_of_base_stations:
        print("Impossible number of edge server connections! Setting it to the maximum")
        num_of_edge_server_connections = num_of_edge_servers * num_of_base_stations


    i = 0
    linked_edge_servers = []
    while i < num_of_edge_server_connections:
        random_x = np.random.randint(0, num_of_rows)
        random_y = np.random.randint(0, num_of_cols)
        random_edge_server = edge_server_list[np.random.randint(0, num_of_edge_servers)]
        if random_edge_server in linked_edge_servers and len(linked_edge_servers) == len(edge_server_list):
            if not link_does_exist(base_station_list[random_x][random_y], random_edge_server):
                edge_bs_links_list.append(
                    add_link(source=base_station_list[random_x][random_y], destination=random_edge_server))
                edge_bs_links_list.append(
                    add_link(source=random_edge_server, destination=base_station_list[random_x][random_y]))
                i += 1
                continue
            else:
                continue
        elif random_edge_server not in linked_edge_servers:
            if not link_does_exist(base_station_list[random_x][random_y], random_edge_server):
                edge_bs_links_list.append(
                    add_link(source=base_station_list[random_x][random_y], destination=random_edge_server))
                edge_bs_links_list.append(
                    add_link(source=random_edge_server, destination=base_station_list[random_x][random_y]))
                linked_edge_servers.append(random_edge_server)
                i += 1
            else:
                continue
        else:
            continue

    if num_of_inter_edge_server_connections > ncr(num_of_edge_servers, 2) or num_of_inter_edge_server_connections < 0:
        print("Impossible number of inter-edge server connections. Setting it to the maximum!")
        num_of_inter_edge_server_connections = ncr(num_of_edge_servers, 2)

    i = 0
    while i < num_of_inter_edge_server_connections:
        edge_server_1 = edge_server_list[np.random.randint(0, num_of_edge_servers)]
        edge_server_2 = edge_server_list[np.random.randint(0, num_of_edge_servers)]
        if edge_server_1 == edge_server_2:
            pass
        elif link_does_exist(edge_server_1, edge_server_2) or link_does_exist(edge_server_2, edge_server_1):
            pass
        else:
            inter_edge_links.append(add_link(source=edge_server_1, destination=edge_server_2))
            inter_edge_links.append(add_link(source=edge_server_2, destination=edge_server_1))
            i = i + 1

    topology = {"entities": ENTITY_LIST, "links": LINK_LIST}

    # -------------------------------   JSON TOPOLOGY CREATION -----------------------------------------

    json_link = {}
    json_entity = {}

    for entity in ENTITY_LIST.values():
        json_entity[str(entity.entity_id)] = {'model': entity.model, 'location': entity.location}

    for link in LINK_LIST.values():
        json_link[str(link.link_id)] = {'src': str(link.source.entity_id), 'dst': str(link.destination.entity_id),
                                        'lat': link.latency,
                                        'bw': link.bandwidth}

    with open('../../edge/config/config_test_3.json', 'w+') as json_file:
        try:
            json_file_data_new = json.load(json_file)
        except json.JSONDecodeError:
            json_file_data_new = {}

        json_file_data_new['area_length'] = 40
        json_file_data_new['area_width'] = 40
        json_file_data_new['num_of_bs'] = num_of_base_stations
        json_file_data_new['num_of_mec_servers'] = 5
        json_file_data_new['num_of_users'] = 5
        json_file_data_new['scenario'] = SIMULATION_SCENARIO
        json_file_data_new['scheduling_granularity'] = SCHEDULING_GRANULARITY
        json_file_data_new["edge_server_types"] = EDGE_SERVER_TYPES
        json_file_data_new["entities"] = json_entity
        json_file_data_new["links"] = json_link
        json_file.seek(0)
        json.dump(json_file_data_new, json_file, indent=0)
        json_file.truncate()

    return topology


if __name__ == '__main__':
    # sim_top = MicroserviceTopology()
    t_json = create_random_grid_topology()
    # sim_top.load(t_json)
    # show_topology(sim_top)
