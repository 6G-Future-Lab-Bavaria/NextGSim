# importing the Python modules
from termcolor import colored
from runtime.Scenarios import *
import json
import os


class SimulationParameters(object):
    def __init__(self, simulation, ConfigFile=True, ConfigFileName='config_test.json'):
        self.simulation = simulation
        self.SimParams = simulation.sim_params
        if ConfigFile:
            self.ConfigFileName = ConfigFileName
            self.parse_ConfigFile()
        else:
            return

    def parse_ConfigFile(self):
        path = os.chdir(os.pardir + '/configuration')
        #  read file
        with open(self.ConfigFileName, 'r') as myfile:
            data = myfile.read()
        #  parse file
        config = json.loads(data)
        print(colored(f"***** New config {config} *****", 'green'))
        # self.SimulationParameters.disable_print = sim_params['disable_printing']
        self.SimParams.num_TTI = config['simulation_time']
        if config['scenario'] == 'indoor':
            self.SimParams.scenario = Indoor()
        elif config['scenario'] == 'outdoor':
            self.SimParams.scenario = Outdoor()
        elif config['scenario'] == 'indoor office':
            self.SimParams.scenario = IndoorOffice()
        elif config['scenario'] == 'indoor factory SL':
            self.SimParams.scenario = IndoorFactorySL()
        elif config['scenario'] == 'indoor factory DL':
            self.SimParams.scenario = IndoorFactoryDL()
        elif config['scenario'] == 'indoor factory SH':
            self.SimParams.scenario = IndoorFactorySH()
        elif config['scenario'] == 'indoor factory DH':
            self.SimParams.scenario = IndoorFactoryDH()
        self.SimParams.num_cells = config['num_of_bs']
        self.SimParams.scenario.max_num_devices_per_scenario = config['num_of_users']
        self.SimParams.communication_type = config['communication_type']
        self.SimParams.channel_measurement_granularity = config['scheduling_granularity']
        self.SimParams.traffic_model = config['consider_traffic_models']
        self.SimParams.with_mobility = config['consider_mobility']
        self.SimParams.scheduler_type = config['scheduler_type']
        self.SimParams.service_placement_algorithm = config['service_placement_algorithm']
        self.SimParams.service_replacement_algorithm = config['service_replacement_algorithm']


