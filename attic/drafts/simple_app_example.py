import datetime

import logging.config
import os


from core.core import SimThread, SimConfig
from core.create_simulation import create_simulation_from_json
from pathlib import Path
from application_examples.simple_app_examples import *
from entities.entity import ENTITY_LIST


RELATIVE_JSON_CONFIG_FILE = '../topologies/grid_bs_topology_w_latency.json'
ABS_JSON_CONFIG_FILE = os.path.abspath(RELATIVE_JSON_CONFIG_FILE)
folder_results = Path("../examples/results/")
folder_results.mkdir(parents=True, exist_ok=True)
folder_results = str(folder_results) + "/"
sim_config = SimConfig(running_time=120,
                       plot_latency=False,
                       plot_topology=False,
                       show_csv=True,
                       is_ran_scheduling_in_use=True,
                       is_ran_simulator_in_use=False,
                       location_update=False,
                       computing_period=0.2,
                       reporting_period=0.3,
                       location_update_period=1,
                       ran_granularity=1000,
                       ran_csv_dir='../sim_params/config_test_3.json',
                       mec_csv_dir='/MEC.csv')



def run_simulation(config):
    sim = SimThread(sim_config=config)
    sim.run(test_initial_deployment=False)


if __name__ == '__main__':
    log_file_path = Path(__file__).parent / 'logging.ini'
    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    sim_top = create_simulation_from_json(ABS_JSON_CONFIG_FILE)
    run_simulation(sim_top)
