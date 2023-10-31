import datetime
import os
import logging.config

from application_examples.simple_app_examples import app_deployment_1
from core.core import SimThread
from network.network_topology import NetworkTopology
from entities.entity import create_topology_from_json
from result_collection.plot import show_topology
from pathlib import Path

SHOW_TOPOLOGY = False
JSON_CONFIG_FILE = '../edge/config/config_test.json'
folder_results = Path("../topology_generation/topology_types/results/")
folder_results.mkdir(parents=True, exist_ok=True)
folder_results = str(folder_results) + "/"


def topology_json(json_file):
    t = NetworkTopology()
    t_json, num_of_users, area_boundaries = t.read_topology_from_json(json_file)
    t_loaded = create_topology_from_json(t_json, num_of_users, area_boundaries)
    t.load(t_loaded)
    if SHOW_TOPOLOGY:
        show_topology(t)
    return t


def create_simulation(t_sim):
    simulated_time = 1000
    file_name = os.path.basename(__file__)
    s = SimThread(t_sim, results_path=folder_results + file_name + "_" + datetime.datetime.today().strftime("%Y_%m_%d-%H_%M"))
    mobile_device_tag = {"mytag": "simple_device_1_tag"}
    mobile_devices = s.topology.find_device_by_model(mobile_device_tag)

    for mobile_device_id in mobile_devices:
        app_1, placement_1, dataflow_1, selection_1 = app_deployment_1(mobile_device_id)
        s.deploy_app(app_1, placement_1, dataflow_1, selection_1)

    s.run(simulated_time, test_initial_deployment=False)

if __name__ == '__main__':
    logging.config.fileConfig('../../edge/logging.ini')
    t = topology_json(JSON_CONFIG_FILE)
    create_simulation(t)