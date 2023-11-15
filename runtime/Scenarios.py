import pandas as pd
import numpy as np
from abc import ABC
from runtime.data_classes import dataclass
from tabulate import tabulate
from runtime.data_classes import Frequencies, MeasurementParams
from itertools import product


SCS_FR1 = ['15kHz', '30kHz', '60kHz']
SCS_FR2 = ['60kHz', '120kHz']

# see https://www.etsi.org/deliver/etsi_ts/138300_138399/138306/15.03.00_60/ts_138306v150300p.pdf
SCS_to_rlc_rtt = {15: 50, 30: 40, 60: 30, 120: 20}  # KHz to ms

@dataclass()
class ScenarioBase(ABC):
    x_max: int = None
    y_max: int = None
    mimo_antennas = None  # maximum number of MIMO layers (max 8 in DL, 4 in UL)

    def _set_frequency_band(self, center_freq):
        if center_freq >= 24:  # GHz
            return Frequencies.fr2
        else:
            return Frequencies.fr1

    def _set_mu(self, subcarrier_spacing, frequency):
        if frequency == Frequencies.fr1:
            return SCS_FR1.index(str(subcarrier_spacing) + "kHz")
        elif frequency == Frequencies.fr2:
            return SCS_FR2.index(str(subcarrier_spacing) + "kHz")
        else:
            raise NameError("Wrong name of frequency! Choose FR1 or FR2.")

    def _set_num_PRBs(self, subcarrier_spacing, bandwidth, frequency):
        """
        An RB is defined as 12 number of consecutive subcarriers in frequency domain and one slot in time domain
        irrespective of the numerology. The bandwidth occupied by an RB depends upon the numerology being used.
        """
        pd.set_option('display.max_columns', 13)
        if frequency == Frequencies.fr1:
            # just for tests purposes changed at 5 MHZ 25 to 8
            RBs_maximum_transmission_bandwidth_configuration_FR1 = {'0MHz': [0, 0, 0],
                                                                    '5MHz': [6, 11, None], '10MHz': [52, 24, 11],
                                                                    '15MHz': [79, 38, 18], '20MHz': [106, 51, 24],
                                                                    '25MHz': [133, 65, 31], '30MHz': [160, 78, 38],
                                                                    '40MHz': [216, 106, 51], '50MHz': [270, 133, 65],
                                                                    '60MHz': [None, 162, 79], '80MHz': [None, 217, 107],
                                                                    '90MHz': [None, 245, 121],
                                                                    '100MHz': [None, 273, 135]}

            nRBs = pd.DataFrame(RBs_maximum_transmission_bandwidth_configuration_FR1, index=SCS_FR1)
        elif frequency == Frequencies.fr2:
            RBs_maximum_transmission_bandwidth_configuration_FR2 = {'50MHz': [66, 32], '100MHz': [132, 66],
                                                                    '200MHz': [264, 132], '400MHz': [None, 264]}

            nRBs = pd.DataFrame(RBs_maximum_transmission_bandwidth_configuration_FR2, index=SCS_FR2)
        else:
            raise NameError("Wrong name of frequency! Choose FR1 or FR2.")
        try:

            # print((nRBs.loc[str(subcarrier_spacing) + "kHz"]).loc[str(bandwidth) + "MHz"], " PRBs")
            return int((nRBs.loc[str(subcarrier_spacing) + "kHz"]).loc[str(bandwidth) + "MHz"])
        except:
            raise NameError("Wrong BANDWIDTH or SUBCARRIER SPACING name!")

    def print_sim_params(self):
        MeasurementParams().print_sim_params()


@dataclass
class Outdoor(ScenarioBase):
    scenario: str = 'UMi'
    num_rows = 5
    num_cols = 6
    num_macro_gnbs = None
    inter_site_dist_macro: float = 500  # m
    inter_site_dist_micro: float = 200  # m
    min_bs_ue_dist: int = 10  # m
    macro_gnb_antenna_height: int = 25  # m
    micro_gnb_antenna_height: int = 10  # m
    ue_antenna_height: float = 1.5  # m
    effective_env_height: int = 1  # m
    subcarrier_spacing_macro = 30
    subcarrier_spacing_micro = 60 
    center_freq_macro: float = 0.5  # GHz
    center_freq_micro: float = 4  # GHz   # 4
    center_freq_multiplier = 10 ** 9
    bandwidth_macro: int = 20  # MHz
    bandwidth_micro: int = 50  # MHz  # 50 for FR2, 40 for FR1
    transmit_power_macro = 40   # dBm 49 for DL, 23 dBm for UL  # used 26 before
    transmit_power_micro = 33
    # Memory-Full Context-Aware Predictive Mobility Management in Dual Connectivity 5G Networks: 38 dBm
    # if center_freq_micro == 4:
    #     transmit_power_micro = 20  # dBm
    # elif center_freq_micro == 28:
    #     transmit_power_micro = 38  # dBm
    # else:
    #     transmit_power_micro = 13
    device_transmit_power = 0  # dBm
    cell_radius = inter_site_dist_macro / np.sqrt(3)   # m
    max_num_devices_per_scenario: int = 1
    min_num_devices_per_scenario: int = 1
    # mobility_traces_filename = 'mobility/mobility_traces/lstm_fixedseed/vary_hurst_tgap1_speed1/hurst_0.9.mat'
    # mobility_traces_filename = 'mobility/mobility_traces/predictions/results_tgap1_hurst0.6_speed1_stack_seq2seq/models/test_pred.pkl'
    mobility_traces_filename = 'mobility/mobility_traces/predictions/results_tgap1_speed1_hurst0.9_seq2seq_gpu/models/test_pred.pkl'
    # mobility_traces_filename = 'mobility/mobility_traces/predictions/results_tgap1_speed1.5_hurst0.6_seq2seq/models/test_pred_modelstack_seq2seq.pkl'
    print(mobility_traces_filename)
    BS_noise_figure = 5  # dB
    UE_noise_figure = 7  # dB
    gNB_antenna_gain = 8  # dBi # fixme: 15 dB from Simulation res for CHO R2-1815245
    UE_antenna_gain = 0  # dBi
    shadowing_std_los = 4  # dB
    shadowing_std_nlos = 7.82  # dB

    frequency_macro = None
    frequency_micro = None
    num_PRBs_macro = None
    num_PRBs_micro = None
    mu_macro = None
    mu_micro = None
    PRB_bandwidth_macro = None
    PRB_bandwidth_micro = None
    rlc_rtt = SCS_to_rlc_rtt[subcarrier_spacing_macro]

    if bandwidth_micro > 100 or bandwidth_macro > 100:
        assert 0, "Bandwidth must be up to 100 MHz according to 3GPP"

    def __post_init__(self):
        self.frequency_macro = self._set_frequency_band(self.center_freq_macro)
        self.frequency_micro = self._set_frequency_band(self.center_freq_micro)
        self.num_PRBs_macro = self._set_num_PRBs(self.subcarrier_spacing_macro, self.bandwidth_macro,
                                                 self.frequency_macro)
        self.num_PRBs_micro = self._set_num_PRBs(self.subcarrier_spacing_micro, self.bandwidth_micro,
                                                 self.frequency_micro)
        self.mu_macro = self._set_mu(self.subcarrier_spacing_macro, self.frequency_macro)
        self.mu_micro = self._set_mu(self.subcarrier_spacing_micro, self.frequency_micro)
        self._set_PRB_bandwidth()

    def _set_PRB_bandwidth(self):
        self.PRB_bandwidth_macro = 12 * self.subcarrier_spacing_macro  # kHz SCS: [15, 30, 60, 120, 240] kHz
        self.PRB_bandwidth_micro = 12 * self.subcarrier_spacing_micro

    def print_sim_params(self):
        msg = f"ISD macro {self.inter_site_dist_macro} m, micro {self.inter_site_dist_micro} m"
        print(msg)
        print(tabulate([
            ['macro', self.micro_gnb_antenna_height, self.bandwidth_macro,
             self.center_freq_macro, self.transmit_power_macro,
             self.subcarrier_spacing_macro,
             self.num_PRBs_macro, self.PRB_bandwidth_macro, self.mu_macro],
            ['micro', self.macro_gnb_antenna_height, self.bandwidth_micro,
             self.center_freq_micro, self.transmit_power_micro,
             self.subcarrier_spacing_micro,
             self.num_PRBs_micro, self.PRB_bandwidth_micro, self.mu_micro]],
            headers=['gNB type', 'Antenna height', 'BW (MHz)', 'Frequency (GHz)', 'Tx power (dBm)', 'Subcar spacing',
                     "Num PRBs", 'PRB BW (kHz)', 'mu']))
        super().print_sim_params()


@dataclass
class Indoor(ScenarioBase):
    scenario: str = 'Indoor'
    inter_site_dist: float = 20  # m
    gnb_antenna_height: int = 3  # m
    ue_antenna_height: float = 1  # m
    effective_env_height: int = 1  # m
    min_bs_ue_dist: int = 0  # m
    bandwidth: int = 5   # MHz
    center_freq: float = 0.5  # GHz
    center_freq_multiplier = 10 ** 9
    cell_radius = 10  # m
    max_num_devices_per_scenario: int = 5
    min_num_devices_per_scenario: int = 1
    transmit_power = 0  # dBm for UL
    device_transmit_power = 0  # dBm
    mobility_traces_filename = None
    subcarrier_spacing = 15
    BS_noise_figure = 5  # dB
    UE_noise_figure = 7  # dB
    gNB_antenna_gain = 21.5  # dBi
    UE_antenna_gain = 0  # dBi
    shadowing_std_los = 3  # dB
    shadowing_std_nlos = 8.03   # dB 8.03
    rlc_rtt = SCS_to_rlc_rtt[subcarrier_spacing]

    def __post_init__(self):
        self.frequency = self._set_frequency_band(self.center_freq)
        self.num_PRBs = self._set_num_PRBs(self.subcarrier_spacing, self.bandwidth, self.frequency)
        self.mu = self._set_mu(self.subcarrier_spacing, self.frequency)
        self._set_PRB_bandwidth()

    def _set_PRB_bandwidth(self):
        self.PRB_bandwidth = 12 * self.subcarrier_spacing  # kHz SCS: [15, 30, 60, 120, 240] kHz

    def print_sim_params(self):
        super().print_sim_params()

"""
Source: 3GPP Standardized 5G Channel Model for IIoT Scenarios: A Survey
"""

@dataclass
class IndoorOffice(object):
    sceanrio: str = 'Indoor office'
    hall_length = 120 #m
    hall_width = 50 # m
    room_height = 3 #m
    gNB_height = 3 #m
    UE_height = 1 #m
    UE_speed = 3 #km/h
    UE_distribution = 'Uniform'
    LOS_beta: float = 32.4
    LOS_alpha: float = 1.73
    LOS_gamma: float = 2
    LOS_sigma: float = 3
    NLOS_beta: float = 17.3
    NLOS_alpha: float = 3.83
    NLOS_gamma: float = 2.49
    NLOS_sigma: float = 8.03
    max_distance_3D = 150 #m


@dataclass
class IndoorFactory(ScenarioBase):
    scenario: str = 'Indoor factory'
    LOS_beta: float = 31.84
    LOS_alpha: float = 2.15
    LOS_gamma: float = 1.9
    LOS_sigma: float = 4
    NLOS_beta: float = None
    NLOS_alpha: float = None
    NLOS_gamma: float = 2
    NLOS_sigma: float = None
    subscenario: str = None
    description: str = None
    bandwidth: int = 20  # 100 MHz
    hall_length: int = None  # m
    hall_width: int = None  # m
    gNB_distance: int = None  # m
    gNB_height: int = None  # m
    UE_height: int = 1.5  # m 1.5
    room_height: int = 10  # m
    gNB_antenna_elements: int = 1
    gNB_antenna_type: str = 'isotropic'
    sectorization: int = None
    UE_antenna_elements: int = 1
    UE_antenna_type: str = 'isotropic'
    clutter_density: int = None  # % r
    clutter_height: int = None  # m h_c
    clutter_size: int = None  # m d_clutter
    center_freq: float = 0.5  # GHz
    subcarrier_spacing = 15
    cell_radius = 10  # m
    max_num_devices_per_scenario: int = 10
    min_num_devices_per_scenario: int = 1
    device_transmit_power = 0  # dBm
    gNB_coordinates = None

    num_of_edge_servers = 'colocated'

    def _set_gNB_placement(self, hall_length, hall_width, gNB_height, gNB_distance):
        x_coordinates = np.arange((gNB_distance / 2), hall_length, gNB_distance).tolist()
        y_coordinates = np.arange((gNB_distance / 2), hall_width, gNB_distance).tolist()
        z_coordinates = [gNB_height]
        gNB_coordinates_tuple = list(product(x_coordinates, y_coordinates, z_coordinates))
        gNB_coordinates = np.array(list(map(list, gNB_coordinates_tuple)))
        return gNB_coordinates

    def _set_room_limits(self,hall_length, hall_width):
        x_max = hall_length
        y_max = hall_width
        return x_max,y_max

    def __post_init__(self):
        self.frequency = self._set_frequency_band(self.center_freq)
        self.num_PRBs = self._set_num_PRBs(self.subcarrier_spacing, self.bandwidth, self.frequency)
        self.mu = self._set_mu(self.subcarrier_spacing, self.frequency)
        self._set_PRB_bandwidth()

    def _set_PRB_bandwidth(self):
        self.PRB_bandwidth = 12 * self.subcarrier_spacing  # kHz SCS: [15, 30, 60, 120, 240] kHz

    def print_sim_params(self):
        super().print_sim_params()


@dataclass
class IndoorFactorySL(IndoorFactory):
    subscenario: str = 'SL'
    NLOS_beta: float = 33
    NLOS_alpha: float = 2.55
    NLOS_sigma: float = 5.7
    description: str = 'Big machineries composed of regular metallic surfaces. For example: several mixed production ' \
                       'areas with open spaces and memory/commissioning areas'
    hall_length: int = 120  # m
    hall_width: int = 60  # m
    gNB_distance: int = 20  # m
    gNB_height: int = 1.5  # m  below the average clutter height
    clutter_density: int = 0.2  # %
    clutter_height: int = 2  # m
    clutter_size: int = 10  # m

    def __post_init__(self):
        self.gNB_coordinates = self._set_gNB_placement(self.hall_length, self.hall_width, self.gNB_height,
                                                       self.gNB_distance)
        self.x_max, self.y_max = self._set_room_limits(self.hall_length,self.hall_width)

        self.frequency = self._set_frequency_band(self.center_freq)
        self.num_PRBs = self._set_num_PRBs(self.subcarrier_spacing, self.bandwidth, self.frequency)
        self.mu = self._set_mu(self.subcarrier_spacing, self.frequency)
        self._set_PRB_bandwidth()


    def _set_PRB_bandwidth(self):
        self.PRB_bandwidth = 12 * self.subcarrier_spacing  # kHz SCS: [15, 30, 60, 120, 240] kHz


@dataclass
class IndoorFactoryDL(IndoorFactory):
    subscenario: str = 'DL'
    NLOS_beta: float = 18.6
    NLOS_alpha: float = 3.57
    NLOS_sigma: float = 7.2
    description: str = 'Small to medium metallic machinery and objects with irregular structure. For example: ' \
                       'assembly and production lines surrounded by mixed smallsized machineries '
    hall_length: int = 300  # m
    hall_width: int = 150  # m
    gNB_distance: int = 50  # m
    gNB_height: int = 1.5  # m
    clutter_density: int = 0.2  # % transformed
    clutter_height: int = 2  # m
    clutter_size: int = 10  # m

    def __post_init__(self):
        self.gNB_coordinates = self._set_gNB_placement(self.hall_length, self.hall_width, self.gNB_height,
                                                       self.gNB_distance)


@dataclass
class IndoorFactorySH(IndoorFactory):
    subscenario: str = 'SH'
    NLOS_beta: float = 32.4
    NLOS_alpha: float = 2.3
    NLOS_sigma: float = 5.9
    description: str = 'Big machineries composed of regular metallic surfaces. For example: several mixed production ' \
                       'areas with open spaces and memory/commissioning areas'
    hall_length: int = 300  # m
    hall_width: int = 150  # m
    gNB_distance: int = 50  # m
    gNB_height: int = 8  # m above the average clutter height
    clutter_density: int = 0.6  # %
    clutter_height: int = 6  # m
    clutter_size: int = 2  # m

    def __post_init__(self):
        self.gNB_coordinates = self._set_gNB_placement(self.hall_length, self.hall_width, self.gNB_height,
                                                       self.gNB_distance)


@dataclass
class IndoorFactoryDH(IndoorFactory):
    subscenario: str = 'DH'
    NLOS_beta: float = 33.63
    NLOS_alpha: float = 2.19
    NLOS_sigma: float = 4
    description: str = 'Small to medium metallic machinery and objects with irregular structure. For example: ' \
                       'assembly and production lines surrounded by mixed smallsized machineries '
    hall_length: int = 120  # m
    hall_width: int = 60  # m
    gNB_distance: int = 20  # m
    gNB_height: int = 8  # m
    clutter_density: int = 0.6  # %
    clutter_height: int = 6  # m
    clutter_size: int = 2  # m

    def __post_init__(self):
        self.gNB_coordinates = self._set_gNB_placement(self.hall_length, self.hall_width, self.gNB_height,
                                                       self.gNB_distance)

