from attic.topology_generation.topology_types.grid_topology import create_random_grid_topology, show_topology
from applications.simple_apps import app_deployment_1, app_deployment_2
from core.core import SimThread
from network.network_topology import NetworkTopology
from pathlib import Path
import datetime

SHOW_TOPOLOGY = True
folder_results = Path("../topology_generation/topology_types/results/")
folder_results.mkdir(parents=True, exist_ok=True)
folder_results = str(folder_results) + "/"


def grid_example():
    """"""
    t = NetworkTopology()
    t_json = create_random_grid_topology()
    t.load(t_json)

    if SHOW_TOPOLOGY:
        show_topology(t)

    simulated_time = 1000
    file_name = os.path.basename(__file__)
    s = SimThread(t, results_path=folder_results + file_name + "_" + datetime.datetime.today().strftime(
        "%Y_%m_%d-%H_%M"))

    simple_device_1_tag = {"mytag": "simple_device_1_tag"}
    simple_device_2_tag = {"mytag": "simple_device_2_tag"}
    app_1_users = s.topology.find_device_by_model(simple_device_1_tag)
    app_2_users = s.topology.find_device_by_model(simple_device_2_tag)

    for user_1_id in app_1_users:
        app_1, placement_1, population_1, selection_1 = app_deployment_1(user_1_id)
        s.deploy_app(app_1, placement_1, population_1, selection_1)

    for user_2_id in app_2_users:
        app_2, placement_2, population_2, selection_2 = app_deployment_2(user_2_id)
        s.deploy_app(app_2, placement_2, population_2, selection_2)

    s.run(simulated_time, show_progress_monitor=False)


if __name__ == '__main__':
    import logging.config
    import os

    logging.config.fileConfig(os.getcwd() + '/logging.ini')
    grid_example()
