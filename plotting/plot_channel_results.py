# @Author:  Anna Prado
# @Date: 2020-11-19
# @Email: anna.prado@tum.de


import numpy as np
import matplotlib.pyplot as plt
from device.Device import Device
from gnb.GnB import GnB
from channel.ChannelModel import ChannelUMiUMa, ChannelIndoor, ChannelUMa
from runtime import RANSimulation
from runtime.data_classes import States
from runtime.Scenarios import Outdoor, Indoor


class PlotChannel:
    def __init__(self):
        self.num_cells = 1
        self.simulation = None

    def create_simulation_object(self, scenario):
        config = {'always_los_flag': False}
        simulation = RANSimulation.RANSimulation(config)
        simulation.sim_params.snr_averaging = False
        simulation.TTI = 0
        gnbs_pos = [[0, 0], [50, 30]]
        users_pos = []
        for i in range(10, 1000, 10):
            users_pos.append([0, i])
        # print(len(users_pos))

        if scenario == 'Indoor':
            users_pos = users_pos[:14]

        for i in range(self.num_cells):
            x = gnbs_pos[i][0]
            y = gnbs_pos[i][1]
            gnb = GnB(ID=i, x=x, y=y, simulation=simulation)
            simulation.gNBs_per_scenario.append(gnb)

        for i in range(len(users_pos)):
            x = users_pos[i][0]
            y = users_pos[i][1]
            user = Device(ID=i, transmit_power=23, x=x, y=y, simulation=simulation)
            user.state = States.rrc_connected
            user.my_gnb = simulation.gNBs_per_scenario[0]
            simulation.devices_per_scenario.append(user)

        return simulation

    def set_umi(self, scenario):
        self.simulation = self.create_simulation_object(scenario)
        self.simulation.sim_params.num_cells = self.num_cells
        channel = ChannelUMiUMa(self.simulation, self.simulation.sim_params)
        self.simulation.sim_params.scenario = Outdoor()
        self.simulation.sim_params.scenario.num_macro_gnbs = 0
        channel.init()
        assert channel.gnb_antenna_height[0][0] == 10, channel.gnb_antenna_height
        assert channel.effective_env_height == 1
        assert channel.ue_antenna_height == 1.5
#         assert channel.center_freq[0][0] in [4, 28], channel.center_freq  # fixme
        assert channel.center_freq_multiplier == 10 ** 9
        colors = ['green', 'red']
        return colors, channel

    def set_uma(self, scenario):
        self.simulation = self.create_simulation_object(scenario)
        self.simulation.sim_params.num_cells = self.num_cells
        channel = ChannelUMa(self.simulation, self.simulation.sim_params)
        self.simulation.sim_params.scenario = Outdoor()
        self.simulation.sim_params.scenario.num_macro_gnbs = 1
        channel.init()
        assert channel.gnb_antenna_height[0][0] == 25, channel.gnb_antenna_height
        assert channel.effective_env_height == 1
        assert channel.ue_antenna_height == 1.5
        assert channel.center_freq[0][0] == 0.5  # fixme
        assert channel.center_freq_multiplier == 10 ** 9
        colors = ['orange', 'pink']
        return colors, channel

    def set_indoor(self, scenario):
        self.simulation = self.create_simulation_object(scenario)
        self.simulation.sim_params.num_cells = self.num_cells
        self.simulation.sim_params.scenario = Indoor()
        channel = ChannelIndoor(self.simulation, self.simulation.sim_params)
        channel.init()
        assert channel.gnb_antenna_height[0][0] == 3
        assert channel.ue_antenna_height == 1
        assert channel.center_freq == 0.5, channel.center_freq  # fixme
        assert channel.center_freq_multiplier == 10 ** 9
        colors = ['blue', 'black']
        return colors, channel

    def plot_pathloss(self):
        for scenario in ['UMa', 'UMi', 'Indoor']:
            if scenario == 'UMi':
                colors, channel = self.set_umi(scenario)
            elif scenario == 'UMa':
               colors, channel = self.set_uma(scenario)
            else:
                colors, channel = self.set_indoor(scenario)
            distance_2d, distance_3d = channel.calc_distance_btw_users_gnbs()
            flag_nlos = np.zeros_like(distance_3d, dtype=bool)
            final_pathloss_nlos = channel.calc_pathloss(distance_3d, flag_nlos)

            los_flag = np.ones_like(distance_3d, dtype=bool)
            final_pathloss_los = channel.calc_pathloss(distance_3d, los_flag)

            plt.scatter(distance_2d, final_pathloss_los, label=f'{scenario} LoS', color=colors[0])
            plt.scatter(distance_2d, final_pathloss_nlos, label=f'{scenario} No LoS', color=colors[1])
        plt.legend()
        plt.grid()
        plt.title("Pathloss", fontsize=15)
        plt.xlabel("2D distance between UE and BS (m)", fontsize=12)
        plt.ylabel("Pathloss (dB)", fontsize=12)
        plt.savefig(f"results/pathloss.png")
        plt.cla()

    def plot_los_probability(self):
        for scenario in ['UMa', 'UMi', 'Indoor']:
            if scenario == 'UMi':
                colors, channel = self.set_umi(scenario)
            elif scenario == 'UMa':
                colors, channel = self.set_uma(scenario)
            else:
                colors, channel = self.set_indoor(scenario)

            distance_2d, distance_3d = channel.calc_distance_btw_users_gnbs()
            los_prob = channel.calc_los_probability(d_2dout=distance_2d)

            plt.scatter(distance_2d, los_prob, label=f'{scenario}', color=colors[0])
        plt.legend()
        plt.grid()
        plt.title("Line of Sight Probability", fontsize=15)
        plt.xlabel("2D distance between UE and BS (m)", fontsize=12)
        plt.ylabel("Line of Sight Probability (dB)", fontsize=12)
        plt.savefig(f"results/los_probability.png")
        print(f"Saved LoS probability plot to plotting/results")
        plt.cla()

    def plot_snr_vs_distance(self, plot_flag=True):
        plot_cell_radius = False
        # The plots work with Python 3.8, but not with 3.7 (require reshaping).
        if plot_flag:
            plt.figure(figsize=(15, 8))  # if commented, hexagons are plotted
        radius_mean = []
        mean_snr_at_radius = []
        std_snr_at_radius = []
        for scenario in ['UMa', 'UMi']:  # 'Indoor'
            if scenario == 'UMi':
                colors, channel = self.set_umi(scenario)
                # print(f"Tx Power for {scenario} is {self.ran_simulation.sim_params.scenario.transmit_power_macro}, "
                #       f"{self.ran_simulation.sim_params.scenario.transmit_power_micro} dBm")
            elif scenario == 'UMa':
                colors, channel = self.set_uma(scenario)
            else:
                colors, channel = self.set_indoor(scenario)
                # print(f"Tx Power for {scenario} is {self.ran_simulation.sim_params.scenario.transmit_power} dBm")
            distance_2d, distance_3d = channel.calc_distance_btw_users_gnbs(next_pos=False)
            sinr_list = []
            rsrp_list = []
            for i in range(100):
                self.simulation.sim_params.with_interference = False
                channel.calculate_final_SINR_RSRP()
                sinr_list.append(channel.measured_SINR)
                rsrp_list.append(channel.measured_RSRP)
            mean_sinr = np.mean(sinr_list, axis=0)
            std_sinr = np.std(sinr_list, axis=0)

            cur_mean = None
            cur_dist = None
            cur_std = None

            for i in range(len(distance_2d)):
                m = mean_sinr[i]
                d = distance_2d[i]
                if i == len(distance_2d) - 1 and cur_mean is None:
                    cur_dist = d
                    cur_mean = m
                    cur_std = std_sinr[i]
                if m <= -8:
                    break
                else:
                    cur_dist = d
                    cur_mean = m
                    cur_std = std_sinr[i]

            mean_snr_at_radius.append(cur_mean[0])
            radius_mean.append(cur_dist[0])
            std_snr_at_radius.append(cur_std[0])
            if plot_flag:
                plt.errorbar(x=distance_2d, y=mean_sinr, yerr=std_sinr, fmt='o', capsize=4, markersize=4,
                             elinewidth=2, markeredgewidth=2, color=colors[0], label=f'{scenario}')
        if plot_flag:
            plt.hlines(y=-8, xmin=0, xmax=distance_2d[-1] + 10, label='RLF failure', color='red')
            if plot_cell_radius:
                plt.vlines(x=radius_mean[0], ymin=-30, ymax=15, label='Micro gNB radius', color='black',
                           linestyles='dashed')  # 125
                plt.vlines(x=radius_mean[1], ymin=-30, ymax=15, label='Macro gNB radius', color='red',
                           linestyles='dashed')  # 288
                plt.text(200, 40, f"R_micro: {radius_mean[1]} m, R_macro: {radius_mean[0]} m")
            print(f"R_micro: {radius_mean[1]} m, R_macro: {radius_mean[0]} m")
            plt.legend()
            plt.title(f"SNR vs. distance (Tx power macro = {self.simulation.sim_params.scenario.transmit_power_macro} dBm, "
                      f"Tx power micro = {self.simulation.sim_params.scenario.transmit_power_micro} dBm)", fontsize=15)
            plt.xlabel("2D distance between UE and BS (m)", fontsize=15)
            plt.ylabel("SNR (dB)", fontsize=15)
            plt.grid()
            plt.xlim([0, 485])
            plt.savefig(f"results/snr_vs_distance.png", dpi=500)
            # print(f"SNR should be [-30; 20] dB according to https://arxiv.org/pdf/1703.08232.pdf")
            plt.cla()
        return mean_snr_at_radius, std_snr_at_radius, radius_mean

    # def plot_los_probability_umi_uma(self):
    #     scenario = 'UMi'
    #     self.ran_simulation = self.create_simulation_object(scenario)
    #     self.ran_simulation.sim_params.num_cells = self.num_cells
    #     channel = ChannelUMi(self.ran_simulation, self.ran_simulation.sim_params, print_flag=False)
    #     self.ran_simulation.sim_params.scenario = UMi()
    #     self.ran_simulation.sim_params.scenario.num_macro_gnbs = 10
    #     channel.init()
    #
    #     distance_2d, distance_3d = channel.calc_distance_btw_users_gnbs()
    #     los_probability_umi, los_probability_uma, los_probability = channel.calc_los_probability(d_2dout=distance_2d)
    #
    #     plt.scatter(distance_2d, los_probability, label=f'Final', color='black', s=15)
    #     plt.plot(distance_2d, los_probability_umi, label=f'UMi', color='green')
    #     plt.plot(distance_2d, los_probability_uma, label=f'UMa', color='blue')
    #     plt.legend()
    #     plt.title("Line of Sight Probability", fontsize=15)
    #     plt.xlabel("2D distance between UE and BS (m)", fontsize=12)
    #     plt.ylabel("Line of Sight Probability (dB)", fontsize=12)
    #     plt.savefig(f"los_probability_umi_uma.png")
    #     plt.cla()


if __name__ == "__main__":
    test = PlotChannel()
    test.plot_pathloss()
    test.plot_los_probability()
    mean_snr_at_radius, std_snr_at_radius, radius_mean = test.plot_snr_vs_distance()
    print(mean_snr_at_radius, radius_mean)
