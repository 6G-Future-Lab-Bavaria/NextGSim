# @Author: Alba Jano, Anna Prado
# @Date: 2020-11-15
# @Email: alba.jano@tum.de, anna.prado@tum.de
# @Last modified by: Alba Jano
from collections import defaultdict


class HandoverMetrics:
    def __init__(self, simulation):
        self.simulation = simulation
        self.ping_pong_window = 3000  # ms

    def calc_num_ping_pong_handovers_per_user(self, user):
        # Paper: A ran_simulation study on LTE handover and the impact of cell size, 2019
        # Ping-pong handover if after a handover from src to target cell, there is another handover to the
        # original cell, all this happening under a predefined time set to 3 s.
        gnbs = user.connected_to_gnbs
        unique_gnbs = [gnbs[0]]
        # unique_gnbs_ttt = [0]
        gnb_to_time_dict = defaultdict(list)
        for t in range(len(gnbs)):
            if gnbs[t] != unique_gnbs[-1] or t == 0:
                unique_gnbs.append(gnbs[t])
                # unique_gnbs_ttt.append(t)
                gnb_to_time_dict[gnbs[t]].append(t)  # *self.ran_simulation.sim_params.TTI_duration
        num_ping_pong_handovers = 0
        for gnb in gnb_to_time_dict:
            for i in range(len(gnb_to_time_dict[gnb]) - 1):
                if gnb_to_time_dict[gnb][i + 1] - gnb_to_time_dict[gnb][i] <= self.ping_pong_window:
                    num_ping_pong_handovers += 1
        return num_ping_pong_handovers



