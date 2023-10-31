import datetime

import logging.config
import os

from core.core import SimThread, SimConfig
from network.network_topology import NetworkTopology
from entities.entity import create_simulation_from_json
from pathlib import Path
from application_examples.simple_app_examples import *

# RELATIVE_JSON_CONFIG_FILE = '../sim_params/simple_app_config.json'
RELATIVE_JSON_CONFIG_FILE = 'sim_params/grid_bs_topology_w_latency.json'
ABS_JSON_CONFIG_FILE = os.path.abspath(RELATIVE_JSON_CONFIG_FILE)
folder_results = Path("../topology_generation/topology_types/results/")
folder_results.mkdir(parents=True, exist_ok=True)
folder_results = str(folder_results) + "/"

latency_analysis_folder = Path("examples/results/latency_analysis")
latency_analysis_folder.mkdir(parents=True, exist_ok=True)
latency_analysis_folder = str(latency_analysis_folder) + "/"
latency_analysis_file = latency_analysis_folder + 'latency_analysis_' + datetime.datetime.today().strftime("%Y_%m_%d-%H_%M")+'.csv'

sim_config = SimConfig(running_time=10000,
                       plot_latency=False,
                       plot_topology=False,
                       show_csv=True,
                       output_csv=True,
                       is_ran_scheduling_in_use=True,
                       is_ran_simulator_in_use=True,
                       location_update=False,
                       computing_period=0.2,
                       reporting_period=0.2,
                       location_update_period=1,
                       ran_granularity=50,
                       mec_csv_dir='./MEC.csv',
                       latency_analysis_file=latency_analysis_file)


def topology_json(json_file):
    t_initial = NetworkTopology()
    t_json, num_of_users, area_boundaries = t_initial.read_topology_from_json(json_file)
    t_loaded = create_simulation_from_json(t_json, num_of_users, area_boundaries)
    t_initial.load(t_loaded)
    return t_initial


def create_simulation(t_json):
    s = SimThread(t_json, sim_config=sim_config)
    mobile_devices = s.topology.find_mobile_device_by_model("simple_device_1")

    for mobile_device in mobile_devices:
        ran_app, placement, dataflow, selection = simple_ran_app_deployment(mobile_device.user_id)
        s.deploy_app(ran_app, placement, dataflow, selection)

    s.run_ran_simulation(test_initial_deployment=False)


if __name__ == '__main__':
    log_file_path = Path(__file__).parent / 'logging.ini'
    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    t = topology_json(ABS_JSON_CONFIG_FILE)
    create_simulation(t)
