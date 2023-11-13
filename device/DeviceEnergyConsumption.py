
class DeviceEnergyConsumption:
    # Paper-On the Flexible and Performance-Enhanced Radio Resource Control for 5G NR networks
    def __init__(self):

        self.deep_sleep_relative_power_consumption_per_slot = 1
        self.deep_sleep_transition_time = 20  # unit: ms
        self.deep_sleep_transition_power = 450
        self.light_sleep_relative_power_consumption_per_slot = 20
        self.light_sleep_transition_time = 6  # unit: ms
        self.light_sleep_transition_power = 100
        self.micro_sleep_relative_power_consumption_per_slot = 45
        self.micro_sleep_transition_time = 0  # unit: ms
        self.micro_sleep_transition_power = 0
        self.PDCCH_only_relative_power_consumption_per_slot = 100
        self.PDCCH_PDSCH_only_relative_power_consumption_per_slot = 300
        self.PUCCH_relative_power_consumption_per_slot = 250
        self.SSB_relative_power_consumption_per_slot = 100
        self.CSI_RS_relative_power_consumption_per_slot = 100

        # Paper-On the Flexible and Performance-Enhanced Radio Resource Control for 5G NR networks
        self.average_delay_due_to_RACH_scheduling_period = 0.50
        self.RACH_preamble = 1
        self.preamble_detection_and_transmission_of_RA_response = 2
        self.transmission_of_RA_response = 1
        self.UE_processing_delay = 5
        self.transmission_of_RRC_connection_setup_resume_request = 1
        self.processing_delay_in_gNB_L2_and_RRC = 4
        self.transmission_of_RRC_connection_setup_resume = 1
        self.processing_delay_in_UE_L2_RRC = 15
        self.transmission_of_RRC_setup_resume_completed = 1
        self.processing_delay_in_gNB_Uu_NGC = 4
        self.NGC_transfer_delay = None
        self.AMF_processing_delay = 15
        self.MGC_transfer_delay = None
        self.processing_delay_in_gNB_NGC_Uu = 4
        self.transmission_of_RRC_security_mode_command_and_connection_reconfiguration = 1
        self.TTI_aligment = 0.5
        self.processing_delay_in_UE_L2_and_RRC = 20
        self.RRC_setup_procedure_total_CP_delay = 76.004  # unit: ms
        self.RRC_resume_procedure_total_CP_delay = 31.50  # unit: ms
        self.no_RRC_switching_procedure_total_CP_delay = 2.86  # unit: ms
        self.RRC_setup_relative_power_consumption = 4800.00  # unit: -
        self.RRC_resume_relative_power_consumption = 2542.50  # unit: -
        self.no_RRC_state_switching_relative_power_consumption = 194.29  # unit: -

    def RRC_Resume_relative_energy_consumption(self):
        return self.RRC_resume_relative_power_consumption

    def small_packet_transmission_energy_consumption(self):
        return self.no_RRC_state_switching_relative_power_consumption

    def RRC_Setup_relative_energy_consumption(self):
        return self.RRC_setup_relative_power_consumption
