import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pylab
from collections import Counter, defaultdict
from runtime.utilities import get_all_files

rotation = 90  # 90
dpi = 300
fontsize = 10  # xticks
labelsize = 15


class VisualizeResults:
    def __init__(self):
        self.alg_id = 0
        self.colors = ['blue', 'green', 'black', 'orange', 'red', 'pink', 'black', 'brown', 'purple', 'gray', 'orchid',
                       'chocolate', 'lightseagreen', 'cornflowerblue']
        self.legend = []
        self.plot_metrics = []
        self._counter_cell_stats = 0
        self.sum_throughput = []
        self.num_users = None

        self.num_handovers_per_sec = []
        self.num_rlf_per_sec = []
        self.rlf_per_user = []
        self.sum_throughput_per_sec = []
        self.num_ping_pongs_per_user = []
        self.hit_per_user = []
        self.poor_snr_count_per_user = []
        self.network_latency = []
        self.prepared_cells_count = []
        self.wasted_cells_count = []
        self.handovers_per_user = []
        self.no_df_possible = []  # late data forwarding
        self.alogs = [0]  # 0, 3, 6
        self.num_comparisons = 2  # 3

    def main(self):
        global figsize
        figsize = (25, 5)
        # folder = 'final_results/speed_1.5'
        # folder = 'final_results/hurst_0.9'
        # folder = 'final_results/look_ahead_vs_current'
        folder = 'results'
        files = self.get_json_files(folder)
        files.sort()

        if 'speed' in folder:
            files = files[3:] + files[0:3]

        for i, file in enumerate(files):
            with open(file) as f:
                data = json.load(f)
                print(f"\n{data['sim_params']}")
                sim_duration = data['num_ttis']/10**3/60
                # if 'look' not in data['sim_params']:
                #     continue
                # if data['num_top_gnbs'] != 1:
                #     continue
                # if '0.6' not in data['mob_traces_filename']:
                #     continue
                # if 'Normal' in data['sim_params'] or 'pred' in data['sim_params']:
                #     continue
                # if data['num_ttis'] != 3600000:
                #     continue
                sim_label = self.create_alg_label(data)
                self.legend.append(sim_label)
                self.num_users = data['num_users']

                # self.plot_total_num_handovers(data['total_num_handovers'], sim_duration)
                # self.plot_throughput(data['sum_throughput_per_user'], sim_duration)
                # self.plot_num_rlf(data['RLF'], sim_duration)
                # self.plot_num_unused_prep_cells(data['count_prepared_but_not_used_cells'], sim_duration)
                # self.plot_modulation_at_handover(data['modulation_count'], sim_duration)
                # self.plot_wasted_ttis(data['count_wasted_ttis_per_gnb'], data['num_gnbs'], sim_duration)

                self.plot_cho_cell_stats(data['count_prepared_cells'], data['count_prepared_but_not_used_cells'],
                                         data['total_num_handovers'], sim_duration)
                self.print_stats(data)
                self.collect_stats(data, sim_duration)
                self.count_handovers_per_user(data['who_made_handovers_at_TTI'])
                self.alg_id += 1
        assert len(self.plot_metrics) != 0, "No files were selected. Change goal variable."
        for i, metric in enumerate(self.plot_metrics):
            fig_id = self.get_figure_index(metric)
            plt.figure(fig_id)
            # plt.xticks(labels=self.legend, ticks=list(range(0, len(self.legend))))
            plt.grid(True)
            # self.plot_lables(i)
            pylab.xticks(range(len(self.legend)), self.legend)
            plt.xticks(fontsize=fontsize, rotation=rotation)
            plt.savefig(f"metrics/{self.plot_metrics[i]}.png", dpi=dpi, bbox_inches='tight', pad_inches=0.1)

        # self.plot_throughput_boxplot(sim_duration)
        self.plot_user_cannot_tx_rx_count(sim_duration)
        self.plot_network_latency(sim_duration)
        # self.plot_throughput_gain(sim_duration)  # fixme
        self.box_handover_rate()
        self.box_rlf_rate()
        self.box_throughput()
        self.box_ping_pongs(sim_duration)
        self.plot_hit(sim_duration, with_data_forwarding=False)
        # self.plot_hit(sim_duration, with_data_forwarding=True)

        self.plot_rlf_per_user(sim_duration)
        self.throughput_bar()
        self.plot_prepared_wasted_count(sim_duration)

        # self.plot_hit_without_with_df(sim_duration)

    def print_stats(self, data):
        no_fwd_count = data['no_data_forwarding_possible_count']
        print(f"Forwarding was NOT possible {no_fwd_count} times")

    def create_alg_label(self, data):
        sim_label = self.remove_trailing_underscore(data['sim_params'])
        # if CHOVersions.max_top_gnbs_always_preped in data['handover_alg'] or 'ECHO' in data['handover_alg']:
        # sim_label += f"_LoS-{data['los_update_periodicity']}"

        # sim_label += f"-{data['num_top_gnbs']}"

        # if 'speed1.5' in data['mob_traces_filename']:
        #     sim_label += f"_1.5m/s"
        # elif 'speed1' in data['mob_traces_filename']:
        #     sim_label += f"_1m/s"

        return sim_label

    def plot_total_num_handovers(self, total_num_handovers, sim_duration):
        self.add_metric_to_plot_metics('num_handovers')
        fig_index = self.get_figure_index('num_handovers')
        print(f"Number of handovers = {total_num_handovers}")
        color = self.colors[self.alg_id]
        plt.figure(fig_index)
        plt.grid(True)
        plt.scatter(self.alg_id, int(total_num_handovers), color=color)
        plt.xlabel("Simulation parameters")
        plt.ylabel("Number of handovers")
        # plt.title(f"Number of handovers over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)

    def plot_throughput(self, sum_throughput_per_user, sim_duration):
        self.add_metric_to_plot_metics('sum_tp')
        fig_index = self.get_figure_index('sum_tp')
        sum_tp = 0
        for _, tp in sum_throughput_per_user.items():
            sum_tp += float(tp)
        sum_tp = round(sum_tp, 2)
        print(f"Sum TP = {sum_tp}")
        color = self.colors[self.alg_id]
        plt.figure(fig_index)
        plt.grid(True)
        plt.scatter(self.alg_id, sum_tp, color=color)
        # plt.xlabel("Handover algorithm")
        # plt.xlabel("Simulation parameters")
        # plt.ylabel("Sum throughput (Mbps)")
        plt.ylabel("Average device throughput (Mbps)")
        # plt.title(f"User throughput over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)

    def plot_num_rlf(self, num_rlf, sim_duration):
        self.add_metric_to_plot_metics('RLF')
        fig_id = self.get_figure_index('RLF')
        print(f"Num of RLFs = {num_rlf}")
        color = self.colors[self.alg_id]
        plt.figure(fig_id)
        plt.grid(True)
        plt.scatter(self.alg_id, num_rlf, color=color)
        # plt.xlabel("Handover algorithm")
        # plt.xlabel("Simulation parameters")
        plt.ylabel("Number of RLF")
        # plt.title(f"Radio Link Failures over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)

    def plot_num_unused_prep_cells(self, num_prepared_unused_cells, sim_duration):
        self.add_metric_to_plot_metics('num_wasted_preparations')
        fig_index = self.get_figure_index('num_wasted_preparations')
        color = self.colors[self.alg_id]
        plt.figure(fig_index)
        plt.grid(True)
        plt.scatter(self.alg_id, int(num_prepared_unused_cells), color=color)
        # plt.xlabel("Simulation parameters")
        plt.ylabel("Number of wasted preparations")
        # plt.title(f"Number prepared/released, but not used cells over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)

    def plot_cho_cell_stats(self, prep_cell, unused_cell, num_handovers, sim_duration):
        metric = 'prepare_count'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)
        print(f"Num prepared cells: {prep_cell}")
        print(f"Num prepared unused cells: {unused_cell}")
        plt.figure(fig_index)
        plt.grid(True)
        plt.scatter(self.alg_id, int(prep_cell), color='blue', label='Prepared gNB' if self._counter_cell_stats == 0 else "")
        plt.scatter(self.alg_id, int(unused_cell), color='red', label='Wasted preparation/release gNB' if self._counter_cell_stats == 0 else "")
        self._counter_cell_stats += 1
        # plt.xlabel("Handover algorithm")
        plt.ylabel("Count")
        # plt.title(f"Total prepare/release count for the network over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)
        plt.legend()

    def plot_prepared_wasted_count(self, sim_duration):
        metric = 'prepared_wasted_count'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)
        plt.figure(fig_index)
        plt.grid(True)
        # plt.scatter(self.alg_id, int(prep_cell), color='blue', label='Prepared gNB' if self._counter_cell_stats == 0 else "")
        # plt.scatter(self.alg_id, int(unused_cell), color='red', label='Wasted preparation/release gNB' if self._counter_cell_stats == 0 else "")
        # self._counter_cell_stats += 1
        plt.plot(range(self.alg_id), self.prepared_cells_count, linestyle='dashed', color='blue')
        plt.scatter(range(self.alg_id), self.prepared_cells_count, color='blue', label='Prepared gNBs',)

        plt.plot(range(self.alg_id), self.wasted_cells_count, linestyle='dashed', color='red')
        plt.scatter(range(self.alg_id), self.wasted_cells_count, color='red', label='Wasted preparations')
        print(self.prepared_cells_count)
        print(self.wasted_cells_count)
        print("\n")

        for i in self.alogs:
            for alg in range(1, self.num_comparisons):
                cho = self.prepared_cells_count[i]
                echo = self.prepared_cells_count[i+alg]
                res = (cho-echo)/cho * 100
                print(f"Reduction of prepared cells {self.legend[i]} vs {self.legend[i+alg]} is {res}")

        for i in self.alogs:
            for alg in range(1, self.num_comparisons):
                cho = self.wasted_cells_count[i]
                echo = self.wasted_cells_count[i + alg]
                if cho == 0:
                    cho = 0.01
                res = (cho - echo) / cho * 100
                print(f"Reduction of wasted cells {self.legend[i]} vs {self.legend[i + alg]} is {res}")

        # plt.xlabel("Handover algorithm")
        plt.ylabel("Count", fontsize=labelsize)
        # plt.title(f"Total prepare/release count for the network over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)
        plt.legend()
        plt.grid(True)
        pylab.xticks(range(len(self.legend)), self.legend)
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        plt.savefig(f"metrics/7_{metric}.png", dpi=dpi, bbox_inches='tight', pad_inches=0.1)

    def plot_modulation_at_handover(self, modulation_count, sim_duration):
        self.add_metric_to_plot_metics('modulation_count')
        fig_index = self.get_figure_index('modulation_count')
        print(f"Modulation count = {modulation_count}")
        color = self.colors[self.alg_id]
        plt.figure(fig_index)
        plt.grid(True)
        plt.scatter(self.alg_id, int(modulation_count['same']), color=color)
        # plt.xlabel("Simulation parameters")
        plt.ylabel("Number of handovers to a cell with the same modulation")
        # plt.title(f"Handovers to a cell with the same modulation over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)

    def plot_wasted_ttis(self, wasted_ttis_per_gnb, num_gnbs, sim_duration):
        self.add_metric_to_plot_metics('wasted_ttis')
        fig_index = self.get_figure_index('wasted_ttis')
        total_wasted_ttis = 0
        for key, val in wasted_ttis_per_gnb.items():
            total_wasted_ttis += val
        color = self.colors[self.alg_id]
        plt.figure(fig_index)
        plt.grid(True)
        total_wasted_ttis /= (60*1000)  # min
        print(f"Wasted TTIs = {wasted_ttis_per_gnb}, total = {total_wasted_ttis} min")
        plt.scatter(self.alg_id, float(total_wasted_ttis), color=color)
        # plt.xlabel("Simulation parameters")
        plt.ylabel("Reserved and unused (min)")
        # plt.title(f"Time gNBs were reserved and not used of {num_gnbs} gNBs over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)

    def collect_stats(self, data, sim_duration):
        throughput = [data['sum_throughput_per_user'][key] for key in data['sum_throughput_per_user']]
        self.sum_throughput.append(throughput)
        self.num_handovers_per_sec.append(data['num_handovers_per_sec'])
        self.num_rlf_per_sec.append(data['num_rlf_per_sec'])
        self.sum_throughput_per_sec.append(data['sum_throughput_per_sec'])
        self.prepared_cells_count.append(data['count_prepared_cells'])
        self.wasted_cells_count.append(data['count_prepared_but_not_used_cells'])
        self.no_df_possible.append(data['no_data_forwarding_possible_count'])

        # Statistics is stored in  defaultdict() and they might not have all users there;
        #  if the device is not in the dictionary, then add a zero
        res_hit = []
        res_cannot_tx_rx = []
        res_rlf = []
        res_ping_pong = []
        res_network_latency = []
        network_latency_dict = self.calculate_network_latency(data)

        for i in range(0, self.num_users):  # 30 users
            i = str(i)
            if i not in data['handover_interruption_time']:
                count = 0
                print(f"HIT for device {i} is zero")
            else:
                count = data['handover_interruption_time'][i]
            res_hit.append(count/10**3)  # per sec

            if str(i) not in data['user_cannot_rx_tx']:
                count = 0
                print(f"Cannot tx/rx for device {i} is zero")
            else:
                count = data['user_cannot_rx_tx'][i]
            res_cannot_tx_rx.append(count/10**3)  # sec

            if i not in data['rlf_per_user']:
                count = 0
                print(f"RLF for device {i} is zero")
            else:
                count = data['rlf_per_user'][i]
            res_rlf.append(count)

            if i not in data['ping-pong']:
                count = 0
                print(f"Ping-pong for device {i} is zero")
            else:
                count = data['ping-pong'][i]
            res_ping_pong.append(count)

            if i not in network_latency_dict:
                count = 0
            else:
                count = network_latency_dict[i]
            res_network_latency.append(count/10**3)  # sec

        self.hit_per_user.append(res_hit)
        self.poor_snr_count_per_user.append(res_cannot_tx_rx)
        self.rlf_per_user.append(res_rlf)
        self.num_ping_pongs_per_user.append(res_ping_pong)
        self.network_latency.append(res_network_latency)
        self.handover_rate_bar()
        self.rlf_rate_bar(sim_duration)

    def calculate_network_latency(self, data):
        rlf_duration = {}
        # latency_due_to_rlf = 1000  # ms
        # for key, val in data['rlf_per_user'].items():
        #     rlf_duration[key] = val * latency_due_to_rlf
        counter_hit = Counter(data['handover_interruption_time'])
        counter_cannot_rx_tx = Counter(data['user_cannot_rx_tx'])
        counter_rlf = Counter(rlf_duration)
        network_latency_dict = dict(counter_hit + counter_cannot_rx_tx + counter_rlf)
        return network_latency_dict

    def plot_throughput_boxplot(self, sim_duration):
        color = self.colors[self.alg_id]
        plt.figure(8)
        plt.grid(True)
        # plt.scatter(self.alg_id, total_hit, color=color)
        plt.boxplot(self.sum_throughput, positions=range(self.alg_id))
        # plt.xlabel("Simulation parameters")
        plt.ylabel("Sum Throughput")
        # plt.title(f"Sum throughput per device users over {sim_duration} min")
        # plt.ticklabel_format(useOffset=False)
        plt.scatter(range(self.alg_id), np.mean(self.sum_throughput, axis=1), color=self.colors)
        plt.grid(True)
        plt.legend()
        pylab.xticks(range(len(self.legend)), self.legend)
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        plt.savefig(f"metrics/throughput_boxplot.png", dpi=dpi, bbox_inches='tight', pad_inches=0.1)

    def plot_throughput_gain(self, sim_duration):
        metric = 'throughput_gain'
        self.add_metric_to_plot_metics(metric)
        fig_id = self.get_figure_index(metric)
        plt.figure(fig_id)
        plt.grid(True)
        # local_legend = []
        i = 0
        gains = []

        for i in self.alogs:
            for alg in range(1, self.num_comparisons):
                tp_cho = np.mean(self.sum_throughput[i])
                tp_echo = np.mean(self.sum_throughput[i+alg])
                tp_gain = (tp_echo-tp_cho)/tp_cho * 100
                gains.append(tp_gain)
                plt.scatter(self.legend[i+alg], tp_gain, label=self.legend[i]+' vs '+self.legend[i+alg], color='blue') # plt.bar()
                print(f"Throughput gain {self.legend[i]} vs. {self.legend[i + alg]} is {tp_gain} %")



        plt.plot(range(len(gains)), gains, linestyle='dashed', color='blue')
        # plt.xlabel("Simulation parameters")
        plt.ylabel("Throughput gain (%)")
        # plt.title(f"Average sum throughput gain over {sim_duration} min")
        plt.grid(True)
        plt.legend()
        # pylab.xticks(range(len(local_legend)), local_legend)
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        plt.savefig(f"metrics/8_{metric}.png", dpi=dpi, bbox_inches='tight', pad_inches=0.1)

    def throughput_bar(self):
        metric = 'throughput_bar'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)

        x_pos = np.arange(len(self.legend))
        means = []
        stds = []
        for val in self.sum_throughput_per_sec:
            means.append(np.mean(val))
            stds.append(np.std(val))

        # fig, ax = plt.subplots()
        plt.figure(fig_index)
        ax = plt.gca()
        ax.bar(x_pos, means,
               yerr=stds,
               align='center',
               alpha=0.4,
               ecolor='black',
               capsize=10,
               color=['red', 'blue', 'green'])
        ax.set_ylabel('Sum throughput (Mbps)')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(self.legend)
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        ax.set_title('Sum throughput')
        ax.yaxis.grid(True)
        plt.tight_layout()
        plt.savefig(f'metrics/5_{metric}.png')
        plt.cla()

    def box_handover_rate(self):
        metric = 'num_handovers_per_sec'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)
        # color = self.colors[self.alg_id]
        plt.figure(fig_index)
        plt.grid(True)
        plt.boxplot(self.num_handovers_per_sec, positions=range(self.alg_id))
        # plt.xlabel("Handover algorithm")
        plt.ylabel("Handover rate")
        # plt.title(f"Handover rate per device per sec")
        pylab.xticks(range(len(self.legend)), self.legend)
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        plt.savefig(f"metrics/{metric}.png", dpi=dpi, bbox_inches='tight', pad_inches=0.1)
        plt.cla()

    def handover_rate_bar(self):
        metric = 'handover_rate_bar'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)
        x_pos = np.arange(len(self.legend))
        means = []
        stds = []
        for i, val in enumerate(self.num_handovers_per_sec):
            means.append(np.mean(val))
            stds.append(np.std(val))
            print(f"{self.legend[i]} has HO rate {np.mean(val)}")
        # fig, ax = plt.subplots()

        plt.figure(fig_index)
        ax = plt.gca()
        ax.bar(x_pos, means,
               yerr=stds,
               align='center',
               alpha=0.4,
               ecolor='black',
               capsize=10,
               color=['red', 'blue', 'green'])
        ax.set_ylabel('Count (per sec)', fontsize=labelsize)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(self.legend)
        # ax.set_title('Handover Rate ')
        ax.yaxis.grid(True)
        plt.tight_layout()
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        plt.savefig(f'metrics/3_{metric}.png', dpi=dpi)


    def box_rlf_rate(self):
        metric = 'num_rlf_per_sec'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)
        # color = self.colors[self.alg_id]
        plt.figure(fig_index)
        plt.grid(True)
        plt.boxplot(self.num_rlf_per_sec, positions=range(self.alg_id))
        # plt.xlabel("Handover algorithm")
        plt.ylabel("RLF rate")
        # plt.title(f"Radio Link Failure rate per device per sec")
        pylab.xticks(range(len(self.legend)), self.legend)
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        plt.savefig(f"metrics/{metric}.png", dpi=dpi, bbox_inches='tight', pad_inches=0.1)

    def rlf_rate_bar(self, sim_duration):
        metric = 'rlf_rate_bar'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)
        x_pos = np.arange(len(self.legend))
        means = []
        stds = []
        for val in self.num_rlf_per_sec:
            means.append(np.mean(val))
            stds.append(np.std(val))

        # fig, ax = plt.subplots
        plt.figure(fig_index)
        ax = plt.gca()
        ax.bar(x_pos, means,
               # yerr=stds,
               align='center',
               alpha=0.4,
               ecolor='black',
               capsize=10,
               color=['red', 'blue', 'green'])
        ax.set_ylabel('Count (per sec)', fontsize=labelsize)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(self.legend)
        # ax.set_title(f'RLF Rate.')
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        ax.yaxis.grid(True)
        plt.tight_layout()
        plt.savefig(f'metrics/4_{metric}.png', dpi=dpi)

        for i in range(self.alg_id):
            print(f"Mean RLF rate for alg {self.legend[i]} is {means[i]}")

    def box_throughput(self):
        metric = 'throughput'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)
        plt.figure(fig_index)
        plt.grid(True)
        plt.boxplot(self.sum_throughput_per_sec, positions=range(self.alg_id))
        # plt.xlabel("Handover algorithm")
        plt.ylabel("Sum throughput (Mbps)")
        # plt.title(f"Network sum throughput per sec")
        pylab.xticks(range(len(self.legend)), self.legend)
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        plt.savefig(f"metrics/{metric}.png", dpi=dpi, bbox_inches='tight', pad_inches=0.1)

    def box_ping_pongs(self, sim_duration):
        metric = 'ping_pongs'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)
        plt.figure(fig_index)
        plt.grid(True)
        plt.boxplot(self.num_ping_pongs_per_user, positions=range(self.alg_id))
        for i in self.alogs:
            for alg in range(1, self.num_comparisons):
                cho = np.mean(self.num_ping_pongs_per_user[i])
                echo = np.mean(self.num_ping_pongs_per_user[i+alg])
                res = (cho-echo)/cho*100
                print(f"Number of ping-pongs reduced {self.legend[i]} vs {self.legend[i+alg]} by {res} %")
        # plt.xlabel("Handover algorithm")
        plt.ylabel("Number of ping-pong handovers")
        # plt.title(f"Ping-pong handovers per device over {sim_duration} min")
        pylab.xticks(range(len(self.legend)), self.legend)
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        plt.savefig(f"metrics/1_{metric}.png", dpi=dpi, bbox_inches='tight', pad_inches=0.1)

    def plot_hit(self, sim_duration, with_data_forwarding):
        metric = 'hit'
        if with_data_forwarding:
            self.calc_hit_with_df()
            metric += '_with_df'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)
        plt.figure(fig_index)
        plt.grid(True)
        plt.boxplot(self.hit_per_user, positions=range(self.alg_id))

        # plt.xlabel("Handover algorithm")
        plt.ylabel("Count (per sec)", fontsize=labelsize)
        # plt.title(f"Handover interruption time per device over {sim_duration} min")
        pylab.xticks(range(len(self.legend)), self.legend)
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        plt.savefig(f"metrics/0_{metric}.png", dpi=dpi, bbox_inches='tight', pad_inches=0.1)

        for i in self.alogs:
            for alg in range(1, self.num_comparisons):
                cho = np.mean(self.hit_per_user[i])
                echo = np.mean(self.hit_per_user[i + alg])
                res = (cho - echo) / cho * 100
                print(f"HIT reduced {self.legend[i]} vs {self.legend[i + alg]} by {res} %")

    def plot_hit_without_with_df(self, sim_duration):
        metric = 'hit_without_with_df'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)
        plt.figure(fig_index)
        plt.grid(True)
        plt.boxplot(self.hit_per_user, positions=range(self.alg_id))

        self.calc_hit_with_df()
        plt.boxplot(self.hit_per_user, positions=range(self.alg_id, self.alg_id*2))

        # plt.xlabel("Handover algorithm")
        plt.ylabel("HIT per device (sec)", fontsize=labelsize)
        # plt.title(f"Handover interruption time per device over {sim_duration} min")
        legend = self.legend

        # pylab.xticks(range(len(self.legend), self.legend))
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        plt.savefig(f"metrics/0_{metric}.png", dpi=dpi, bbox_inches='tight', pad_inches=0.1)

    def calc_hit_with_df(self):
        save_with_df = 6/10**3  # sec handover command
        for i in range(len(self.no_df_possible)):
            for user in self.no_df_possible[i]:
                user = int(user)
                num_handovers = self.handovers_per_user[i][user]
                if user not in self.no_df_possible[i]:
                    no_df = 0
                else:
                    no_df = self.no_df_possible[i][user]
                df_possible = num_handovers - no_df
                self.hit_per_user[i][user] -= df_possible * save_with_df

    def plot_network_latency(self, sim_duration):
        metric = 'network_latency'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)
        plt.figure(fig_index)
        plt.grid(True)
        plt.boxplot(self.network_latency, positions=range(self.alg_id))
        plt.xlabel("Handover algorithm")
        plt.ylabel("Network Latency per device (sec)")
        # plt.title(f"Network latency per device over {sim_duration} min")
        pylab.xticks(range(len(self.legend)), self.legend)
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        plt.savefig(f"metrics/{metric}.png", dpi=dpi, bbox_inches='tight', pad_inches=0.1)

    def plot_user_cannot_tx_rx_count(self, sim_duration):
        metric = 'poor_snr'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)
        plt.figure(fig_index)
        plt.grid(True)
        plt.boxplot(self.poor_snr_count_per_user, positions=range(self.alg_id))
        # plt.xlabel("Handover algorithm")
        plt.ylabel("Time (sec)", fontsize=labelsize)
        # plt.title(f"Time device cannot transmit/receive due to poor SNR over {sim_duration} min")
        pylab.xticks(range(len(self.legend)), self.legend)
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        plt.savefig(f"metrics/6_{metric}.png", dpi=dpi, bbox_inches='tight', pad_inches=0.1)

    def plot_rlf_per_user(self, sim_duration):
        metric = 'rlf_per_user'
        self.add_metric_to_plot_metics(metric)
        fig_index = self.get_figure_index(metric)
        plt.figure(fig_index)
        plt.grid(True)
        plt.boxplot(self.rlf_per_user, positions=range(self.alg_id))
        # plt.xlabel("Handover algorithm")
        plt.ylabel("RLF count")
        # plt.title(f"Total number of RLFs per device over {sim_duration} min")
        pylab.xticks(range(len(self.legend)), self.legend)
        plt.xticks(fontsize=fontsize, rotation=rotation)  # 90
        plt.savefig(f"metrics/{metric}.png", dpi=dpi, bbox_inches='tight', pad_inches=0.1)

    def count_handovers_per_user(self, who_made_handovers_at_TTI):
        handovers_per_user = defaultdict(int)
        for tti, users in who_made_handovers_at_TTI.items():
            for user in users:
                handovers_per_user[user] += 1
        self.handovers_per_user.append(handovers_per_user)

    def plot_lables(self, fig_num):
        plt.figure(fig_num)
        plt.grid()

        plt.tick_params(labelsize=fontsize, pad=0.1)
        plt.xticks(range(len(self.legend)))
        handles = []
        for i in range(len(self.legend)):
            handle = mpatches.Patch(color=self.colors[i], label=self.legend[i])
            handles.append(handle)
        plt.legend(handles=handles)
        plt.gcf().set_size_inches(4, 4)

    def get_json_files(self, folder):
        os.chdir(folder)
        try:
            os.mkdir("metrics")
        except FileExistsError:
            pass

        files = get_all_files()
        print(f"Number of json files is {len(files)}")
        return files

    def add_metric_to_plot_metics(self, name):
        if name not in self.plot_metrics:
            self.plot_metrics.append(name)

    def get_figure_index(self, name):
        return self.plot_metrics.index(name)

    @staticmethod
    def remove_trailing_underscore(word):
        if word[-1] == '_':
            return word[:-1]
        else:
            return word


if __name__ == "__main__":
    vis_res = VisualizeResults()
    vis_res.main()



