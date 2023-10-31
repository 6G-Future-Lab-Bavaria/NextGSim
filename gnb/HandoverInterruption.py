# @Author: Alba Jano, Anna Prado
# @Date: 2020-11-15
# @Email: alba.jano@tum.de, anna.prado@tum.de
# @Last modified by: Alba Jano

class HandoverInterruption:
    # 1. 5G New Radio—NR and NG-RAN Overall Description-Stage 2, 3GPP TS 38.300 Release 15, Version 15.5.0, Mar. 2019.
    # 2. Mohamed, Abdelrahim, et al. "Memory-full context-aware predictive mobility management
    # in dual connectivity 5G networks." IEEE Access 6 (2018): 9655-9666.
    def __init__(self, simulation):
        self.simulation = simulation
        self.transmission_latency_and_processing_btw_gnb_ue = None  # ms
        self.transmission_latency_btws_gnbs = None  # ms
        self.processing_latency_at_gnb = None  # ms
        self.ue_detach_and_access_new_gnb_of_ue = None  # ms
        self.params_from_memory_full_mm_paper()
        # self.rach_procedure = None

    def params_from_memory_full_mm_paper(self):
        self.transmission_latency_and_processing_btw_gnb_ue = 6.5  # ms
        self.transmission_latency_btws_gnbs = 5  # ms
        self.processing_latency_at_gnb = 4  # ms
        self.ue_detach_and_access_new_gnb_of_ue = 12  # ms  # fixme: 20 ms in HO mechanisms in NR paper

    # def params_from_sync_rach_less_handover_nokia_paper(self):
    #     # self.transmission_latency_and_processing_btw_gnb_ue = 6.5  # ms
    #     self.process_and_build_handover_cmd_serving = 5  # ms
    #     self.x2_message_process_target = 27  # ms
    #     self.transmission_latency_btws_gnbs = 5  # ms
    #     self.processing_latency_at_gnb = 5  # ms
    #     self.ue_detach_and_access_new_gnb_of_ue = 20  # ms
    #     self.rach_procedure = 15  # ms

    def calc_handover_preparation_time(self, target_gnb):
        if self.simulation.sim_params.instantaneous_handover: return True, 0
        # later: handover can be made after the MR is processed => processing_latency_at_gnb latency
        # later: transmission latency from UE => use SNR which transmission_latency_and_processing_btw_gnb_ue ms old
        waiting = 0
        waiting += self.processing_latency_at_gnb  # Processing of the MR at the source gNB
        waiting += self.transmission_latency_btws_gnbs  # Tx of handover request from serving to target gNB
        waiting += self.processing_latency_at_gnb  # Processing at the target gNB
        waiting += self.transmission_latency_btws_gnbs  # Tx of handover reply to the serving gNB (ACK, NACK)
        waiting += self.processing_latency_at_gnb  # Processing at the serving gNB
        admission_decision = self.admission_control_response(target_gnb)
        # self.log(f"Admission {admission_decision}, waiting for handover {waiting} ms")
        if not admission_decision:
            return admission_decision, waiting
        waiting += self.transmission_latency_and_processing_btw_gnb_ue  # Tx to the UE handover trigger msg
        return admission_decision, waiting

    def calc_handover_interruption(self, target_gnb):
        if self.simulation.sim_params.instantaneous_handover: return 0
        interruption = 0
        # interruption += 15  # ms # RRC processing
        # interruption += 20  # self.ue_detach_and_access_new_gnb_of_ue  # UE detaches and accessed the serving gNB
        interruption += 8.5  # self.calc_random_access_latency()  # RACH
        interruption += 6  # ms Handover Command (HO mechanism for NR paper)
        # UE syncs to the new cell and completes RRC HO procedure
        # Add state transition latency or is it included in detach and access latency
        # Core network switching; data forwarding; will the data arrive on time to the target gNB?
        return interruption

    def admission_control_response(self, target_gnb):
        # todo: check the load of the target gNB and if it's bellow some threshold, then accept the device
        # num_connected_users = len(target_gnb.connected_devices)
        return True

    def calc_random_access_latency(self):
        # todo: add a mean and std of time it takes to perform RACH
        # should depend on the number of connected UEs to the target gNB and amount of available resources
        # num_connected_users = len(target_gnb.connected_devices)
        # RACH failure probability (?)
        rach_latency = 8.5  # ms
        return rach_latency

    def calc_remove_prep_cell_at_gnb_latency(self):
        # CHO
        latency = 0
        latency += self.transmission_latency_and_processing_btw_gnb_ue  # should be without processing at UE
        latency += self.processing_latency_at_gnb
        latency += self.transmission_latency_btws_gnbs
        latency += self.processing_latency_at_gnb
        return latency

    def calc_time_to_reconnect_after_failure(self):
        # fixme: set a realistic value. Connecting after RLF takes longer than just RACH-latency!
        latency = 0
        latency += self.calc_random_access_latency()
        latency = 1000  # ms
        return latency