from dataclasses import dataclass
from tabulate import tabulate


@dataclass
class MeasurementParams():
    # Measurement gap lengths of 1.5, 3, 3.5, 4, 5.5, and 6 ms with measurement gap repetition periodicity of
    #  20, 40, 80, and 160 ms are defined in NR.
    #  http://howltestuffworks.blogspot.com/2020/01/5g-nr-measurement-gaps.html
    update_ue_position_gap = 1  # ms
    channel_measurement_periodicity = 1  # ms # TS38.133: FR2: 20 ms; FR1: 40 ms; LTE: 40 ms
    traffic_generation_periodicity = 1000  # ms
    # measurement_duration = 4  # ms # for 15 KHz can be 6 ms, 4, ms, 3 ms; also depends on subcarrier spacing
    # (see TS38.133 table 9.1.2-4)

    # Typical L3 filtering period is 200 ms from "Mobility management challenges in 3GPP heterogeneous networks"
    snr_averaging_time = 200  # 200 ms

    def print_sim_params(self):
        print("\nMeasurement Periodicity")
        print(tabulate([[self.channel_measurement_periodicity, self.update_ue_position_gap, self.snr_averaging_time]],
                       headers=['Channel (ms)', 'UE position update (ms)', 'SNR/RSRP average over (ms)']))


@dataclass
class Schedulers:
    round_robin: str = "Round Robin"
    dummy: str = 'dummy'


@dataclass
class States:
    rrc_idle: str = "RRC_IDLE"
    rrc_connected: str = "RRC_CONNECTED"
    rrc_inactive: str = "RRC_INACTIVE"


@dataclass
class AggregatedTraffic:
    model1 = 'uniform'
    model2 = 'beta(3,4)'


@dataclass
class MobilityModels:
    random_waypoint = 'Random Waypoint'


@dataclass
class BaseStations:
    indoor = 'Indor'
    micro = 'Micro'
    macro = 'Macro'


@dataclass
class Frequencies:
    fr1 = 'FR1'
    fr2 = 'FR2'


@dataclass
class Constants:
    speed_of_light: int = 3 * 10 ** 8  # m/s

    def __post_init__(self):
        pass

@dataclass
class EntityClass:
    physical_entities = ["Device", "EdgeServer", "GnB", "Router"]
    application_entities = ["Microservice"]

