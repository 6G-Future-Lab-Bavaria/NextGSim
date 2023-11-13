import numpy as np

""" Important references:
1. Fairness Aware Downlink Scheduling Algorithm for LTE Networks. 
2. An Evaluation of the Proportional Fair Scheduler in a Physically Deployed LTE-A Network:
 https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9118081
3.  alpha = 0, beta = 1 maximum fairness scheduler
    alpha = 1, beta = 0 maximum rate scheduler
    alpha = 1, beta = 1 proportional scheduler
"""


class RadioResourceSchedulers(object):
    def __init__(self, simulation, channel_quality=None, scheduler_type=None):
        self.sim = simulation
        self.num_users = self.sim.sim_params.scenario.max_num_devices_per_scenario
        self.devices_per_scenario_ID = np.array(range(0, self.num_users))
        self.num_BSs = self.sim.sim_params.num_cells
        self.num_PRBs = self.sim.sim_params.scenario.num_PRBs
        self.scheduler_name = scheduler_type
        self.SINR = channel_quality
        self.RR_assignment = np.zeros((self.num_BSs, self.num_users, self.num_PRBs))
        self.user_throughput = np.zeros(self.num_users)
        self.user_PRB_throughput = np.zeros((self.num_users, self.num_PRBs))
        self.user_BS = np.zeros(self.num_users)
        if scheduler_type == 'Proportional_Fair':
            self.alpha = 1
            self.beta = 1
        elif scheduler_type == 'Max_Rate':
            self.alpha = 1
            self.beta = 0

    def schedule_round_robin(self):
        for BS_index in range(0, self.num_BSs):
            BS_object = self.sim.gNBs_per_scenario[BS_index]
            connected_devices = BS_object.connected_devices
            for user_object in connected_devices:
                self.user_BS[user_object.ID] = BS_index
            if len(connected_devices) > 0:
                for PRB in range(0, self.num_PRBs):
                    self.RR_assignment[BS_index, connected_devices[0].ID, PRB] = 1
                    connected_devices = np.roll(connected_devices, -1)
                    # self.RR_assignment[BS_index, self.devices_per_scenario_ID[0], PRB] = 1
                    # self.devices_per_scenario_ID = np.roll(self.devices_per_scenario_ID, -1)
        # print(self.RR_assignment)
        return self.RR_assignment, self.user_BS

    def schedule_random(self):
        for BS_index in range(0, self.num_BSs):
            BS_object = self.sim.gNBs_per_scenario[BS_index]
            connected_devices = BS_object.connected_devices
            connected_devices_ID = [device.ID for device in connected_devices]
            for user_object in connected_devices:
                self.user_BS[user_object.ID] = BS_index
            if len(connected_devices) > 0:
                for PRB in range(0, self.num_PRBs):
                    selected_device = np.random.choice(connected_devices_ID)
                    self.RR_assignment[BS_index, selected_device, PRB] = 1
        return self.RR_assignment, self.user_BS

    def schedule_proportional_fair(self, history):
        connected_devices_ID =[]
        for BS_index in range(0, self.num_BSs):
            BS_object = self.sim.gNBs_per_scenario[BS_index]
            connected_devices = BS_object.connected_devices
            connected_devices_ID = [device.ID for device in connected_devices]
            inst_data_rate = np.zeros((self.num_users, self.num_PRBs))
            score = np.zeros((self.num_users, self.num_PRBs))
            for user_object in connected_devices:
                self.user_BS[user_object.ID] = BS_index
            if len(connected_devices) > 0:
                for PRB in range(0, self.num_PRBs):
                    for user in connected_devices_ID:
                        inst_data_rate[user, PRB] = 180 * np.log2(1 + 10**(self.SINR[BS_index, user, PRB]/10))
                        score[user, PRB] = (inst_data_rate[user, PRB])**self.alpha/(history[user])**self.beta
                    selected_device = np.argmax(score[:, PRB])
                    self.RR_assignment[BS_index, selected_device, PRB] = 1
        return self.RR_assignment, self.user_BS

    def calc_achieved_throughput(self):
        for user in range(0, self.num_users):
            for BS in range(0, self.num_BSs):
                for PRB in range(0, self.num_PRBs):
                    ' 180 kHz bandwidth per user'
                    if self.RR_assignment[BS, user, PRB] == 1:
                        self.user_PRB_throughput[user, PRB] = 180 * np.log2(1 + 10**(self.SINR[BS, user, PRB]/10))
                        self.user_throughput[user] += self.user_PRB_throughput [user, PRB]
        return self.user_PRB_throughput, self.user_throughput
