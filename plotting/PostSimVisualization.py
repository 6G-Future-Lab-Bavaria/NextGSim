import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from copy import deepcopy
from runtime.utilities import check_if_directory_with_results_exists
from runtime.data_classes import MeasurementParams


class PostSimVisualization:
    def __init__(self, simulation):
        self.simulation = simulation
        self.sinr_at_TTI = {}
        self.measured_rsrp_at_TTI = {}

    def store_snr_and_rsrp(self):
        if self.simulation.sim_params.plot_snr_per_TTI:
            self.sinr_at_TTI[self.simulation.TTI] = deepcopy(self.simulation.channel.average_SINR)
            # self.measured_rsrp_at_TTI[self.ran_simulation.TTI] = deepcopy(self.ran_simulation.channel.average_RSRP)

    def plot_gnb_id(self, user):
        # very slow
        check_if_directory_with_results_exists('sinr')
        plt.cla()
        for tti, gnb_id in enumerate(user.connected_to_gnbs):
            plt.scatter(tti, gnb_id)
        plt.xlabel("TTI")
        plt.ylabel("serving gNB")
        plt.title("Serving gNBs")
        plt.grid()
        plt.savefig('results/sinr/connected_gnb.png', dpi=200)

    def plot_user_sinrs(self, user):
        check_if_directory_with_results_exists('sinr')
        plt.cla()
        plt.figure(figsize=(15, 5))
        for sinr_at_TTI, name in zip([self.sinr_at_TTI], ['Average', 'Measured', ]):  # self.real_sinr_at_TTI,
            # plt.cla()
            total_colors = ['grey', 'orange', 'black', 'red', 'pink'] * (len(self.simulation.gNBs_per_scenario) // 4)
            sinr_at_gnb_dict = defaultdict(list)
            for tti in sinr_at_TTI:
                for gnb in self.simulation.gNBs_per_scenario:
                    sinr = sinr_at_TTI[tti][user.ID, gnb.ID]
                    sinr_at_gnb_dict[gnb.ID].append(sinr)
            for gnb_id, sinrs in sinr_at_gnb_dict.items():
                my_gnb_id = user.connected_to_gnbs[self.simulation.TTI]
                cur_gnb = [gnb_id] * len(sinrs)
                my_gnb = np.array(sinrs)
                cur_gnb = np.array(cur_gnb)
                res = np.equal(my_gnb, cur_gnb)
                colors = ['green' if x == 1 else 'blue' for x in res]
                if name == 'Real':
                    linestyle = 'solid'
                else:
                    linestyle = 'dashed'
                # if np.mean(sinrs) > - 10:  # to plot only the best gNBs
                plt.scatter(range(len(sinrs)), sinrs, color='black', s=8)
                plt.plot(range(len(sinrs)), sinrs, color=total_colors[gnb_id], label=f'gNB {gnb_id}',
                             linestyle=linestyle)
                    # plt.xticks(range(0, len(sinrs), 10))
                # self.plot_handovers_at_snr(device, np.mean(sinrs))
            ue_id = self.simulation.sim_params.user_id
            plt.title(f"{name} SINR of UE {ue_id} over time. Green lines are handovers")
            plt.xlabel(f"MR (1 MR is {MeasurementParams.channel_measurement_periodicity} ms)")
            plt.ylabel("SINR")
            plt.legend()
            plt.grid()
            name += ("_" + self.simulation.sim_params.handover_algorithm)
            plt.savefig(f"results/sinr/{name.lower()}_sinr_user{ue_id}.png", dpi=200)

    def plot_user_rsrp(self, user):
        check_if_directory_with_results_exists('rsrp')
        plt.cla()
        # plt.cla()
        total_colors = ['grey', 'orange', 'black', 'red', 'pink'] * 5
        rsrp_at_gnb_dict = defaultdict(list)
        for tti in self.measured_rsrp_at_TTI:
            for gnb in self.simulation.gNBs_per_scenario:
                rsrp = np.mean(self.measured_rsrp_at_TTI[tti][user.ID, :, gnb.ID])
                rsrp_at_gnb_dict[gnb.ID].append(rsrp)
        for gnb_id, rsrps in rsrp_at_gnb_dict.items():
            my_gnb = self.user_to_gnbs_dict[user.ID]  # use device.connected_to_gnb
            cur_gnb = [gnb_id] * len(rsrps)
            my_gnb = np.array(my_gnb)
            cur_gnb = np.array(cur_gnb)
            res = np.equal(my_gnb, cur_gnb)
            colors = ['green' if x == 1 else 'blue' for x in res]
            plt.scatter(range(len(rsrps)), rsrps, color=colors)
            plt.plot(range(len(rsrps)), rsrps, color=total_colors[gnb_id], label=f'gNB {gnb_id}')
            self.plot_handovers_at_snr(user, np.mean(rsrps))
        plt.title(f"RSRP of UE {user.ID} over time. Serving gNB in green, others in blue")
        plt.xlabel(f"TTIs")
        plt.ylabel("RSRP")
        plt.legend()  # todo: fixme: so that only once
        plt.grid()
        plt.savefig(f"results/rsrp/rsrp_user{user.ID}_rsrp_over_time.png", dpi=200)

    def plot_handovers_at_snr(self, user, mean):
        for TTI, users in self.simulation.handover.who_made_handovers.items():
            if user.ID in users:
                plt.vlines(x=TTI / MeasurementParams.channel_measurement_periodicity, ymin=-20, ymax=30,
                           linestyles='dashed', color='green')
