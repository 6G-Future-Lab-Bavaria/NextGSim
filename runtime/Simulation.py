# @Author: Alba Jano
# @Email: alba.jano@tum.de
import csv
import os
import numpy as np
import simpy
import sys
import logging.config
import random
import pandas as pd
from pathlib import Path
import logging.config
from definitions import RESULTS_DIR, ROOT_DIR

from runtime.InitialSetUp import InitialSetUpIndoor, InitialSetUpOutdoor, InitialSetUpHardCoded, \
    InitialSetUpIndoorFactory
from runtime.RANSimulation import RANSimulation
from runtime.MECSimulation import MECSimulation
from runtime.SimulationParameters import SimulationParameters
from runtime.RunTimeSetUp import RunTime
from runtime.EventChain import EventChain
from runtime.utilities import utility
# from runtime.Parse_configuration import SimulationParameters
from edge.util.DistributionFunctions import DeterministicDistributionWithStartingTime

np.set_printoptions(threshold=np.inf)
utility.format_figure()

EPSILON = 0.001


class Simulation:
    def __init__(self):
        log_file_path = Path(__file__).parent.parent / 'logging.ini'
        logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
        logging.getLogger("matplotlib.texmanager").setLevel(logging.WARNING)
        logging.getLogger("matplotlib.dviread").setLevel(logging.WARNING)
        logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
        logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)
        random.seed(0)
        self.record_results = False
        self.sim_params = SimulationParameters("config_test.json")
        self.env = simpy.Environment()
        self.setup = None
        self.stop = False
        self.logging_level = "DEBUG"
        logging.basicConfig(level=self.logging_level)
        self.tti_dist = DeterministicDistributionWithStartingTime(name="TTI",
                                                                  starting_time=self.sim_params.TTI_duration,
                                                                  period=self.sim_params.TTI_duration)

        self.user_coordinates = None
        self.devices_per_scenario = None
        self.gNBs_per_scenario = None
        self.edge_servers_per_scenario = []
        self.routers_per_scenario = []
        self.event_chain = EventChain()
        self.stop = False
        self.initialize_physicalEnvironment()
        self.ran_data = pd.DataFrame()
        self.ran_simulation = RANSimulation(self)
        self.mec_data = pd.DataFrame()
        self.mec_simulation = MECSimulation(self)
        self.results_folder = "fnwf/test/test.csv"
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
        if self.sim_params.hardcoded_initial_setup:
            self.setup = InitialSetUpHardCoded(self, )
        elif self.sim_params.scenario.scenario == 'Indoor':
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


def blockPrint():
    sys.stdout = open(os.devnull, 'w')


if __name__ == "__main__":
    # blockPrint()
    simulation = Simulation()
    simulation.run()
