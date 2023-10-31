import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from runtime.utilities import get_all_files

# Mean and std, as well as plots are saved in results.json in the folder res_plots


class VisualizeResults:
    def __init__(self):
        self.alg_id = 0
        self.colors = ['blue', 'green', 'black', 'orange', 'red', 'pink']
        self.legend = []
        self.plot_metrics = ['num_handovers', 'sum_tp', 'RLF', 'ping_pongs', 'delays', 'drop_rate']

    def main(self):
        files = self.get_json_files()
        for i, file in enumerate(files):
            with open(file) as f:
                data = json.load(f)
                print(f"\n{data['sim_params']}")
                sim_duration = data['num_ttis']/10**3/60
                # self.legend.append(data['handover_alg'])
                #self.legend.append(data['sim_params'][-3::])
                self.legend.append(data['sim_params'])
                self.plot_total_num_handovers(data['total_num_handovers'], sim_duration)
                self.plot_sum_tp(data['sum_throughput_per_user'], sim_duration)
                self.plot_num_rlf(data['RLF'], sim_duration)
                self.plot_ping_pongs(data['ping-pong'], sim_duration)
                #self.plot_avg_delay(data['delay_per_user'], sim_duration)
                #self.plot_drop_rate(data['drop_rate_per_user'], sim_duration)
                self.alg_id += 1

        for i in range(len(self.plot_metrics)):
            plt.figure(i)
            plt.xticks(labels=self.legend, ticks=list(range(0, len(self.legend))))
            plt.grid()


            plt.savefig(f"metrics/{self.plot_metrics[i]}.png", dpi=1200, bbox_inches='tight', pad_inches=0.1)

    def plot_total_num_handovers(self, total_num_handovers, sim_duration):
        print(f"Number of handovers = {total_num_handovers}")
        color = self.colors[self.alg_id]
        plt.figure(0)
        plt.scatter(self.alg_id, int(total_num_handovers), color=color)
        plt.xlabel("Handover algorithm")
        #plt.xlabel("Error probability")
        plt.ylabel("Number of handovers")
        plt.title(f"Number of handovers over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)

    def plot_sum_tp(self, sum_throughput_per_user, sim_duration):
        sum_tp = 0
        for _, tp in sum_throughput_per_user.items():
            sum_tp += float(tp)
        sum_tp /= 10**6
        sum_tp = round(sum_tp, 2)
        print(f"Sum TP = {sum_tp}")
        plt.figure(1)
        plt.scatter(self.alg_id, sum_tp)
        plt.xlabel("Handover algorithm")
        #plt.xlabel("Error probability")
        plt.ylabel("Sum throughput (Mbps)")
        plt.title(f"Sum throughput over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)

    def plot_avg_delay(self, delay_per_user, sim_duration):
        sum_delay = 0
        i = 0
        for _, delay in delay_per_user.items():
            if not np.isnan(delay):
                sum_delay += float(delay)
                i += 1
        sum_delay /= float(i)
        sum_delay = round(sum_delay, 2)
        plt.figure(4)
        plt.scatter(self.alg_id, sum_delay)
        plt.xlabel("Error probability")
        plt.ylabel("Average delay (ms)")
        plt.title(f"Average delay over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)

    def plot_drop_rate(self, drop_rate_per_user, sim_duration):
        sum_rate = 0
        i = 0
        for _, drop_rate in drop_rate_per_user.items():
            sum_rate += float(drop_rate)
            i += 1
        sum_rate /= float(i)
        sum_rate = round(sum_rate, 2)
        plt.figure(5)
        plt.scatter(self.alg_id, sum_rate)
        plt.xlabel("Error probability")
        plt.ylabel("Average drop rate")
        plt.title(f"Average drop rate over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)

    def plot_num_rlf(self, num_rlf, sim_duration):
        print(f"Num of RLFs = {num_rlf}")
        plt.figure(2)
        plt.scatter(self.alg_id, num_rlf)
        plt.xlabel("Handover algorithm")
        #plt.xlabel("Error probability")
        plt.ylabel("Number of RLF")
        plt.title(f"Radio Link Failures over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)

    def plot_ping_pongs(self, ping_pong_per_user, sim_duration):
        num_ping_pongs = 0
        for _, num in ping_pong_per_user.items():
            num_ping_pongs += int(num)
        print(f"Num of ping-pongs {num_ping_pongs}")
        plt.figure(3)
        plt.scatter(self.alg_id, num_ping_pongs)
        plt.xlabel("Handover algorithm")
        #plt.xlabel("Error probability")
        plt.ylabel("Number of ping-pong handovers")
        plt.title(f"Ping-pong handovers over {sim_duration} min")
        plt.ticklabel_format(useOffset=False)

    def plot_lables(self, fig_num):
        plt.figure(fig_num)
        plt.grid()

        plt.tick_params(labelsize=10, pad=0.1)
        handles = []
        for i in range(len(self.legend)):
            handle = mpatches.Patch(color=self.colors[i], label=self.legend[i])
            handles.append(handle)
        plt.legend(handles=handles)
        plt.gcf().set_size_inches(4, 4)

    def get_json_files(self):
        #os.chdir('tests/results')
        os.chdir('results')
        try:
            os.mkdir("metrics")
        except FileExistsError:
            pass

        files = get_all_files()
        print(f"Number of json files is {len(files)}")
        return files


if __name__ == "__main__":
    vis_res = VisualizeResults()
    vis_res.main()



