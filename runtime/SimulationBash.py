import csv
import os
import sys

# import numpy as np

from InitialSetUp import InitialSetUpIndoor, InitialSetUpOutdoor, InitialSetUpIndoorFactory
from utilities import utility
from pathlib import Path
import threading
import logging.config
from RANSimulation import RANSimulation
from MECSimulation import MECSimulation
from attic.Application import *
from SimulationParameters import SimulationParameters as SimParams
from EventChain import EventChain
from device.TrafficGenerator import TrafficGenerator
import logging.config
from Parse_configuration import SimulationParameters
import numpy as np
import pandas as pd

# np.set_printoptions(threshold=np.inf)
utility.format_figure()

EPSILON = 0.001
np.random.seed(0)


class Simulation:
    def __init__(self, logger=None):
        log_file_path = Path(__file__).parent / 'logging.ini'
        logging.basicConfig(level='DEBUG')
        logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
        logging.getLogger("matplotlib.texmanager").setLevel(logging.WARNING)
        logging.getLogger("matplotlib.dviread").setLevel(logging.WARNING)
        logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
        logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)
        # random.seed(0)
        self.record_results = True
        self.setup = None
        self.user_coordinates = None
        self.devices_per_scenario = None
        self.gNBs_per_scenario = None
        self.edge_servers_per_scenario = []
        self.routers_per_scenario = []
        self.sim_params = SimParams()
        self.applications = redcap_application()
        self.file_sim_params = SimulationParameters(self, ConfigFile=self.sim_params.use_configFile,
                                                    ConfigFileName="figure_5_experiment_radio_aware.json")
        self.traffic_generator = TrafficGenerator(self)
        self.event_chain = EventChain()
        self.stop = False
        self.feedback_event = threading.Event()
        self.initialize_physicalEnvironment()
        self.ran_data = pd.DataFrame()
        self.mec_data = pd.DataFrame()
        self.mec_simulation = MECSimulation(self)
        self.ran_simulation = RANSimulation(self)

        self.result_file = os.pardir + '/results/reproduction/num_of_user_' + str(sys.argv[1]) + '.csv'

        # self.result_file
        header = ["Num_of_Users", "Memory Used", "Simulation Runtime"]

        with open(self.result_file, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)

    def run(self):
        self.mec_simulation.start()
        self.ran_simulation.start()
        return

    def initialize_physicalEnvironment(self):
        if self.sim_params.scenario.scenario == 'Indoor':
            self.setup = InitialSetUpIndoor(self)
        elif self.sim_params.scenario.scenario == 'Indoor factory':
            self.setup = InitialSetUpIndoorFactory(self)
        else:
            self.setup = InitialSetUpOutdoor(self)
        self.gNBs_per_scenario = self.setup.create_gnbs(self.sim_params.scenario.cell_radius)
        self.devices_per_scenario, self.user_coordinates = self.setup.create_users()

    # self.edge_servers_per_scenario = self.setup.create_edge_servers()


if __name__ == '__main__':
    simulation = Simulation()
    simulation.run()
