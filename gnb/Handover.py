# @Author: Alba Jano, Anna Prado
# @Date: 2020-11-15
# @Email: alba.jano@tum.de, anna.prado@tum.de
# @Last modified by: Alba Jano

import sys
from tabulate import tabulate
from termcolor import colored
from abc import ABC, abstractmethod
from collections import defaultdict
from gnb.HandoverInterruption import HandoverInterruption
from runtime.data_classes import HandoverParameters, MeasurementParams


class Handover(ABC):
    def __init__(self, simulation):
        self.simulation = simulation
        self.who_made_handovers = defaultdict(list)
        self.handover_interruption = HandoverInterruption(simulation)
        self.hof_dict = defaultdict(list)
        self.num_hof = 0
        self.modulation_count = {'better': 0, 'worse': 0, 'same': 0}
        self.no_data_forwarding_possible_per_user = defaultdict(int)
        self.user_cannot_rx_tx = defaultdict(int)

    @abstractmethod
    def main_handover_function(self, user):
        self.set_next_predicted_position_echo(user)
        user.my_sinr = self.simulation.channel.average_SINR[user.ID, user.my_gnb.ID]
        if not self.check_user_can_rx_tx(user):
            self.user_cannot_rx_tx[user.ID] += self.simulation.sim_params.TTI_duration
            # self.print_msg(device, f"UE {device.ID} cannot tx/rx with SINR = {device.my_sinr} dB", 'red')
        user.connected_to_gnbs[self.simulation.TTI] = user.my_gnb.ID
        self.check_if_hof(user)

    def set_next_predicted_position_echo(self, user):
        if 'ECHO' in self.simulation.sim_params.handover_algorithm \
                and self.simulation.TTI % MeasurementParams.update_ue_position_gap == 0:
            if 'look_ahead' not in self.simulation.sim_params.handover_algorithm:
                self.simulation.handover.set_next_predicted_position(user)

    def set_next_predicted_position_look_ahead(self):
        # only for ECHO with look ahead
        pass

    def count_resource_reservation_duration(self, gnb):
        # not for NHO, only for CHO
        pass

    def check_user_can_rx_tx(self, user):
        return user.my_sinr > HandoverParameters.Qout

    def start_ttt(self, user):
        current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
        user.ttt_finish = current_time + HandoverParameters.ttt_exec
        user.handover_prep_is_ongoing = False
        msg = f"2.5. Started TTT  for user {user.ID} with gNB {user.next_gnb.ID} at TTI={current_time}. My gNB is {user.my_gnb.ID}"
        self.print_msg(user, msg, 'red')

    def prepare_handover(self, user, target_gnb, prep_time_offset=0):
        # the source and target gNB exchange the UE parameters and allocate radio resources
        admission_decision, handover_preparation_time = \
            self.handover_interruption.calc_handover_preparation_time(target_gnb)
        # self.check_if_handover_increases_modulation_order(device, target_gnb, msg='Prep.')
        if admission_decision:
            current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
            user.handover_prep_time_finish = current_time + handover_preparation_time + prep_time_offset
            user.handover_prep_is_ongoing = True
            user.ttt_finish = None
            self.simulation.save_results.handover_preparation_waiting_time_per_user[user.ID] += \
                handover_preparation_time

        else:
            print(f"gNB {user.next_gnb.ID} rejected UE {user.ID} coming from {user.my_gnb.ID}")

    def execute_handover(self, user):
        # the UE disconnects from the source gNB and accesses the target gNB
        # print(f"User {device.ID}: {device.my_gnb.ID} ---> {device.next_gnb.ID}")
        assert user.my_gnb.ID != user.next_gnb.ID, \
            f"HO from gNB {user.my_gnb.ID} to gNB {user.next_gnb.ID}"
        self.check_if_handover_increases_modulation_order(user, user.next_gnb, msg='Exec.')
        current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration

        handover_interruption_time = self.handover_interruption.calc_handover_interruption(user.next_gnb)
        if self.check_if_data_forwd_possible(user):
            # handover_interruption_time -= 6  # HC ms  # fixme: for data forwarding
            pass
        user.hit_finish = current_time + handover_interruption_time
        user.handover_prep_time_finish = None
        user.rlf_finish_timer = None
        user.handover_t304_finish = current_time + HandoverParameters.handover_hof_t304_timer
        self.simulation.save_results.handover_interruption_time_per_user[user.ID] += handover_interruption_time
        user.previous_gnb = user.my_gnb
        user.my_gnb.connected_devices.remove(user)
        self.who_made_handovers[self.simulation.TTI].append(user.ID)
        self.simulation.plot_allocation_flag = True
        user.ttt_finish = None

    def check_if_data_forwd_possible(self, user):
        sinr = self.simulation.channel.measured_SINR[user.ID, user.my_gnb.ID]  # fixme measured or average SINR?
        if sinr > HandoverParameters.Qout:
            # UE can send a bye message to sgNB, which will start data forwarding
            return True
        else:
            self.no_data_forwarding_possible_per_user[user.ID] += 1
            return False

    def complete_handover(self, user):
        if self.simulation.sim_params.traffic_model:
            user.my_gnb.connected_devices.remove(user)
        user.my_gnb = user.next_gnb
        user.my_gnb.connected_devices.append(user)
        user.next_gnb = None
        user.hit_finish = None
        user.handover_t304_finish = None
        user.rlf_finish_timer = None
        self.simulation.plot_allocation_flag = True

    def set_handover_params_to_default(self, user):
        user.next_gnb = None
        user.ttt_finish = None
        user.handover_prep_is_ongoing = False
        user.hit_finish = None
        user.handover_prep_time_finish = None
        user.handover_t304_finish = None  # NormalHandoverParameters.handover_hof_t304_timer
        user.rlf_finish_timer = None
        # assert 0, "Check this function implementation"

    def check_if_handover_increases_modulation_order(self, user, prep_cell, msg):
        sinr_target = self.simulation.channel.average_SINR[user.ID, prep_cell.ID]
        sinr_serving = self.simulation.channel.average_SINR[user.ID, user.my_gnb.ID]
        modulation_target = self.simulation.throughput_calc.calc_modulation_order_from_sinr(sinr_target)
        modulation_serving = self.simulation.throughput_calc.calc_modulation_order_from_sinr(sinr_serving)
        msg = msg + f"gNb {user.my_gnb.ID} -> gNB {prep_cell.ID}; Modulation order:  {modulation_serving} --> {modulation_target}"
        if modulation_target > modulation_serving:
            # print(colored(msg, 'green'))
            if 'Exec' in msg:
                self.modulation_count['better'] += 1
        elif modulation_target == modulation_serving:
            # print(colored(msg, 'blue'))
            if 'Exec' in msg:
                self.modulation_count['same'] += 1
        else:
            # print(colored(msg, 'red'))
            if 'Exec' in msg:
                self.modulation_count['worse'] += 1

    def select_channel_metric_to_use(self, SINR_matrix, RSRP_matrix):
        if self.simulation.sim_params.channel_metric_for_handover == 'SINR':
            channel_matrix = SINR_matrix
        elif self.simulation.sim_params.channel_metric_for_handover == 'RSRP':
            channel_matrix = RSRP_matrix
        else:
            raise NotImplementedError(f"Handover only works with SINR and RSRP, not with {self.simulation.sim_params.channel_metric_for_handover}")
        return channel_matrix

    def check_if_hof(self, user):
        # HOFs in RLF monitor (RLF + HIT is not None). Maybe remove this function, double check.
        current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
        if user.handover_t304_finish and user.handover_t304_finish <= current_time:
            print(f"HOF: User {user.ID} at TTI = {current_time} with {user.handover_t304_finish}", file=sys.stderr)
            assert 0
            self.log_hof(user)
            # todo: when to reconnect again: add this device to RLF dictionary; the reconnection can be done there
            user.time_to_connect_again = current_time + self.handover_interruption.calc_time_to_reconnect_after_failure()

    def log_hof(self, user):
        self.hof_dict[self.simulation.TTI].append(user.ID)
        self.num_hof += 1

    def print_handover_parameters(self):
        print("\n")
        print(tabulate([['Ping-pong window', self.simulation.handover_metrics.ping_pong_window],
                        ['Tx latency and proces btw gNB and UE', self.handover_interruption.transmission_latency_and_processing_btw_gnb_ue],
                        ['Tx latency btw gNBs', self.handover_interruption.transmission_latency_btws_gnbs],
                        ['Processing at gNB', self.handover_interruption.processing_latency_at_gnb],
                        ['UE detach and access new gNB', self.handover_interruption.ue_detach_and_access_new_gnb_of_ue],
                        ['RACH latency', self.handover_interruption.calc_random_access_latency()],
                        ['HIT', self.handover_interruption.calc_handover_interruption(None)],
                        ['HO prep time', self.handover_interruption.calc_handover_preparation_time(None)[1]],
                        ['RLF Recovery Time', self.simulation.handover.handover_interruption.calc_time_to_reconnect_after_failure()]
                        ],
                       headers=['Handover Parameter', 'Value (ms)']))
        print("\n")

    def print_msg(self, user, msg, color):
        print(colored(msg, color))

    def print_error(self, user, msg):
        print(msg, file=sys.stderr)