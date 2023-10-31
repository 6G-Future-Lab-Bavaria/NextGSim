from dataclasses import dataclass


# NOT USING
@dataclass()
class IndoorHotspoteMBB:
    scenario: str = 'IndoorHotspoteMBB'
    carrier_frequency = 4  # GHz
    BS_antenna_height = 3  # m
    UE_antenna_height = 1.5  # m
    bandwidth = 20  # MHz - there are different options for
    total_transmit_power_per_TRxP = 24  # dBm
    UE_power_class = 23  # dBm
    inter_site_distance = 20  # m
    number_of_antennas_elements_per_TRxP = 256  # Tx/Rx
    number_of_UE_antenna_elements = 8  # Tx/Rx
    device_deployment = "100 % indoor randomly and uniformly distributed over the area"
    ue_mobility_model = "Fixed and identical speed |v| of all UEs, randomly and uniformly distributed direction"
    UE_speed_indoor = 3  # km/h
    UE_speed_outdoor = None
    BS_noise_figure = 5  # dB
    UE_noise_figure = 7  # dB
    BS_antenna_element_gain = 5  # dBi
    UE_antenna_element_gain = 0  # dBi
    thermal_noise_level = -174  # dBm/Hz
    traffic_model = "Full buffer"


@dataclass()
class DenseUrbaneMMB:
    scenario: str = 'DenseUrbaneMMB'
    carrier_frequency = 4  # GHz
    BS_antenna_height = 25  # m
    UE_antenna_height = 1.5  # m outdoor - indoor they use a formula
    bandwidth = 20  # MHz
    total_transmit_power_per_TRxP = 44  # dBm
    UE_power_class = 23  # dBm
    percentage_of_high_loss_building_type = 20  # %
    percentage_of_low_loss_building_type = 80  # %
    inter_site_distance = 200  # m
    number_of_antennas_elements_per_TRxP = 256  # Tx/Rx
    number_of_UE_antenna_elements = 8  # Tx/Rx
    device_deployment = "80% indoor 20% outdoor, randomly and uniformly distributed over the area"
    ue_mobility_model = "Fixed and identical speed |v| of all UEs, randomly and uniformly distributed direction"
    UE_speed_indoor = 3  # km/h
    UE_speed_outdoor = 30  # km/h
    BS_noise_figure = 5  # dB
    UE_noise_figure = 7  # dB
    BS_antenna_element_gain = 8  # dBi
    UE_antenna_element_gain = 0  # dBi
    thermal_noise_level = -174  # dBm/Hz
    traffic_model = "Full buffer"


@dataclass()
class RuraleMMB:
    scenario: str = 'RuraleMMB'
    carrier_frequency = 700  # MHz
    BS_antenna_height = 35  # m
    UE_antenna_height = 1.5  # m outdoor
    bandwidth = 20  # MHz
    total_transmit_power_per_TRxP = 49  # dBm
    UE_power_class = 23  # dBm
    percentage_of_high_loss_building_type = "100% low loss"
    percentage_of_low_loss_building_type = "100% low loss"
    inter_site_distance = 1732  # m
    number_of_antennas_elements_per_TRxP = 64  # Tx/Rx
    number_of_UE_antenna_elements = 4  # Tx/Rx
    device_deployment = "50% indoor 50% outdoor, randomly and uniformly distributed over the area"
    ue_mobility_model = "Fixed and identical speed |v| of all UEs, randomly and uniformly distributed " \
                                 "direction "
    UE_speed_indoor = 3  # km/h
    UE_speed_outdoor = 120  # km/h
    BS_noise_figure = 5  # dB
    UE_noise_figure = 7  # dB
    BS_antenna_element_gain = 8  # dBi
    UE_antenna_element_gain = 0  # dBi
    thermal_noise_level = -174  # dBm/Hz
    traffic_model = "Full buffer"


@dataclass()
class UrbanMacomMTC:
    scenario: str = 'UrbanMacomMTC'
    carrier_frequency = 700  # MHz
    BS_antenna_height = 25  # m
    UE_antenna_height = 1.5  # m outdoor
    bandwidth = 20  # MHz
    total_transmit_power_per_TRxP = 49  # dBm
    UE_power_class = 23  # dBm
    percentage_of_high_loss_building_type = "20% low loss"
    percentage_of_low_loss_building_type = "80% low loss"
    inter_site_distance = 500  # m
    number_of_antennas_elements_per_TRxP = 64  # Tx/Rx
    number_of_UE_antenna_elements = 2  # Tx/Rx
    device_deployment = "80% indoor 20% outdoor, randomly and uniformly distributed over the area"
    ue_mobility_model = "Fixed and identical speed |v| of all UEs, randomly and uniformly distributed " \
                                 "direction "
    UE_speed_indoor = 3  # km/h
    UE_speed_outdoor = 120  # km/h
    BS_noise_figure = 5  # dB
    UE_noise_figure = 7  # dB
    BS_antenna_element_gain = 8  # dBi
    UE_antenna_element_gain = 0  # dBi
    thermal_noise_level = -174  # dBm/Hz
    traffic_model = "With layer 2 PDU (Protocol Data Unit) message size of 32 bits: 1 message/day/device or " \
                             "1 message/2 hours/device6 Packet arrival follows Poisson arrival process for non-full " \
                             "buffersystem-level ran_simulation "


@dataclass()
class UrbanMacroURLLC:
    scenario: str = 'UMi'
    x_max: int = 2000  # set to 120
    y_max: int = 2000
    min_bs_ue_dist: int = 10  # m
    gnb_antenna_height: int = 25  # m
    ue_antenna_height: float = 1.5  # m
    effective_env_height: int = 1  # m
    bandwidth: int = 20 * 10 ** 6  # Hz
    subcarrier_spacing = 30
    center_freq: float = 4  # GHz
    center_freq_multiplier = 10 ** 9
    transmit_power = 49  # dBm for DL, 23 dBm for UL
    inter_site_dist: float = 500  # m
    cell_radius = 50  # m
    max_num_devices_per_cell: int = 20  # todo: not per cell, per scenario
    min_num_devices_per_cell: int = 1  # todo: not per cell, per scenario
    mobility_traces_filename = 'mobility/mobility_traces/traces_30.0users_120.0x50.0size_0.95hurst_5.0hours.mat'
    BS_noise_figure = 5  # dB
    UE_noise_figure = 7  # dB
    shadowing_std_los = 4  # dB
    shadowing_std_nlos = 7.82  # dB
    gNB_antenna_gain = 8  # dBi
    UE_antenna_gain = 0  # dBi
    if bandwidth > 100 * 10 ** 6:
        assert 0, "Bandwidth must be up to 100 MHz according to 3GPP"
    # UE_power_class = 23  # dBm
    # percentage_of_high_loss_building_type = "80% low loss"
    # percentage_of_low_loss_building_type = "20% low loss"
    # number_of_antennas_elements_per_TRxP = 256  # Tx/Rx
    # number_of_UE_antenna_elements = 8  # Tx/Rx