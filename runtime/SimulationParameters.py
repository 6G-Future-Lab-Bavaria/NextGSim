from runtime.data_classes import Frequencies, AggregatedTraffic, MeasurementParams
from termcolor import colored
from runtime.Scenarios import *
from definitions import CONFIGURATION_DIR
import json


@dataclass()
class SimulationParameters(object):
    def __init__(self, config_file=None):
        # self.use_configFile: bool = True
        if config_file:
            self.config_file = CONFIGURATION_DIR + config_file
        else:
            self.config_file = None
        self.disable_print: bool = False
        self.num_TTI: int = 20205  # simulation time in ms
        self.initial_TTI: int = 0
        self.TTI_duration: int = 10
        '---------------------- Building simulation scenario --------------------------------------'
        self.include_MEC: bool = True
        self.traffic_model: bool = False  # include 3GPP traffic models
        self.agreggated_traffic_model: str = AggregatedTraffic.model2
        self.with_mobility: bool = True  # UEs with dynamic mobility
        self.generate_mobility_traces: bool = False  # generate traces or read a data set (path in Scenario)
        self.channel_metric_for_handover: str = 'RSRP'  # 'RSRP' 'SINR'
        self.scenario: object = IndoorFactorySL()  # IndoorFactorySL()  # Indoor() # Outdoor()
        self.num_cells: int = 18
        self.max_cells_in_one_row = 10  # for plotting purpose
        self.communication_type: str = 'UL'
        self.snr_averaging: bool = False
        self.with_interference: bool = False
        self.channel_measurement_granularity: int = MeasurementParams.channel_measurement_periodicity
        self.schedule_PRBs: bool = True
        if self.schedule_PRBs:
            self.scheduler_type = 'Random'  # 'Round_Robin', 'Random', 'Max_Rate'
        self.store_throughput = False
        self.store_latency = False
        '------------------------ Plotting the interactive GUI --------------------------------------'
        self.visualise_scenario: bool = False
        if self.scenario.scenario == 'Indoor factory':
            self.predefined_gNB_coord: bool = True
        else:
            self.predefined_gNB_coord: bool = False
        self.show_connections: bool = True
        '----------------------- Parameters that need to be checked --------------------------------'
        self.los_update_periodicity = 1000  # 1 s
        self.always_los_flag = None  # always LoS: best case
        self.always_non_los_flag = False  # never LoS: worst case
        self.with_sanity_checks = False  # slows down the simulation

        # Mobility-related
        self.slaw_range = 1000
        self.t_gap_slaw = 10 ** 3  # ms
        self.num_top_gnbs = None
        self.user_id = 0  # 13
        self.look_ahead = None
        self.start_offset = 0  # int(100*10**3 - num_TTI/10**3)  # 1h # start reading mobility traces from this value (sec) [0; 100,000]
        self.error_probability = 0
        self.plot_snr_per_TTI = False
        self.results_name = ''
        self.scheduler_type = "Round_Robin"

        # Edge Related
        self.computing_period = 2
        self.service_update_period = 25
        self.service_placement_algorithm = "Random"  # LatencyAware, Random or RoundRobin
        self.service_type = "radio-aware"
        self.number_of_instances = 10

        if config_file:
            self.parse_ConfigFile()
        return

    def __post_init__(self):
        if self.communication_type == 'UL':
            self.scenario.mimo_antennas = 4
        elif self.communication_type == 'DL':
            self.scenario.mimo_antennas = 8
        if self.scenario.scenario == "Indoor":
            self.scenario.x_max = self.scenario.cell_radius * (self.num_cells / self.max_cells_in_one_row * 2)
            self.scenario.y_max = self.scenario.cell_radius * 3 + 20
        elif self.scenario == "Indoor factory":
            self.scenario.x_max = self.scenario.hall_length
            self.scenario.y_max = self.scenario.hall_width

        self._check_los_flag()
        self.set_simulation_parameters()

    def _check_los_flag(self):
        if self.always_los_flag:
            print("Always LoS in the channel")
        if self.always_los_flag and self.always_non_los_flag:
            assert 0, 'Wrong LoS and no LoS flags set in SimulationParameters. Either one or another can be True'

    def set_simulation_parameters(self):
        self.results_name += '_'
        for param, val in self.config.items():
            if param == 'always_los_flag':
                self.always_los_flag = val
            elif param == 'los_update_periodicity':
                self.los_update_periodicity = val
            elif param == 'top_num_gnbs':
                self.num_top_gnbs = val
            elif param == 'center_freq_micro':
                self.scenario.center_freq_micro = val


    def parse_ConfigFile(self):
        # path = os.chdir(os.pardir + '/../configuration')
        #  read file
        with open(self.config_file, 'r') as config_file:
            data = config_file.read()
        #  parse file
        config = json.loads(data)
        print(colored(f"***** New config {config} *****", 'green'))
        # self.SimulationParameters.disable_print = sim_params['disable_printing']
        self.num_TTI = config['simulation_time']
        if config['scenario'] == 'indoor':
            self.scenario = Indoor()
        elif config['scenario'] == 'outdoor':
            self.scenario = Outdoor()
        elif config['scenario'] == 'indoor office':
            self.scenario = IndoorOffice()
        elif config['scenario'] == 'indoor factory SL':
            self.scenario = IndoorFactorySL()
        elif config['scenario'] == 'indoor factory DL':
            self.scenario = IndoorFactoryDL()
        elif config['scenario'] == 'indoor factory SH':
            self.scenario = IndoorFactorySH()
        elif config['scenario'] == 'indoor factory DH':
            self.scenario = IndoorFactoryDH()
        self.num_cells = config['num_of_bs']
        self.scenario.max_num_devices_per_scenario = config['num_of_users']
        self.communication_type = config['communication_type']
        self.channel_measurement_granularity = config['scheduling_granularity']
        self.traffic_model = config['consider_traffic_models']
        self.with_mobility = config['consider_mobility']
        self.scheduler_type = config['scheduler_type']
        self.service_placement_algorithm = config['service_placement_algorithm']
        self.service_replacement_algorithm = config['service_replacement_algorithm']
