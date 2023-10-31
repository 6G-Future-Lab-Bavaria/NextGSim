# @Author: Alba Jano, Anna Prado
# @Date: 2020-11-15
# @Email: alba.jano@tum.de, anna.prado@tum.de
# @Last modified by: Alba Jano

import numpy as np
import os
from matplotlib import patches
import matplotlib.pyplot as plt
from runtime.data_classes import States, Schedulers


class RadioResourceSchedulers(object):
    def __init__(self, simulation, channel_quality, scheduler_type=None):
        self.simulation_object = simulation
        self.num_users = self.simulation_object.sim_params.scenario.max_num_devices_per_scenario
        self.devices_per_scenario_ID = np.array(range(0, self.num_users))
        self.num_BSs = self.simulation_object.sim_params.num_cells
        self.num_PRBs = self.simulation_object.sim_params.scenario.num_PRBs
        self.scheduler_name = scheduler_type
        self.SINR = channel_quality
        self.RR_assignment = np.zeros((self.num_BSs, self.num_users, self.num_PRBs))
        self.user_throughput = np.zeros(self.num_users)
        self.user_BS = np.zeros(self.num_users)

    def schedule_round_robin(self):
        for BS_index in range(0, self.num_BSs):
            BS_object = self.simulation_object.gNBs_per_scenario[BS_index]
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

    def calc_achieved_throughput(self):
        for user in range(0, self.num_users):
            for BS in range(0, self.num_BSs):
                for PRB in range(0, self.num_PRBs):
                    # TODO: put the correct bandwidth for the device
                    ' 180 kHz bandwidth per device'
                    if self.RR_assignment[BS, user, PRB] == 1:
                        self.user_throughput[user] += 180 * np.log2(1 + self.SINR[BS, user, PRB])
        return self.user_throughput


# Main functions of the scheduler class
# TODO: 1. A function which receives the SINRs ( 3D matrix: Nr. users, Nr. PRBs, Nr. gNBs) for each TTI

# TODO: Alba- check how the BS selection is done in RRC Idle and RRC Inactive state. There should be a mechanism that
#  does not rely in SINRs. If so generate SINR matrix just for connected users - status (information here)
# procedure is complicated- better use the minimum distance

# fixme: Device in RRC Idle (Pass the information to read me after implementation) -done
"""
[https://www.sharetechnote.com/html/5G/5G_CellSelectionCriterion.html]
1. When UE is powered on first time, it select best gNB based on cell selection procedure and sends Registration
Request to initiates the RRC connect setup signalling  toward gNB, and N2 Signaling to AMF. Registration Request
triggers the transition from CM-Idle to CM-Connected. 
[Specified in ETSI TS 138 304 V15.0.0. -> section 5.2.3]
2. If UE is in this state, but not just power on, UE itself  manages mobility based on the network configurations via 
cell (re-) selections. The UE performs the required neighbouring cell measurements which are required for cell (re-) 
selections.
3. On transition from RRC_CONNECTED or RRC_INACTIVE to RRC_IDLE, a UE should camp on a cell as result of cell selection
 according to the frequency be assigned by RRC in the state transition message if any.
 4. When UE is in CM-Idle and it has to send uplink data, UE triggers Service Request NAS message to AMF and changes
CM-Idle state to CM-Connected
"""
# fixme: Device in RRC Inactive (Pass the information to read me after implementation)
"""
1. Mobility is handled through cell reselection, that is, without involvement of the network.
"""


# TODO: 2. Based on the received SINRs, we decide the max SINR for each device for each gNB and select the max SINR
#  between all gNBs. This will define with which gNB the device will be connected, regardless of the state. Here, check
#  the handover, how will behave

# TODO: 3. Create in the beginning round robin and resource fair scheduling based on rrc connected users. How they work:
#  Round Robin: Loop over all users; Loop over all PRBs; assign the selected PRB to the selected device ;
#  Fair scheduling is based on the throughput, that the users should receive similar throughput

# TODO 4: Calculate the throughput with Shannon formula for connected users (function)


class Scheduler:
    def __init__(self, simulation):
        self.channel = simulation.channel
        self.sim_params = simulation.sim_params
        self.simulation = simulation
        self.visualize_scheduler_allocation_flag = False

    def schedule(self, scheduler):
        # schedule and hand over only connected users
        if scheduler == Schedulers.round_robin:
            self.schedule_with_round_robin()
        elif scheduler == Schedulers.dummy:
            self.dummy_scheduler()
        else:
            raise NotImplementedError("Only Round Robin Scheduler is implemented")
        self.visualize_scheduler_allocation(self.simulation.TTI)

    def connect_users_to_gnbs(self):
        for user in self.simulation.devices_per_scenario:
            user.my_gnb.connected_devices.append(user)
            user.state = States.rrc_connected

    def get_num_PRBs(self, gnb_type):
        if self.simulation.sim_params.scenario.scenario == 'Indoor':
            return self.simulation.sim_params.scenario.num_PRBs
        elif gnb_type == 'macro':
            return self.simulation.sim_params.scenario.num_PRBs_macro
        elif gnb_type == 'micro':
            return self.simulation.sim_params.scenario.num_PRBs_micro

    def schedule_with_round_robin(self):
        """
        Each device gets PRBs allocated and his achievable rate is calculated.
        First, users get a quotient integer of PRBs, then remaining PRBs are allocated to users one by one.
        :param TTI:
        :return: Sets my_prbs for every connected device
        """
        # todo: reset my_prbs of non-connected users
        # todo: reserve resources for device in prepared cells; add len(gnb.prepared_cells)
        for user in self.simulation.devices_per_scenario:
            user.my_prbs = []  # reset

        for gnb in self.simulation.gNBs_per_scenario:
            self.simulation.handover.count_resource_reservation_duration(gnb)
            num_connected_users = max(len(gnb.connected_devices), 1)
            # print(f"gNB {gnb.ID} has {len(gnb.connected_devices)} users")
            num_PRBs = gnb.get_available_resources()
            quotient_int = num_PRBs // num_connected_users
            remainder = num_PRBs % num_connected_users
            last_used_prb_id = 0
            for user in gnb.connected_devices:
                if user.state != States.rrc_connected:
                    raise ValueError(f"UE {user.ID} IS NOT CONNECTED")
                # print(f"User id {device.ID}, {device.handover_is_ongoing}, {device.handover_interruption_time}")
                # current_time = self.ran_simulation.TTI * self.ran_simulation.sim_params.TTI_duration
                # if device.hit_finish and device.hit_finish >= current_time:  # this device is making a handover
                #     device.my_prbs = []
                #     continue
                user.my_prbs = list(range(last_used_prb_id, last_used_prb_id + quotient_int))
                last_used_prb_id += quotient_int
                if remainder > 0:
                    user.my_prbs.append(last_used_prb_id)
                    last_used_prb_id += 1
                    remainder -= 1
            assert last_used_prb_id <= num_PRBs, f"Last allocated PRB id {last_used_prb_id}"
        self.check_prbs_assignment()
        # for device in self.ran_simulation.devices_per_scenario:
        #     if len(device.my_prbs) == 0:
        #         print(f"UE {device.ID} was not served at {self.ran_simulation.TTI}")

    def get_shannon_rate(self, sinrs_for_my_prbs):
        # todo: convert SINR to linear
        user_rate = 0
        for sinr in sinrs_for_my_prbs:
            if sinr < 0:
                raise Exception("Log of negative SINR in Shannon rate calculation")
            user_rate += self.simulation.sim_params.PRB_bandwidth_macro * np.log2(1 + sinr)
        return round(user_rate, 1)

    def visualize_scheduler_allocation(self, TTI):
        if not self.visualize_scheduler_allocation_flag:
            return
        counter = 0
        fig = plt.figure(111)
        ax = fig.gca()
        for device in self.simulation.devices_per_scenario:
            if device.state is not States.rrc_connected:  # only connected users were scheduled
                continue
            plt.text(device.ID + 0.01, device.my_gnb.ID + 0.25, f"{len(device.my_prbs)} PRBs", size=7)
            # sinr = self.ran_simulation.channel.measured_SINR[device.ID, device.my_gnb.ID]
            # plt.text(device.ID+0.01, device.my_gnb.ID + 0.5, f"{round(sinr, 1)} dB", size=7)
            # plt.text(device.ID+0.01, device.my_gnb.ID + 0.75, f"{round(device.my_rate,1)} Mbps", size=7)

            if TTI in self.simulation.handover.who_made_handovers and device.ID in \
                    self.simulation.handover.who_made_handovers[TTI]:
                color = 'red'
                label = 'Made handover'
                counter += 1
                # print(f"Plot device {device.ID} handover to gnb {device.my_gnb.ID}")
            else:
                color = '#0099FF'
                label = ''
            rect = patches.Rectangle((device.ID, device.my_gnb.ID,), 1, 1, color=color,
                                     label=label if counter == 0 else "")
            ax.add_patch(rect)
            plt.xticks(range(len(self.simulation.devices_per_scenario)))
            plt.yticks(range(len(self.simulation.gNBs_per_scenario)))
            plt.xlim([0, len(self.simulation.devices_per_scenario) + 0.01])
            plt.ylim([0, len(self.simulation.gNBs_per_scenario) + 0.01])

            ax.set_xlabel("Users")
            ax.set_ylabel("gNBs")
            ax.set_title(f"Allocation of PRBs at TTI={TTI}")
        # fig.legend()
        ax.grid()
        self.check_if_dir_exists()
        fig.savefig(f"results/scheduling/scheduling_{str(TTI).zfill(3)}.png", dpi=600)
        fig.clf()
        ax.cla()

    def check_prbs_assignment(self):
        # print(f"TTI={TTI}")
        for gNB in self.simulation.gNBs_per_scenario:
            num_assigned_prbs_per_gnb = 0
            for user in gNB.connected_devices:
                # print(f"User {device.ID} connected {device.my_gnb.ID} with {len(device.my_prbs)} PRBs")
                num_assigned_prbs_per_gnb += len(user.my_prbs)
            # print(f"At TTI={self.ran_simulation.TTI}, gNB assigned {num_assigned_prbs_per_gnb} out of {gNB.available_resources}")
            assert num_assigned_prbs_per_gnb <= gNB.available_resources, \
                f"gNB assigned {num_assigned_prbs_per_gnb} out of {self.simulation.sim_params.num_PRBs}"

    def check_if_dir_exists(self):
        if self.simulation.TTI == 0 and not os.path.isdir('results/scheduling'):
            os.mkdir('results/scheduling')

    def dummy_scheduler(self):
        for user in self.simulation.devices_per_scenario:  # to reset the rates
            user.my_rate = 0
        for gnb in self.simulation.gNBs_per_scenario:
            self.simulation.handover.count_resource_reservation_duration(gnb)
            for user in gnb.connected_devices:
                if user.state != States.rrc_connected:
                    raise ValueError(f"UE {user.ID} IS NOT CONNECTED")
                assert user.hit_finish is None, f"UE {user.ID}: HIT = {user.hit_finish}"
                if user.my_rate != 0:
                    assert 0, "Why device's rate was not reset?"
                user.my_rate = 20 * 10 ** 6  # 20 Mbps  (minimum required rate in 5G DL)
