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
class HandoverAlgorithms:
    normal_5g_mbb = 'Normal'  # Normal 5G Handover Make Before Break
    conditional_5g = 'CHO'  # Conditional 5G Handover
    echo_with_known_tr = 'ECHO_known'  # Enhanced Conditional Handover with known trajectory (full knowledge)
    echo_with_pred_tr = 'ECHO_pred'  # ECHO with predicted trajectory
    echo_with_current_pos = 'ECHO_current'
    echo_with_look_ahead = 'ECHO_look_ahead'  # ECHO with predicted trajectory with look_ahead
    echo_with_current_look_ahead = 'ECHO_current_look_ahead'


@dataclass
class ECHOVersions:
    distance_based = 'distance_based'  # Predicted UExy -> closed macro and micro gNB
    distance_based_one_macro = 'closed_ma_mi'  # Select among closed macro and micro gNBs
    force_closed_micro = 'force_closed_micro'  # Closed micro gNB has an offset


@dataclass
class CHOVersions:
    max_top_gnbs_always_preped = "Top gNBs always prepared"  # top_num_gnbs always are or being prepared to provide garantees
    up_to_top_gnbs_prepared = 'Up to top gNBs prepared'  # no more than top_num_gnbs are or being prepared


@dataclass
class HandoverParameters:
    ttt_exec = 320  # number of TTIs (ms) 120
    ttt_prep = 480  # ms
    a3_offset = 3  # dB
    event = 3  # todo: use it
    a5_offset_1 = -156  # dBm RSRP
    a5_offset_2 = - 31  # dBm RSRP
    # ho_decision_timer = 5  # ms
    # rsrp_threshold = -160  # s-criteria
    Qout = -8  # -8 dB
    Qin_duration = 600  # fixme 600 ms # from Ingo, On the Basics of CHO for 5G Mobility
    Qin = -6  # -6 dB
    handover_hof_t304_timer = 500  # 500 ms after receiving a handover cmd, if UE does not perform a handover within this time, then HOF
    # t310 ENUMERATED {ms0, ms50, ms100, ms200, ms500, ms1000, ms2000, ms4000, ms6000} (page 310)
    # https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/15.04.00_60/ts_138331v150400p.pdf


@dataclass
class ConditionalHandoverParameters:
    # Ingo, On the Basics of CHO for 5G Mobility
    prep_offset = -3  # dB  # -3 Ingo  # +3 3GPP
    exec_offset = 3  # dB # 3 Ingo # 5 3GPP  # 10
    remove_offset = -3  # prep_offset - 3
    replace_offset = 3  # dB fixme: set a real value
    with_ttt_exec = False  # in case CHO with TTT, set TTT in HandoverParameters
    with_ttt_prep = False  # in case CHO with TTT, set TTT in HandoverParameters
    event = 3  # 2, 3, 4
    a2_rsrp_threshold = -69  # dBm
    a4_rsrp_threshold = - 87  # dBm


@dataclass
class Constants:
    speed_of_light: int = 3 * 10 ** 8  # m/s

    def __post_init__(self):
        pass

# Added by Mert
@dataclass
class EntityClass:
    physical_entities = ["Device", "EdgeServer", "GnB", "Router"]
    application_entities = ["Microservice"]
