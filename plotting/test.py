import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
# from runtime.SimulationParameters import SimulationParameters
import seaborn
import tikzplotlib

from definitions import RESULTS_DIR

seaborn.set(style="ticks")


class Oct29Plots:
    def __init__(self):
        self.max_rate_radio_aware_files = []
        self.max_rate_non_radio_aware_files = []
        self.round_robin_radio_aware_files = []
        self.round_robin_non_radio_aware_files = []
        self.random_radio_aware_files = []
        self.random_non_radio_aware_files = []
        self.proportional_fair_radio_aware_files = []
        self.proportional_fair_non_radio_aware_files = []
        self.num_of_users = [50]

        res_dir = RESULTS_DIR + "reproduction/test/"
        print("RES DIR")
        print(res_dir)

        radio_scheduling_algorithms = ["Proportional_Fair", "Random", "Round_Robin", "Max_Rate"]
        radio_aware_status = ["FCFS", "Radio-Aware"]

        for i in self.num_of_users:
            for j in radio_scheduling_algorithms:
                for k in radio_aware_status:
                    if j == "Proportional_Fair":
                        if k == "Radio-Aware":
                            self.proportional_fair_radio_aware_files.append(
                                res_dir +
                                str(i) + '_' + str(j) + '_' + str(k) + '_1.csv')
                        else:
                            self.proportional_fair_non_radio_aware_files.append(
                                res_dir +
                                str(i) + '_' + str(j) + '_' + str(k) + '_1.csv')

                    if j == "Random":
                        if k == "Radio-Aware":
                            self.random_radio_aware_files.append(
                                res_dir +
                                str(i) + '_' + str(j) + '_' + str(k) + '_1.csv')
                        else:
                            self.random_non_radio_aware_files.append(
                                res_dir +
                                str(i) + '_' + str(j) + '_' + str(k) + '_1.csv')

                    if j == "Max_Rate":
                        if k == "Radio-Aware":
                            self.max_rate_radio_aware_files.append(
                                res_dir +
                                str(i) + '_' + str(j) + '_' + str(k) + '_1.csv')
                        else:
                            self.max_rate_non_radio_aware_files.append(
                                res_dir +
                                str(i) + '_' + str(j) + '_' + str(k) + '_1.csv')

                    if j == "Round_Robin":
                        if k == "Radio-Aware":
                            self.round_robin_radio_aware_files.append(
                                res_dir +
                                str(i) + '_' + str(j) + '_' + str(k) + '_1.csv')
                        else:
                            self.round_robin_non_radio_aware_files.append(
                                res_dir +
                                str(i) + '_' + str(j) + '_' + str(k) + '_1.csv')

    def plot_TotalLatencyVsAlgorithm_desired_latency100(self):
        pf_radio_aware_latencies = []
        pf_radio_aware_completion_rate = []
        pf_non_radio_aware_latencies = []
        pf_non_radio_aware_completion_rate = []
        mr_radio_aware_latencies = []
        mr_radio_aware_completion_rate = []
        mr_non_radio_aware_latencies = []
        mr_non_radio_aware_completion_rate = []
        random_radio_aware_latencies = []
        random_radio_aware_completion_rate = []
        random_non_radio_aware_latencies = []
        random_non_radio_aware_completion_rate = []
        rr_radio_aware_latencies = []
        rr_radio_aware_completion_rate = []
        rr_non_radio_aware_latencies = []
        rr_non_radio_aware_completion_rate = []

        total_sent_packets = [i * 999 for i in self.num_of_users]
        desired_latency = 100
        print("TOTAL SENT PACKETS")
        print(total_sent_packets)

        for file in self.proportional_fair_radio_aware_files:
            data = pd.read_csv(file)
            pf_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            pf_radio_aware_completion_rate.append(len(data["Total Latency"] < desired_latency))

        print("pf ra before")
        print(pf_radio_aware_completion_rate)

        pf_radio_aware_completion_rate = np.divide(pf_radio_aware_completion_rate, total_sent_packets)

        for file in self.proportional_fair_non_radio_aware_files:
            data = pd.read_csv(file)
            pf_non_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            pf_non_radio_aware_completion_rate.append(len(data[data["Total Latency"] < desired_latency]))
        pf_non_radio_aware_completion_rate = np.divide(pf_non_radio_aware_completion_rate, total_sent_packets)

        for file in self.max_rate_radio_aware_files:
            data = pd.read_csv(file)
            mr_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            mr_radio_aware_completion_rate.append(len(data[data["Total Latency"] < desired_latency]))

        mr_radio_aware_completion_rate = np.divide(mr_radio_aware_completion_rate, total_sent_packets)

        for file in self.max_rate_non_radio_aware_files:
            data = pd.read_csv(file)
            mr_non_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            mr_non_radio_aware_completion_rate.append(len(data[data["Total Latency"] < desired_latency]))

        mr_non_radio_aware_completion_rate = np.divide(mr_non_radio_aware_completion_rate, total_sent_packets)

        print("RR RADIO AWARE FILES")
        print(self.round_robin_radio_aware_files)

        for file in self.round_robin_radio_aware_files:

            data = pd.read_csv(file)
            rr_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            rr_radio_aware_completion_rate.append(len(data[data["Total Latency"] < desired_latency]))

        print("rr ra before")
        print(rr_radio_aware_completion_rate)
        rr_radio_aware_completion_rate = np.divide(rr_radio_aware_completion_rate, total_sent_packets)

        for file in self.round_robin_non_radio_aware_files:
            data = pd.read_csv(file)
            rr_non_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            rr_non_radio_aware_completion_rate.append(len(data[data["Total Latency"] < desired_latency]))

        rr_non_radio_aware_completion_rate = np.divide(rr_non_radio_aware_completion_rate, total_sent_packets)

        for file in self.random_radio_aware_files:
            data = pd.read_csv(file)
            random_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            random_radio_aware_completion_rate.append(len(data[data["Total Latency"] < desired_latency]))
        random_radio_aware_completion_rate = np.divide(random_radio_aware_completion_rate, total_sent_packets)

        for file in self.random_non_radio_aware_files:
            data = pd.read_csv(file)
            random_non_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            random_non_radio_aware_completion_rate.append(len(data[data["Total Latency"] < desired_latency]))
        random_non_radio_aware_completion_rate = np.divide(random_non_radio_aware_completion_rate, total_sent_packets)

        print("Proportional Fair Radio Aware")
        print(pf_radio_aware_latencies)
        print("Max Rate Radio Aware")
        print(mr_radio_aware_latencies)
        print("Random Radio Aware")
        print(random_radio_aware_latencies)
        print("RR Radio Aware")
        print(rr_radio_aware_latencies)

        # plt.plot(self.num_of_users, random_radio_aware_completion_rate, label="Random-RA")
        # plt.plot(self.num_of_users, random_non_radio_aware_completion_rate, label="Random-RNA")
        # plt.plot(self.num_of_users, mr_radio_aware_completion_rate, label="MaxRate-RA", marker="o")
        # plt.plot(self.num_of_users, mr_non_radio_aware_completion_rate, label="MaxRate-RNA", marker="v")
        # plt.plot(self.num_of_users, rr_radio_aware_completion_rate, label="RoundRobin-RA", marker="d")
        # plt.plot(self.num_of_users, rr_non_radio_aware_completion_rate, label="RoundRobin-RNA", marker="D")
        # plt.plot(self.num_of_users, pf_radio_aware_completion_rate, label="ProportionallyFair-RA", marker="s")
        # plt.plot(self.num_of_users, pf_non_radio_aware_completion_rate, label="ProportionallyFair-RNA", marker="P")
        # #
        #
        # plt.legend()
        # plt.show()
        #
        print("PF RA")
        print(pf_radio_aware_completion_rate)
        print("PF NONE")
        print(pf_non_radio_aware_completion_rate)
        print("RR RA")
        print(rr_radio_aware_completion_rate)
        print("RR NONE")
        print(rr_non_radio_aware_completion_rate)
        print("MR RA")
        print(mr_radio_aware_completion_rate)
        print("MR NONE")
        print(mr_non_radio_aware_completion_rate)
        print("RANDOM RA")
        print(random_radio_aware_completion_rate)
        print("RANDOM NONE")
        print(random_non_radio_aware_completion_rate)

        # plt.plot(self.num_of_users, pf_radio_aware_latencies, label="PF-RA")
        # plt.plot(self.num_of_users, mr_radio_aware_latencies, label="MR-RA")
        # plt.plot(self.num_of_users, rr_radio_aware_latencies, label="RR-RA")
        # # plt.plot(self.num_of_users, random_radio_aware_latencies, label="Random-RA")
        # plt.plot(self.num_of_users, pf_non_radio_aware_latencies, label="PF-RNA")
        # plt.plot(self.num_of_users, mr_non_radio_aware_latencies, label="MR-RNA")
        # plt.plot(self.num_of_users, rr_non_radio_aware_latencies, label="RR-RNA")
        # plt.plot(self.num_of_users, random_non_radio_aware_latencies, label="Random-RNA")
        # plt.xlabel("Number of Users")
        # # plt.ylabel("Average Task Processing Latency (ms)")
        # plt.ylabel("On-Time Completion Rate of Tasks")
        # plt.legend(fontsize="10")
        # fig = plt.gcf()
        # fig.set_size_inches(18.5, 10.5)
        # # plt.show()
        # tikzplotlib.save("completion_rate_vs_num_users.tex")

Oct29Plots().plot_TotalLatencyVsAlgorithm_desired_latency100()
