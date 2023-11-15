import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from runtime.SimulationParameters import SimulationParameters
import seaborn
import tikzplotlib

from definitions import RESULTS_DIR

seaborn.set(style="ticks")

sim_params = SimulationParameters()


class Figure6:
    def __init__(self):
        self.num_of_instances = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        self.num_users = [50]
        self.edge_scheduling = ["Radio-Aware", "FCFS"]
        # self.seeds = [1]
        self.seeds = [1, 2, 3, 4, 5]
        self.radio_scheduling = ["Round_Robin"]

        self.rr_radio_aware_files = {}
        self.rr_none_files = {}
        self.rr_radio_aware_completion_rate = {}
        self.rr_radio_aware_completion_rate_avg = {}
        self.rr_none_completion_rate = {}
        self.rr_none_completion_rate_avg = {}

        self.results_dir = RESULTS_DIR + "reproduction/figure6/"

        for num_user in self.num_users:
            self.rr_radio_aware_files[num_user] = {}
            self.rr_none_files[num_user] = {}
            for num_instance in self.num_of_instances:
                self.rr_radio_aware_files[num_user][num_instance] = []
                self.rr_none_files[num_user][num_instance] = []

        for num_user in self.num_users:
            for i in self.radio_scheduling:
                for j in self.edge_scheduling:
                    for k in self.num_of_instances:
                        for l in self.seeds:
                            if i == "Round_Robin":
                                if j == "Radio-Aware":
                                    self.rr_radio_aware_files[num_user][k].append(
                                        self.results_dir + str(num_user) + '_' +
                                        str(i) + '_' + str(j) + '_' + str(k) + '_' + str(l) + '.csv')
                                else:
                                    self.rr_none_files[num_user][k].append(
                                        self.results_dir + str(num_user)
                                        + '_' + str(i) + '_' + str(j) + '_' + str(k) + '_' + str(l) + '.csv')

    def plot_graph(self):
        desired_latency = 100
        fontsize = 36
        for num_user in self.num_users:
            self.rr_radio_aware_completion_rate[num_user] = {}
            self.rr_none_completion_rate[num_user] = {}
            for num_instance in self.num_of_instances:
                self.rr_radio_aware_completion_rate[num_user][num_instance] = []
                self.rr_none_completion_rate[num_user][num_instance] = []

        for num_user in self.num_users:
            for num_instance in self.num_of_instances:
                num_of_packets = 999 * num_user
                for file in self.rr_radio_aware_files[num_user][num_instance]:
                    data = pd.read_csv(file)
                    self.rr_radio_aware_completion_rate[num_user][num_instance].append(
                        len(data[data["Total Latency"] < desired_latency]) / num_of_packets)
                for file in self.rr_none_files[num_user][num_instance]:
                    data = pd.read_csv(file)
                    self.rr_none_completion_rate[num_user][num_instance].append(
                        len(data[data["Total Latency"] < desired_latency]) / num_of_packets)

            for num_user in self.num_users:
                self.rr_none_completion_rate_avg[num_user] = {}
                self.rr_radio_aware_completion_rate_avg[num_user] = {}
                for num_instance in self.num_of_instances:
                    self.rr_none_completion_rate_avg[num_user][num_instance] = np.mean(
                        self.rr_none_completion_rate[num_user][num_instance])
                    self.rr_radio_aware_completion_rate_avg[num_user][num_instance] = np.mean(
                        self.rr_radio_aware_completion_rate[num_user][num_instance])

        data_group_1 = [self.rr_radio_aware_completion_rate[50][5], self.rr_radio_aware_completion_rate[50][6],
                        self.rr_radio_aware_completion_rate[50][7], self.rr_radio_aware_completion_rate[50][8],
                        self.rr_radio_aware_completion_rate[50][9], self.rr_radio_aware_completion_rate[50][10],
                        self.rr_radio_aware_completion_rate[50][11],
                        self.rr_radio_aware_completion_rate[50][12], self.rr_radio_aware_completion_rate[50][13],
                        self.rr_radio_aware_completion_rate[50][14], self.rr_radio_aware_completion_rate[50][15]]
        #
        data_group_2 = [self.rr_none_completion_rate[50][5], self.rr_none_completion_rate[50][6],
                        self.rr_none_completion_rate[50][7], self.rr_none_completion_rate[50][8],
                        self.rr_none_completion_rate[50][9],
                        self.rr_none_completion_rate[50][10], self.rr_none_completion_rate[50][11],
                        self.rr_none_completion_rate[50][12], self.rr_none_completion_rate[50][13],
                        self.rr_none_completion_rate[50][14], self.rr_none_completion_rate[50][15]]

        data_group_3 = [self.rr_radio_aware_completion_rate[150][5], self.rr_radio_aware_completion_rate[150][6],
                        self.rr_radio_aware_completion_rate[150][7], self.rr_radio_aware_completion_rate[150][8],
                        self.rr_radio_aware_completion_rate[150][9], self.rr_radio_aware_completion_rate[150][10],
                        self.rr_radio_aware_completion_rate[150][11],
                        self.rr_radio_aware_completion_rate[150][12], self.rr_radio_aware_completion_rate[150][13],
                        self.rr_radio_aware_completion_rate[150][14], self.rr_radio_aware_completion_rate[150][15]]

        data_group_4 = [self.rr_none_completion_rate[150][5], self.rr_none_completion_rate[150][6],
                        self.rr_none_completion_rate[150][7], self.rr_none_completion_rate[150][8],
                        self.rr_none_completion_rate[150][9],
                        self.rr_none_completion_rate[150][10], self.rr_none_completion_rate[150][11],
                        self.rr_none_completion_rate[150][12], self.rr_none_completion_rate[150][13],
                        self.rr_none_completion_rate[150][14], self.rr_none_completion_rate[150][15]]

        data_groups = [data_group_1, data_group_2, data_group_3, data_group_4]

        # --- Labels for your data:
        x_values = ["5", "6", "7", "8", "9", '10', '11', '12', "13", "14", "15"]
        width = 5 / len(x_values)
        xlocations = [x * ((1 + len(data_groups)) * width) for x in range(len(data_group_1))]
        colors = ['red', 'pink', 'green', 'lightgreen']
        symbol = 'r+'
        ymin = min([val for dg in data_groups for data in dg for val in data])
        ymax = max([val for dg in data_groups for data in dg for val in data]) + 0.1

        plt.rcParams['text.usetex'] = True
        plt.rcParams.update({'font.size': fontsize})
        ax = plt.gca()
        ax.set_ylim(ymin, ymax)

        ax.grid(True, linestyle='dotted')
        ax.set_axisbelow(True)

        plt.xlabel('Number of Instances', fontsize=fontsize)
        plt.ylabel('On-Time Completion Rate of Tasks', fontsize=fontsize)

        space = len(data_groups) / 2
        offset = len(data_groups) / 2
        labels = ["RR-RASQ-50", "RR-FCFS-50", "RR-RASQ-150", "RR-FCFS-150"]

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
                            #             capprops=dict(color=c),
                            #            whiskerprops=dict(color=c),
                            #            flierprops=dict(color=c, markeredgecolor=c),
                            medianprops=dict(color='grey'),
                            #           notch=False,
                            #           vert=True,
                            #           whis=1.5,
                            #           bootstrap=None,
                            #           usermedians=None,
                            #           conf_intervals=None,
                            patch_artist=True,
                            showfliers=False)

            box_plots.append(bp)
            for m in bp['medians']:
                [[x0, x1], [y0, y1]] = m.get_data()
                X.append(np.mean((x0, x1)))
                Y.append(np.mean((y0, y1)))

            plt.plot(X, Y, color=c)

        ax.legend([element["boxes"][0] for element in box_plots],
                  [labels[idx] for idx, _ in enumerate(data_groups)], fontsize=fontsize - 10, loc='upper center',
                  ncol=2,
                  bbox_to_anchor=(0.5, 1.175))

        ax.set_xticks(xlocations)
        ax.set_xticklabels(x_values, rotation=0, fontsize=fontsize)
        ax.set_ylim(ymin=0, ymax=1)
        ax.margins(x=0)
        # ax.set_xlim(xmin=0, xmax=15)
        # ax.set_xlim(left=0)
        ax.tick_params(axis='both', which='major', labelsize=fontsize)
        plt.rc('ytick', labelsize=fontsize)
        fig = plt.gcf()
        fig.set_size_inches(18, 10)
        # tikzplotlib.save("completion_rate_vs_num_of_instances_boxplot_rectangle.tex")
        # fig.savefig('completion_rate_vs_num_of_instances_boxplot_rectangle.pdf', format='pdf', dpi=800)
        plt.show()


Figure6().plot_graph()
