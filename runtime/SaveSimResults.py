# @Author: Anna Prado
# @Date: 2020-11-15
# @Email: anna.prado@tum.de
# @Last modified by: Alba Jano
import sys

import numpy as np
import time
import matplotlib.pyplot as plt
from collections import defaultdict
from utilities import save_results_to_json
from data_classes import HandoverAlgorithms, MeasurementParams, ConditionalHandoverParameters, HandoverParameters
from utilities import plot_mobility


class SaveSimResults:
    def __init__(self, simulation):
        self.simulation = simulation
        # self.who_made_handovers_at_TTI = {}
        self.who_made_handovers_at_TTI_clean = {}
        # self.measured_sinr_at_TTI = {}
        # self.measured_rsrp_at_TTI = {}
        self.ping_pong_per_user = {}
        self.total_num_handovers_over_sim = 0
        self.sum_throughput_per_user = defaultdict(float)
        self.handover_interruption_time_per_user = defaultdict(float)
        self.handover_preparation_waiting_time_per_user = defaultdict(float)
        self.prepared_cells_count_dict = {}
        # for new metrics
        self.current_throughput = 0  # throughput within a second
        self.sum_throughput_per_sec = []
        self.current_num_handovers = 0  # within a second
        self.num_handovers_per_sec = []
        self.current_rlf = 0
        self.num_rlf_per_sec = []
        self.delay_per_user = defaultdict(float)
        self.drop_rate_per_user = defaultdict(float)

    def reset_per_tti_vars(self):
        pass

    def calc_sum_tp(self):
        pass

    def calc_qos(self):
        pass

    def print_rlf_and_hof(self):
        print("RLF")
        print(self.simulation.monitor_rlf.rlf_dict)
        print("HOF")
        print(self.simulation.handover.hof_dict)

    def get_number_final_ping_pongs(self):
        for user in self.simulation.devices_per_scenario:
            num_ping_pongs = self.simulation.handover_metrics.calc_num_ping_pong_handovers_per_user(user)
            self.ping_pong_per_user[user.ID] = num_ping_pongs
        # print(f"Ping pong handovers per device {self.ping_pong_per_user}")

    def get_average_delay(self):
        for user in self.simulation.devices_per_scenario:
            self.delay_per_user[user.ID] = np.mean(np.array(user.delays))

    def get_drop_rate(self):
        for user in self.simulation.devices_per_scenario:
            user.dropped_packets += user.get_buffer_stats()
            self.drop_rate_per_user[user.ID] = user.dropped_packets/(user.dropped_packets+user.transmitted_packets)

    def print_handovers_per_tti(self):
        print("Handovers per TTI")
        print(self.who_made_handovers_at_TTI_clean)

    def save_results(self):
        self.on_sim_end()
        if 'CHO' in self.simulation.sim_params.handover_algorithm:
            count_prepared_cells = self.simulation.handover.count_prepared_cells
            count_released_cells = self.simulation.handover.count_released_cells
            count_prepared_but_not_used_cells = self.simulation.handover.count_prepared_but_not_used_cells
            num_top_gnbs = self.simulation.handover.num_top_gnbs
            count_wasted_ttis_per_gnb = self.simulation.handover.count_wasted_ttis_per_gnb
        elif self.simulation.sim_params.handover_algorithm == HandoverAlgorithms.normal_5g_mbb:
            count_prepared_cells = count_released_cells = self.total_num_handovers_over_sim
            count_prepared_but_not_used_cells = 0
            num_top_gnbs = count_wasted_ttis_per_gnb = 0
        else:
            raise NotImplementedError("No such handover algorithm")

        num_handovers_per_user_per_second = self.total_num_handovers_over_sim / self.simulation.sim_params.num_TTI \
                                            / len(self.simulation.devices_per_scenario) * 1000

        handover_alg = self.simulation.sim_params.handover_algorithm + self.simulation.handover.version
        if 'TTT' in handover_alg:
            self.simulation.results_name += 'T'
        # if self.ran_simulation.sim_params.handover_algorithm == HandoverAlgorithms.conditional_enhanced:
        #               handover_alg += ('-' + self.ran_simulation.handover.echo_version)
        average_sinr = self.simulation.throughput_calc.sum_sinr_per_ue / \
                       self.simulation.throughput_calc.count_tti_ue_is_served
        results = {'num_ttis': self.simulation.sim_params.num_TTI,
                   'ttt_duration': self.simulation.sim_params.TTI_duration,
                   'num_users': len(self.simulation.devices_per_scenario),
                   'num_gnbs': len(self.simulation.gNBs_per_scenario),
                   'scenario': self.simulation.sim_params.scenario.scenario,
                   'handover_alg': handover_alg,
                   'num_top_gnbs': num_top_gnbs,
                   'sim_params': self.simulation.sim_params.results_name,
                   'start_offset': self.simulation.sim_params.start_offset,
                   'center_freq_micro': self.simulation.sim_params.scenario.center_freq_micro,
                   'mobility_model': self.simulation.sim_params.mobility_model,
                   'mob_traces_filename': self.simulation.sim_params.scenario.mobility_traces_filename,
                   'always_los_flag': self.simulation.sim_params.always_los_flag,
                   'los_update_periodicity': self.simulation.sim_params.los_update_periodicity,
                   'snr_averaging': self.simulation.sim_params.snr_averaging,
                   'snr_averaging_time': MeasurementParams.snr_averaging_time,
                   'channel_measurement_periodicity': MeasurementParams.channel_measurement_periodicity,
                   'total_num_handovers': self.total_num_handovers_over_sim,
                   'user_cannot_rx_tx': self.simulation.handover.user_cannot_rx_tx,
                   'num_handovers_per_user_per_second': num_handovers_per_user_per_second,
                   'count_prepared_cells': count_prepared_cells,
                   'count_released_cells': count_released_cells,
                   'count_prepared_but_not_used_cells': count_prepared_but_not_used_cells,
                   'count_wasted_ttis_per_gnb': count_wasted_ttis_per_gnb,
                   'no_data_forwarding_possible_count': self.simulation.handover.no_data_forwarding_possible_per_user,
                   'sum_throughput_per_user': self.sum_throughput_per_user,
                   # 'average_sinr': list(average_sinr),
                   'modulation_count': self.simulation.handover.modulation_count,
                   'instantaneous_handover': self.simulation.sim_params.instantaneous_handover,
                   'handover_interruption_time': self.handover_interruption_time_per_user,
                   'handover_prep_waiting': self.handover_preparation_waiting_time_per_user,
                   'HOF': self.simulation.handover.num_hof,
                   'RLF': self.simulation.monitor_rlf.num_rlf,
                   'HOF_dict': self.simulation.handover.hof_dict,
                   # 'RLF_dict': self.ran_simulation.monitor_rlf.rlf_dict,
                   "ping-pong": self.ping_pong_per_user,
                   # 'RLF at position': self.ran_simulation.monitor_rlf.rlf_at_position, # does not contain all RLFs
                   'who_made_handovers_at_TTI': self.who_made_handovers_at_TTI_clean,
                   'num_handovers_per_sec': self.num_handovers_per_sec,
                   'sum_throughput_per_sec': self.sum_throughput_per_sec,
                   'num_rlf_per_sec': self.num_rlf_per_sec,
                   'rlf_per_user': self.simulation.monitor_rlf.rlf_per_user,
                   }

        t = time.time()
        self.simulation.sim_params.results_name = str(int(t)) + '_' + self.simulation.sim_params.results_name
        save_results_to_json(results, 'results_' + self.simulation.sim_params.results_name)
        print(f"Number of handovers {results['total_num_handovers']}, RLFs {results['RLF']}")
        # if len(self.ran_simulation.devices_per_scenario) <= 2:
        #     print(self.ran_simulation.handover.prepared_cells_dict, file=sys.stderr)
        self.save_handover_params()
        # self.delete_objects()
        # del results
        if self.simulation.sim_params.scenario.max_num_devices_per_scenario < 5:
            self.plot_handovers_and_rlf_on_sim_end()
        # self.sanity_checks(results)

    def save_handover_params(self):
        if "CHO" in self.simulation.sim_params.handover_algorithm:
            results = {'prep_offset': ConditionalHandoverParameters.prep_offset,
                       'exec_offset': ConditionalHandoverParameters.exec_offset,
                       'remove_offset': ConditionalHandoverParameters.remove_offset,
                      'replace_offset': ConditionalHandoverParameters.replace_offset,
                       'with_ttt_exec': ConditionalHandoverParameters.with_ttt_exec,
                       'TTT_exec': HandoverParameters.ttt_exec,
                       'with_ttt_prep': ConditionalHandoverParameters.with_ttt_prep,
                       'TTT_prep': HandoverParameters.ttt_prep,
                       'A_event': ConditionalHandoverParameters.event
                       }
        elif "Normal" in self.simulation.sim_params.handover_algorithm:
            results = {'TTT handover timer': HandoverParameters.ttt_exec,
                        'A3 offset': HandoverParameters.a3_offset,
                        'Qout': HandoverParameters.Qout,
                        'Qin duration': HandoverParameters.Qin_duration,
                        'Qin': HandoverParameters.Qin,
                        'HOF T304 timer': HandoverParameters.handover_hof_t304_timer,
                        'A_event': HandoverParameters.event,
                       }

        filename = 'handover_params_' + self.simulation.sim_params.results_name
        save_results_to_json(results, filename)

    def count_total_num_handovers(self):
        self.drop_empty_lists_from_who_made_handovers_at_TTI()
        for tti in self.who_made_handovers_at_TTI_clean:
            self.total_num_handovers_over_sim += len(self.who_made_handovers_at_TTI_clean[tti])

    def drop_empty_lists_from_who_made_handovers_at_TTI(self):
        for tti in self.simulation.handover.who_made_handovers.keys():
            if len(self.simulation.handover.who_made_handovers[tti]) > 0:
                self.who_made_handovers_at_TTI_clean[tti] = self.simulation.handover.who_made_handovers[tti]

    def collect_sum_throughput(self, user):
        # print(f"User {device.ID} has {device.my_rate} bps", file=sys.stderr)
        self.current_throughput += user.my_rate*self.simulation.sim_params.TTI_duration
        self.sum_throughput_per_user[user.ID] += user.my_rate*self.simulation.sim_params.TTI_duration  # log it too (just in case)

    def collect_num_handovers(self):
        self.current_num_handovers += len(self.simulation.handover.who_made_handovers[self.simulation.TTI])
        if self.simulation.TTI != 0 and self.simulation.TTI % 1000 == 0:  # sum throughput per second is collected
            num_users = len(self.simulation.devices_per_scenario)
            self.num_handovers_per_sec.append(self.current_num_handovers / num_users)
            self.current_num_handovers = 0

    def collect_num_rlfs(self):
        if self.simulation.TTI != 0 and self.simulation.TTI % 1000 == 0 or self.simulation.TTI == self.simulation.sim_params.num_TTI-1:
            num_users = len(self.simulation.devices_per_scenario)
            self.num_rlf_per_sec.append(self.current_rlf)
            self.current_rlf = 0


    def add_to_current_num_rlfs(self):
        self.current_rlf += 1

    def on_sim_end(self):
        self.count_total_num_handovers()

    def plot_handovers_and_rlf_on_sim_end(self):
        if self.simulation.visualization.radius_mean is None:
            self.simulation.visualization.get_radius_coverage_outdoor()
        self.simulation.visualization._plot_gNBs()
        self.simulation.visualization.hexagon_maker.plot_colored_hexagons()
        plot_mobility(self.simulation.mobility.X_mobility, self.simulation.mobility.Y_mobility,
                      len(self.simulation.devices_per_scenario), self.simulation.visualization.user_speed_metrics,
                      self.simulation.sim_params.results_name, with_users=True)
        if len(self.simulation.devices_per_scenario) == 1:
            self.plot_handovers_in_allocation()
            self.plot_rlfs_in_allcation()
            self.plot_first_gnb_connection()
            self.write_num_preparations_of_each_cell()
            plt.savefig(f"results/handovers_{self.simulation.sim_params.results_name}.png", dpi=500)

    def delete_objects(self):
        # del self.ran_simulation.handover  # is used
        del self.simulation.handover_metrics
        # del self.ran_simulation.sim_params  # is used
        del self.simulation.scheduler
        del self.simulation.throughput_calc

    def print_top_gnbs(self, top_num):
        print("SINRs: ", sorted(self.simulation.channel.measured_SINR[0][:top_num], reverse=True))
        print("gNB IDs: ", np.argsort(self.simulation.channel.measured_SINR[0])[::-1][:top_num])

    def plot_handovers_in_allocation(self):
        for TTI, users in self.simulation.handover.who_made_handovers.items():
            TTI_pos = int(TTI / MeasurementParams.update_ue_position_gap)
            for user_id in users:
                x = self.simulation.mobility.X_mobility[user_id][TTI_pos]
                y = self.simulation.mobility.Y_mobility[user_id][TTI_pos]
                plt.scatter(x, y, color='red', s=7, marker=0)
                self.plot_user_gnb_connection(user_id, TTI, [x, y])

    def plot_rlfs_in_allcation(self):
        for x, y in self.simulation.monitor_rlf.rlf_at_position:
            plt.scatter(x, y, color='orange', s=10, marker='x')

    def plot_user_gnb_connection(self, user_id, TTI, user_xy):
        user = self.simulation.devices_per_scenario[user_id]
        my_gnb_id = user.connected_to_gnbs[TTI]
        my_gnb = self.simulation.gNBs_per_scenario[my_gnb_id]
        plt.plot([user_xy[0], my_gnb.x], [user_xy[1], my_gnb.y], color='green', linewidth=0.5, linestyle='dashed')

    def plot_first_gnb_connection(self):
        for user in self.simulation.devices_per_scenario:
            # self.plot_user_gnb_connection(device.ID, 0, [device.x, device.y])
            user = self.simulation.devices_per_scenario[user.ID]
            my_gnb_id = user.connected_to_gnbs[0]
            if my_gnb_id:  # when using traffic models, device might have been inactive
                my_gnb = self.simulation.gNBs_per_scenario[my_gnb_id]
                plt.plot([user.x, my_gnb.x], [user.y, my_gnb.y], color='green', linewidth=0.5, linestyle='dashed')

    def write_num_preparations_of_each_cell(self):
        for gnb_id, count in self.prepared_cells_count_dict.items():
            gnb = self.simulation.gNBs_per_scenario[gnb_id]
            msg = f"p={count}"
            plt.text(gnb.x + 20, gnb.y + 45, msg, color='blue', size=8)

    def sanity_checks(self, results):
        assert self.simulation.sim_params.scenario.transmit_power_macro >= 22, \
            f"Macro Tx Power = {self.simulation.sim_params.scenario.transmit_power_macro}"
        # assert results['count_prepared_cells'] > results['count_released_cells'], \
        #     f"Prepared {results['count_prepared_cells']} gNBs, but released {results['count_released_cells']}"
        # assert results['count_prepared_cells'] > results['count_prepared_but_not_used_cells'], \
        #     f"Prepared {results['count_prepared_cells']} gNBs, " \
        #     f"and among them not used {results['count_prepared_but_not_used_cells']}"