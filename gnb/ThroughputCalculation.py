import numpy as np
from runtime.data_classes import States


# todo: UL/ DL ratio (so far DDDD format)
# todo: add number of beams (beamforming)
# check: TDD or FDD? I see no difference in throughput in the calculator
# what we use is OFDMA, so why TDD?
class ThroughputCalculation:
    def __init__(self, simulation):
        self.simulation = simulation
        self.j = 1  # j number of aggregated component carriers (j=1, single carrier)
        self.overhead_dl = 0.14  # overhead of control channels for DL 3GPP 38.306 for FR1
        self.overhead_ul = 0.08
        self.v = self.simulation.sim_params.scenario.mimo_antennas  # maximum number of MIMO layers (max 8 in DL, 4 in UL)
        self.Rmax = 0.92578125  # value depends on the type of coding from 3GPP 38.212 and 238.214
        self.f = 1  # scaling factor from 3GPP 38.306
        self.data_rate = None
        self.sinr_to_cqi_dict = {-6.7: 1, -4.7: 2, -2.3: 3, 0.2: 4, 2.4: 5, 4.3: 6, 5.9: 7, 8.1: 8, 10.3: 9, 11.7: 10,
                            14.1: 11, 16.3: 12, 18.7: 13, 21.0: 14, 22.7: 15}

        self.cqi_to_modulation = {1: "QPSK", 7: "16QAM", 10: "64QAM", }  # is it for LTE? no 256 QAM?
        self.modulation_name_to_oder = {"QPSK": 2, "16QAM": 4, "64QAM": 6, "256QAM": 8}
        self.checked_flag = False
        self.sum_sinr_per_ue = np.zeros(len(self.simulation.devices_per_scenario))
        self.count_tti_ue_is_served = np.zeros(len(self.simulation.devices_per_scenario))

    def calculate_final_data_rate(self, ue, SINR_matrix):
        if ue.state != States.rrc_connected:
            return
        overhead = self.get_overhead()
        sinr = SINR_matrix[ue.ID, ue.my_gnb.ID]
        qm = self.calc_modulation_order_from_sinr(sinr)
        if self.simulation.sim_params.scenario.scenario == 'Indoor':
            ts_mu_s = (10 ** (-3)) / (14 * 2 ** self.simulation.sim_params.scenario.mu)
        elif ue.my_gnb.type == 'macro':
            ts_mu_s = (10 ** (-3)) / (14 * 2 ** self.simulation.sim_params.scenario.mu_macro)
        elif ue.my_gnb.type == 'micro':
            ts_mu_s = (10 ** (-3)) / (14 * 2 ** self.simulation.sim_params.scenario.mu_micro)
        else:
            raise NameError("Cannot calc mu for these ran_simulation parameters")
        user_rate = self.calc_data_rate(qm, len(ue.my_prbs), overhead, ts_mu_s)
        self.data_rate[ue.ID, ue.my_gnb.ID] = user_rate
        ue.my_rate = user_rate
        if len(ue.my_prbs) > 0:  # only log SINR values when the device is served
            self.sum_sinr_per_ue[ue.ID] += sinr
            self.count_tti_ue_is_served[ue.ID] += 1
        # elif len(ue.my_prbs) == 0:
        #     print(f"UE {ue.ID} gets 0 data rate at {self.ran_simulation.TTI}")
        if not self.checked_flag:
            self.check_that_user_is_connected_to_only_gnb()

    def calc_data_rate(self, qm, num_PRBs, overhead, ts_mu_s):
        data_rate = 0
        for _ in range(self.j):
            data_rate += 10 ** (-6) * self.v * qm * self.f * self.Rmax * num_PRBs * 12 / ts_mu_s * (1 - overhead)
        return data_rate

    def calc_data_rate_per_prb(self, ue, sinr):
        if ue.state != States.rrc_connected:
            return
        overhead = self.get_overhead()
        qm = self.calc_modulation_order_from_sinr(sinr)
        data_rate = 0
        for _ in range(self.j):
            data_rate += self.v * qm * self.f * self.Rmax * 12 * (1 - overhead)/8
        return data_rate

    def calc_max_data_rate(self):
        overhead = self.get_overhead()
        qm = 8
        if self.simulation.sim_params.scenario.scenario == 'Indoor':
            num_PRBs = self.simulation.sim_params.scenario.num_PRBs
            ts_mu_s = (10 ** (-3)) / (14 * 2 ** self.simulation.sim_params.scenario.mu)
        else:
            num_PRBs = self.simulation.sim_params.scenario.num_PRBs_macro
            ts_mu_s = (10 ** (-3)) / (14 * 2 ** self.simulation.sim_params.scenario.mu_macro)

        data_rate = self.calc_data_rate(qm, num_PRBs, overhead, ts_mu_s)
        return data_rate

    def calc_modulation_order_from_sinr(self, sinr):
        cqi = self.calc_cqi_from_sinr(sinr)
        modulation_name, modulation_order = self.calc_modulation_from_cqi(cqi)
        return modulation_order

    def calc_cqi_from_sinr(self, sinr):
        cqi = 1
        for sinr_key in self.sinr_to_cqi_dict:
            if sinr >= sinr_key:
                cqi = self.sinr_to_cqi_dict[sinr_key]
        return cqi

    def calc_modulation_from_cqi(self, cqi):
        modulation_name = "QPSK"
        for cqi_key in self.cqi_to_modulation:
            if cqi >= cqi_key:
                modulation_name = self.cqi_to_modulation[cqi_key]
        order = self.modulation_name_to_oder[modulation_name]
        return modulation_name, order

    def get_overhead(self):
        # todo: add 0.18 for FR2 DL; 0.10 for FR2 UL
        if self.simulation.sim_params.communication_type == 'UL':
            overhead = self.overhead_ul
        elif self.simulation.sim_params.communication_type == 'DL':
            overhead = self.overhead_dl
        else:
            raise Exception
        return overhead

    def check_that_user_is_connected_to_only_gnb(self):
        for row in self.data_rate:
            assert max(row) == sum(row), self.data_rate

    def check_that_total_rate_per_gnb(self):
        # todo: check that a gNB does not provide more than it's maximum rate
        # max rate can be calculated the same way for total num_PRBs
        pass