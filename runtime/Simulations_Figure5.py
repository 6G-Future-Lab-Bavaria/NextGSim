import os
import csv
import sys
from definitions import RESULTS_DIR, ROOT_DIR

os.chdir(ROOT_DIR)

# import numpy as np

from runtime.utilities import utility
from runtime.MECSimulation import MECSimulation
from runtime.InitialSetUp import InitialSetUpIndoor, InitialSetUpOutdoor, InitialSetUpIndoorFactory
from pathlib import Path
import threading
import logging.config
from runtime.RANSimulation import RANSimulation
from definitions import RESULTS_DIR
from attic.Application import *
from runtime.SimulationParameters import SimulationParameters
from runtime.EventChain import EventChain
from device.TrafficGenerator import TrafficGenerator
import numpy as np
import pandas as pd
import simpy
import random

from edge.util.DistributionFunctions import DeterministicDistributionWithStartingTime

# np.set_printoptions(threshold=np.inf)
utility.format_figure()

EPSILON = 0.001



class Simulation:
    def __init__(self):
        log_file_path = './runtime/logging.ini'
        logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
        logging.getLogger("matplotlib.texmanager").setLevel(logging.WARNING)
        logging.getLogger("matplotlib.dviread").setLevel(logging.WARNING)
        logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
        logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)

        self.record_results = False
        config_file = None
        if sys.argv[3] == "FCFS":
            config_file = "figure_5_experiment_non_radio_aware.json"

        elif sys.argv[3] == "Radio-Aware":
            config_file = "figure_5_experiment_radio_aware.json"

        self.sim_params = SimulationParameters(config_file)

        self.env = simpy.Environment()
        self.setup = None
        self.stop = False
        self.tti_dist = DeterministicDistributionWithStartingTime(name="TTI",
                                                                  starting_time=self.sim_params.TTI_duration,
                                                                  period=self.sim_params.TTI_duration)

        self.logging_level = "CRITICAL"
        logging.basicConfig(level=self.logging_level)

        random.seed(0)
        np.random.seed(int(sys.argv[4]))

        self.user_coordinates = None
        self.devices_per_scenario = None
        self.gNBs_per_scenario = None
        self.edge_servers_per_scenario = []
        self.routers_per_scenario = []
        self.sim_params.scenario.max_num_devices_per_scenario = int(sys.argv[1])
        self.sim_params.scheduler_type = sys.argv[2]
        self.results_folder = 'reproduction/' + sys.argv[1] + '_' + \
                              sys.argv[2] + '_' + sys.argv[3] + '_' + sys.argv[4] +'.csv'

        self.traffic_generator = TrafficGenerator(self)
        self.event_chain = EventChain()
        self.stop = False
        self.feedback_event = threading.Event()
        self.initialize_physicalEnvironment()
        self.ran_data = pd.DataFrame()
        self.mec_data = pd.DataFrame()
        self.mec_simulation = MECSimulation(self)
        self.ran_simulation = RANSimulation(self)

        self.initialize_results_folder()

    def initialize_results_folder(self):
        self.results_folder = RESULTS_DIR + self.results_folder
        header = ["Message Name", "User ID", "Sequence Number", "UL Latency", "Processing Time", "Total Latency",
                  "Delay Budget"]

        with open(self.results_folder, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)

    def initialize_physicalEnvironment(self):
        print("what a weird implementation")
        print(self.sim_params.scenario.scenario)

        if self.sim_params.scenario.scenario == 'Indoor':
            self.setup = InitialSetUpIndoor(self)
        elif self.sim_params.scenario.scenario == 'Indoor factory':
            self.setup = InitialSetUpIndoorFactory(self)
        else:
            self.setup = InitialSetUpOutdoor(self)
        self.gNBs_per_scenario = self.setup.create_gnbs(self.sim_params.scenario.cell_radius)
        self.devices_per_scenario, self.user_coordinates = self.setup.create_users()

    def run(self):
        self.mec_simulation.start()
        self.ran_simulation.start()
        return


if __name__ == '__main__':
    simulation = Simulation()
    simulation.run()
