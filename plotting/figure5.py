import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
# from runtime.SimulationParameters import SimulationParameters
import seaborn

from definitions import RESULTS_DIR

seaborn.set(style="ticks")


class Fig5Plot:
    def __init__(self):
        res_dir = RESULTS_DIR + "reproduction/"
        self.num_of_users = [50, 100, 150, 200, 250, 300]
        self.radio_scheduling_algo = ["Proportional_Fair", "Max_Rate", "Round_Robin"]
        self.edge_scheduling = ["Radio-Aware", "FCFS"]
        self.seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        self.max_rate_radio_aware_files = {}
        self.max_rate_non_radio_aware_files = {}
        self.round_robin_radio_aware_files = {}
        self.round_robin_non_radio_aware_files = {}
        self.proportional_fair_radio_aware_files = {}
        self.proportional_fair_non_radio_aware_files = {}

        for num_user in self.num_of_users:
            self.max_rate_radio_aware_files[num_user] = []
            self.max_rate_non_radio_aware_files[num_user] = []
            self.round_robin_radio_aware_files[num_user] = []
            self.round_robin_non_radio_aware_files[num_user] = []
            self.proportional_fair_radio_aware_files[num_user] = []
            self.proportional_fair_non_radio_aware_files[num_user] = []

        for i in self.num_of_users:
            for j in self.radio_scheduling_algo:
                for k in self.edge_scheduling:
                    for l in self.seeds:
                        if j == "Proportional_Fair":
                            if k == "Radio-Aware":
                                self.proportional_fair_radio_aware_files[i].append(
                                    res_dir +
                                    str(i) + '_' + str(j) + '_' + str(k) + '_' + str(l) + '.csv')
                            else:
                                self.proportional_fair_non_radio_aware_files[i].append(
                                    res_dir +
                                    str(i) + '_' + str(j) + '_' + str(k) + '_' + str(l) + '.csv')

                        if j == "Max_Rate":
                            if k == "Radio-Aware":
                                self.max_rate_radio_aware_files[i].append(
                                    res_dir +
                                    str(i) + '_' + str(j) + '_' + str(k) + '_' + str(l) + '.csv')
                            else:
                                self.max_rate_non_radio_aware_files[i].append(
                                    res_dir +
                                    str(i) + '_' + str(j) + '_' + str(k) + '_' + str(l) + '.csv')

                        if j == "Round_Robin":
                            if k == "Radio-Aware":
                                self.round_robin_radio_aware_files[i].append(
                                    res_dir +
                                    str(i) + '_' + str(j) + '_' + str(k) + '_' + str(l) + '.csv')
                            else:
                                self.round_robin_non_radio_aware_files[i].append(
                                    res_dir +
                                    str(i) + '_' + str(j) + '_' + str(k) + '_' + str(l) + '.csv')

    def plot_graph(self):
        desired_latency = 100
        fontsize = 36
        task_completion_rates = []

        pf_radio_aware_completion_rate = {}
        pf_radio_aware_completion_rate_avg = {}
        pf_non_radio_aware_completion_rate = {}
        pf_non_radio_aware_completion_rate_avg = {}
        mr_radio_aware_completion_rate = {}
        mr_radio_aware_completion_rate_avg = {}
        mr_non_radio_aware_completion_rate = {}
        mr_non_radio_aware_completion_rate_avg = {}
        rr_radio_aware_completion_rate = {}
        rr_radio_aware_completion_rate_avg = {}
        rr_non_radio_aware_completion_rate = {}
        rr_non_radio_aware_completion_rate_avg = {}

        for num_user in self.num_of_users:
            mr_radio_aware_completion_rate[num_user] = []
            mr_radio_aware_completion_rate_avg[num_user] = []
            mr_non_radio_aware_completion_rate[num_user] = []
            mr_non_radio_aware_completion_rate_avg[num_user] = []
            rr_radio_aware_completion_rate[num_user] = []
            rr_radio_aware_completion_rate_avg[num_user] = []
            rr_non_radio_aware_completion_rate[num_user] = []
            rr_non_radio_aware_completion_rate_avg[num_user] = []
            pf_radio_aware_completion_rate[num_user] = []
            pf_radio_aware_completion_rate_avg[num_user] = []
            pf_non_radio_aware_completion_rate[num_user] = []
            pf_non_radio_aware_completion_rate_avg[num_user] = []

        for num_user in self.num_of_users:
            num_of_packets = 999 * num_user
            for file in self.max_rate_radio_aware_files[num_user]:
                print(self.max_rate_radio_aware_files)
                data = pd.read_csv(file)
                mr_radio_aware_completion_rate[num_user].append(
                    len(data[data["Total Latency"] < desired_latency]) / num_of_packets)
            for file in self.max_rate_non_radio_aware_files[num_user]:
                data = pd.read_csv(file)
                mr_non_radio_aware_completion_rate[num_user].append(
                    len(data[data["Total Latency"] < desired_latency]) / num_of_packets)
            for file in self.proportional_fair_radio_aware_files[num_user]:
                data = pd.read_csv(file)
                pf_radio_aware_completion_rate[num_user].append(
                    len(data[data["Total Latency"] < desired_latency]) / num_of_packets)
            for file in self.proportional_fair_non_radio_aware_files[num_user]:
                data = pd.read_csv(file)
                pf_non_radio_aware_completion_rate[num_user].append(
                    len(data[data["Total Latency"] < desired_latency]) / num_of_packets)
            for file in self.round_robin_radio_aware_files[num_user]:
                data = pd.read_csv(file)
                rr_radio_aware_completion_rate[num_user].append(
                    len(data[data["Total Latency"] < desired_latency]) / num_of_packets)
            for file in self.round_robin_non_radio_aware_files[num_user]:
                data = pd.read_csv(file)
                rr_non_radio_aware_completion_rate[num_user].append(
                    len(data[data["Total Latency"] < desired_latency]) / num_of_packets)

            mr_radio_aware_completion_rate_avg[num_user] = np.mean(mr_radio_aware_completion_rate[num_user])
            pf_radio_aware_completion_rate_avg[num_user] = np.mean(pf_radio_aware_completion_rate[num_user])
            rr_radio_aware_completion_rate_avg[num_user] = np.mean(rr_radio_aware_completion_rate[num_user])
            mr_non_radio_aware_completion_rate_avg[num_user] = np.mean(mr_non_radio_aware_completion_rate[num_user])
            pf_non_radio_aware_completion_rate_avg[num_user] = np.mean(pf_non_radio_aware_completion_rate[num_user])
            rr_non_radio_aware_completion_rate_avg[num_user] = np.mean(rr_non_radio_aware_completion_rate[num_user])

        data_group_1 = [mr_radio_aware_completion_rate[50], mr_radio_aware_completion_rate[100],
                        mr_radio_aware_completion_rate[150], mr_radio_aware_completion_rate[200],
                        mr_radio_aware_completion_rate[250], mr_radio_aware_completion_rate[300]]

        data_group_2 = [mr_non_radio_aware_completion_rate[50], mr_non_radio_aware_completion_rate[100],
                        mr_non_radio_aware_completion_rate[150], mr_non_radio_aware_completion_rate[200],
                        mr_non_radio_aware_completion_rate[250], mr_non_radio_aware_completion_rate[300]]

        data_group_3 = [pf_radio_aware_completion_rate[50], pf_radio_aware_completion_rate[100],
                        pf_radio_aware_completion_rate[150], pf_radio_aware_completion_rate[200],
                        pf_radio_aware_completion_rate[250], pf_radio_aware_completion_rate[300]]

        data_group_4 = [pf_non_radio_aware_completion_rate[50], pf_non_radio_aware_completion_rate[100],
                        pf_non_radio_aware_completion_rate[150], pf_non_radio_aware_completion_rate[200],
                        pf_non_radio_aware_completion_rate[250], pf_non_radio_aware_completion_rate[300]]

        data_group_5 = [rr_radio_aware_completion_rate[50], rr_radio_aware_completion_rate[100],
                        rr_radio_aware_completion_rate[150], rr_radio_aware_completion_rate[200],
                        rr_radio_aware_completion_rate[250], rr_radio_aware_completion_rate[300]]

        data_group_6 = [rr_non_radio_aware_completion_rate[50], rr_non_radio_aware_completion_rate[100],
                        rr_non_radio_aware_completion_rate[150], rr_non_radio_aware_completion_rate[200],
                        rr_non_radio_aware_completion_rate[250], rr_non_radio_aware_completion_rate[300]]

        data_groups = [data_group_1, data_group_2, data_group_3, data_group_4, data_group_5, data_group_6]

        # # --- Labels for your data:
        x_values = ['50', '100', '150', "200", "250", "300"]
        width = 5 / len(x_values)
        xlocations = [x * ((1 + len(data_groups)) * width) for x in range(len(data_group_1))]
        colors = ["blue", "lightblue", "green", "lightgreen", "red", "pink"]
        symbol = 'r+'
        ymin = min([val for dg in data_groups for data in dg for val in data])
        ymax = max([val for dg in data_groups for data in dg for val in data]) + 0.1

        plt.rcParams['text.usetex'] = True
        plt.rcParams.update({'font.size': fontsize})
        ax = plt.gca()
        ax.set_ylim(ymin, ymax)

        ax.grid(True, linestyle='dotted')
        ax.set_axisbelow(True)

        plt.xlabel('Number of Users', fontsize=fontsize)
        plt.ylabel('On-Time Completion Rate of Tasks', fontsize=fontsize)

        space = len(data_groups) / 2
        offset = len(data_groups) / 2

        labels = ["MR-RASQ", "MR-FCFS", "PF-RASQ", "PF-FCFS", "RR-RASQ", "RR-FCFS"]

        # --- Offset the positions per group:

        group_positions = []
        box_plots = []
        for num, dg in enumerate(data_groups):
            _off = (0 - space + (0.5 + num))
            print(_off)
            group_positions.append([x + _off * (width + 0.01) for x in xlocations])

        for dg, pos, c, lab in zip(data_groups, group_positions, colors, labels):
            X = []
            Y = []
            bp = ax.boxplot(dg,
                            sym=symbol,
                            labels=[''] * len(x_values),
                            #            labels=x_values,
                            positions=pos,
                            widths=width,
                            boxprops=dict(facecolor=c),
                            medianprops=dict(color='grey'),
                            patch_artist=True,
                            showfliers=False)

            box_plots.append(bp)
            for m in bp['medians']:
                [[x0, x1], [y0, y1]] = m.get_data()
                X.append(np.mean((x0, x1)))
                Y.append(np.mean((y0, y1)))

            plt.plot(X, Y, color=c)

        ax.legend([element["boxes"][0] for element in box_plots],
                  [labels[idx] for idx, _ in enumerate(data_groups)], bbox_to_anchor=(0.5, 1.08),
                  fontsize=fontsize - 10, ncol=3, loc='center')

        fig = plt.gcf()
        fig.set_size_inches(18, 10)
        plt.xlabel("Number of Users")
        plt.ylabel("On-Time Completion Rate of Tasks")
        fig = plt.gcf()
        fig.set_size_inches(18, 10)
        plt.show()


Fig5Plot().plot_graph()
