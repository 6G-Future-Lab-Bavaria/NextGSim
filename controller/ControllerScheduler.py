# @Author: Polina Kutsevol
# @Date: 2021-04-12
# @Email: kutsevol.pn@phystech.edu
# @Last modified by: Polina Kutsevol

import numpy as np
from runtime.data_classes import States


class ControllerScheduler(object):
    def __init__(self, simulation):
        self.sim_params = simulation.sim_params
        self.simulation = simulation
        self.prob_of_lost_msg = np.zeros(self.sim_params.num_controllers)
        self.sum_PRBs = np.zeros(self.sim_params.num_controllers)
        self.scheduling_periodicity = 10

    def init_scheduler(self):
        raise NotImplementedError("init_scheduler is not implemented for base ControllerScheduler class")

    def update_info(self):
        raise NotImplementedError("update_info is not implemented for base ControllerScheduler class")

    def schedule(self):
        raise NotImplementedError("schedule is not implemented for base ControllerScheduler class")


class MaxSNRSliceScheduler(ControllerScheduler):
    def __init__(self, simulation):
        super().__init__(simulation)
        self.SINRs = [[] for _ in range(simulation.sim_params.num_controllers)]
        self.queued_data = [[] for _ in range(simulation.sim_params.num_controllers)]
        self.users = [[] for _ in range(simulation.sim_params.num_controllers)]

    def init_scheduler(self, error_prob):
        for i in range(len(self.simulation.controllers_per_scenario)):
            self.prob_of_lost_msg[i] = error_prob

    def update_info(self):
        np.random.seed(self.simulation.seed)
        for i in range(len(self.simulation.controllers_per_scenario)):
            p = np.random.random()
            if p <= 1 - self.prob_of_lost_msg[i]:
                self.SINRs[i] = []
                self.queued_data[i] = []
                self.users[i] = []
                for gnb in self.simulation.controllers_per_scenario[i].gnbs:
                    for user in gnb.connected_devices:
                        self.SINRs[i].append(self.simulation.channel.measured_SINR[user.ID, user.my_gnb.ID])
                        self.queued_data[i].append(user.get_buffer_stats())
                        self.users[i].append(user)
        self.sum_PRBs = np.zeros(self.sim_params.num_controllers, dtype=int)

        for i in range(len(self.simulation.controllers_per_scenario)):
            self.sum_PRBs[i] = self.simulation.controllers_per_scenario[i].available_resources



    def schedule(self):
        for i in range(len(self.simulation.controllers_per_scenario)):
            device_order = np.flip(np.argsort(self.SINRs[i]))
            available_PRBs = self.sum_PRBs[i]
            full_PRBs = np.zeros(len(self.SINRs[i]))
            for gnb in self.simulation.controllers_per_scenario[i].gnbs:
                gnb.set_zero_available_resources()
            for ID in device_order:
                if self.users[i][ID].state == States.rrc_connected:
                    n_PRBs, flag = self.calculate_PRBs(self.users[i][ID],
                                                   self.queued_data[i][ID], self.SINRs[i][ID])
                    full_PRBs[ID] = flag
                    available_PRBs -= n_PRBs
                    if available_PRBs >= 0:
                        self.users[i][ID].my_gnb.add_available_resources(n_PRBs)
                    else:
                        self.users[i][ID].my_gnb.add_available_resources(n_PRBs + available_PRBs)
                        available_PRBs = 0
                        break
            if available_PRBs > 0:
                for ID in device_order:
                    if available_PRBs == 0:
                        break
                    if self.users[i][ID].state == States.rrc_connected and full_PRBs[ID] != 0:
                        self.users[i][ID].my_gnb.add_available_resources(1)
                        available_PRBs -= 1
                    if available_PRBs == 0:
                        break
            while available_PRBs > 0 and len(device_order):
                for ID in device_order:
                    if available_PRBs == 0:
                        break
                    self.users[i][ID].my_gnb.add_available_resources(1)
                    available_PRBs -= 1
                    if available_PRBs == 0:
                        break

    def calculate_PRBs(self, user, buffer_size, sinr):
        data_per_PRB = self.simulation.throughput_calc.calc_data_rate_per_prb(user, sinr)
        return int(buffer_size * self.simulation.traffic_generator.packet_size()) // int(data_per_PRB), \
               int(buffer_size * self.simulation.traffic_generator.packet_size()) % int(data_per_PRB)

    def perform(self):
        self.update_info()
        self.schedule()