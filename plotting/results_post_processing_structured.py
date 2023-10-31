import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from runtime.SimulationParameters import SimulationParameters
import seaborn
import tikzplotlib

seaborn.set(style="ticks")

sim_params = SimulationParameters()


def plot_cdf(data):
    count, bins_count = np.histogram(data, bins=1000)
    pdf = count / sum(count)
    cdf = np.cumsum(pdf)
    plt.plot(bins_count[1:], cdf, label="CDF")
    plt.legend()
    # plt.show()


class LatencyOverTime:
    def __init__(self, file=None):
        self.file = os.pardir + '/results/sigcomm/2023-05-22T15:20:50.089850.csv'

    def generate_plot(self):
        csv_data = pd.read_csv(self.file)
        csv_data.sort_values(["Sequence Number"], axis=0, ascending=[True], inplace=True)
        print("\nAfter sorting:")
        print(csv_data)
        latency_per_user = {}
        for index, row in csv_data.iterrows():
            print(row['Latency'])
            tmp_user_id = int(row["User ID"])
            tmp_latency = row["Latency"]
            if int(row[0]) not in latency_per_user:
                latency_per_user[tmp_user_id] = []
                latency_per_user[tmp_user_id].append(tmp_latency)
            else:
                latency_per_user[tmp_user_id].append(tmp_latency)

        latency_per_user = {key: latency_per_user[key] for key in sorted(latency_per_user.keys())}
        print(latency_per_user)

        for key in latency_per_user.keys():
            y = [i * sim_params.TTI_duration for i in range(len(latency_per_user[key]))]
            plt.plot(y, latency_per_user[key])

        plt.show()


class LatencyStatisticsVsAlgorithm:
    def __init__(self):
        self.file_1 = os.pardir + '/results/sigcomm/Indoor factory_Max_Rate_LatencyAware.csv'
        self.file_2 = os.pardir + '/results/sigcomm/Indoor factory_Random_LatencyAware.csv'
        self.file_3 = os.pardir + '/results/sigcomm/Indoor factory_Round_Robin_LatencyAware.csv'
        self.file_4 = os.pardir + '/results/sigcomm/Indoor factory_Max_Rate_random.csv'
        self.file_5 = os.pardir + '/results/sigcomm/Indoor factory_Random_random.csv'
        self.file_6 = os.pardir + '/results/sigcomm/Indoor factory_Round_Robin_random.csv'
        self.files = [self.file_1, self.file_2, self.file_3, self.file_4, self.file_5, self.file_6]
        self.labels = ["MaxRate-LatencyAware", "Random-LatencyAware", "RoundRobin-LatencyAware",
                       "MaxRate-Random", "Random-Random", "RoundRobin-Random"]
        # self.files = [self.file_1]

    def generate_plot(self):
        datas = []
        fig1, ax1 = plt.subplots()
        for file in self.files:
            csv_data = pd.read_csv(file)
            datas.append(csv_data["Total Latency"])

        fig1.set_figheight(20)
        fig1.set_figwidth(25)
        ax1.set_title(
            "Task Completion Time Distribution vs Resource Allocation-Service Placement Algorithm Combinations "
            "in an Indoor Factory Setup")
        # ax1.set_title("Algorithms")
        ax1.set_xlabel('Algorithms')
        ax1.set_ylabel('Average Task Completion Time(ms)')
        ax1.boxplot(datas, patch_artist=True, showfliers=False, labels=self.labels)
        ax1.tick_params(axis='x', labelrotation=45)
        plt.show()


class LatencyStatisticsVsAlgorithmPartitioned:
    def __init__(self):
        self.file_1 = os.pardir + '/results/sigcomm/Indoor factory_Max_Rate_LatencyAware.csv'
        self.file_2 = os.pardir + '/results/sigcomm/Indoor factory_Random_LatencyAware.csv'
        self.file_3 = os.pardir + '/results/sigcomm/Indoor factory_Round_Robin_LatencyAware.csv'
        self.file_4 = os.pardir + '/results/sigcomm/Indoor factory_Max_Rate_random.csv'
        self.file_5 = os.pardir + '/results/sigcomm/Indoor factory_Random_random.csv'
        self.file_6 = os.pardir + '/results/sigcomm/Indoor factory_Round_Robin_random.csv'
        self.files = [self.file_1, self.file_2, self.file_3, self.file_4, self.file_5, self.file_6]
        self.labels = ["MaxRate-LatencyAware", "Random-LatencyAware", "RoundRobin-LatencyAware",
                       "MaxRate-Random", "Random-Random", "RoundRobin-Random"]

    def generate_plot(self):
        ul_latency_data = []
        edge_latency_data = []
        fig, ax = plt.subplots()
        for file in self.files:
            csv_data = pd.read_csv(file)
            ul_latency_data.append(csv_data["UL Latency"])
            edge_latency_data.append(csv_data["Total Latency"] - csv_data["UL Latency"])

        ul_latency_plot = ax.boxplot(ul_latency_data,
                                     positions=np.array(
                                         np.arange(len(ul_latency_data))) * 2.0 - 0.35,
                                     showfliers=False,
                                     widths=0.6)
        edge_latency_plot = ax.boxplot(edge_latency_data,
                                       patch_artist=True,
                                       showfliers=False,
                                       positions=np.array(
                                           np.arange(len(edge_latency_data))) * 2.0 + 0.35,
                                       widths=0.6)

        def define_box_properties(plot_name, color_code, label):
            for k, v in plot_name.items():
                plt.setp(plot_name.get(k), color=color_code)

            # use plot function to draw a small line to name the legend.
            plt.plot([], c=color_code, label=label)
            plt.legend()

        # setting colors for each groups
        define_box_properties(ul_latency_plot, '#D7191C', 'RAN Latency')
        define_box_properties(edge_latency_plot, '#2C7BB6', 'Wired Delay + Processing')

        # set the x label values
        plt.xticks(np.arange(0, len(self.labels) * 2, 2), self.labels)

        # set the limit for x axis
        # plt.xlim(-2, len(self.labels) * 2)

        # set the limit for y axis
        # plt.ylim(0, 50)

        # set the title
        plt.title(
            "Task Completion Time Latency Dsitributions vs Resource Allocation-Service Placement Algorithm Combinations"
            "in an Indoor Factory Setup")

        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        plt.show()


class NumOfUsersVsLatency:
    def __init__(self):
        self.rr_11250_files = []
        self.rr_45000_files = []
        self.mr_11250_files = []
        self.mr_45000_files = []
        self.random_11250_files = []
        self.random_45000_files = []
        self.pf_11250_files = []
        self.pf_45000_files = []
        self.labels = []
        # for i in range(10, 110, 10):
        #     self.rr_11250_files.append(os.pardir + '/results/sigcomm/Round_Robin_num_of_users_' +
        #                                str(i) + 'cycles_per_bit_11250.csv')
        #     self.rr_45000_files.append(os.pardir + '/results/sigcomm/Round_Robin_num_of_users_' +
        #                                str(i) + 'cycles_per_bit_45000.csv')
        #
        #     self.mr_11250_files.append(os.pardir + '/results/sigcomm/Max_Rate_num_of_users_' +
        #                                str(i) + 'cycles_per_bit_11250.csv')
        #     self.mr_45000_files.append(os.pardir + '/results/sigcomm/Max_Rate_num_of_users_' +
        #                                str(i) + 'cycles_per_bit_45000.csv')
        #
        #     self.random_11250_files.append(os.pardir + '/results/sigcomm/Random_num_of_users_' +
        #                                    str(i) + 'cycles_per_bit_11250.csv')
        #     self.random_45000_files.append(os.pardir + '/results/sigcomm/Random_num_of_users_' +
        #                                    str(i) + 'cycles_per_bit_45000.csv')
        #
        #     self.pf_11250_files.append(os.pardir + '/results/sigcomm/Proportional_Fair_num_of_users_' +
        #                                str(i) + 'cycles_per_bit_11250.csv')
        #     self.pf_45000_files.append(os.pardir + '/results/sigcomm/Proportional_Fair_num_of_users_' +
        #                                str(i) + 'cycles_per_bit_45000.csv')
        #
        #     self.labels.append(str(i))

    def generate_latency_dst_plot(self):
        task_processing_time = []
        ul_latency = []
        fig, ax = plt.subplots(2, 2)
        fig.set_size_inches(20, 12)
        for file in self.rr_45000_files:
            csv_data = pd.read_csv(file)
            task_processing_time.append(np.mean(csv_data["Total Latency"] - csv_data["UL Latency"]))
            ul_latency.append(np.mean(csv_data["UL Latency"]))

        ax[0, 0].plot(self.labels, task_processing_time, label="Processing Latency")
        ax[0, 0].plot(self.labels, ul_latency, label="Network Latency")
        ax[0, 0].title.set_text("Round Robin")
        ax[0, 0].set_xlabel("Num of Users")
        ax[0, 0].set_ylabel("Time(ms)")
        ax[0, 0].legend(loc=0)

        task_processing_time = []
        ul_latency = []
        for file in self.mr_45000_files:
            csv_data = pd.read_csv(file)
            task_processing_time.append(np.mean(csv_data["Total Latency"] - csv_data["UL Latency"]))
            ul_latency.append(np.mean(csv_data["UL Latency"]))
        ax[0, 1].plot(self.labels, task_processing_time, label="Processing Latency")
        ax[0, 1].plot(self.labels, ul_latency, label="Network Latency")
        ax[0, 1].title.set_text("Max Rate")
        ax[0, 1].set_xlabel("Num of Users")
        ax[0, 1].set_ylabel("Time(ms)")
        ax[0, 1].legend(loc=0)

        task_processing_time = []
        ul_latency = []
        for file in self.pf_45000_files:
            csv_data = pd.read_csv(file)
            task_processing_time.append(np.mean(csv_data["Total Latency"] - csv_data["UL Latency"]))
            ul_latency.append(np.mean(csv_data["UL Latency"]))

        ax[1, 0].plot(self.labels, task_processing_time, label="Processing Latency")
        ax[1, 0].plot(self.labels, ul_latency, label="Network Latency")
        ax[1, 0].title.set_text("Proportional Fair")
        ax[1, 0].set_xlabel("Num of Users")
        ax[1, 0].set_ylabel("Time(ms)")
        ax[1, 0].legend(loc=0)

        task_processing_time = []
        ul_latency = []
        for file in self.random_45000_files:
            csv_data = pd.read_csv(file)
            task_processing_time.append(np.mean(csv_data["Total Latency"] - csv_data["UL Latency"]))
            ul_latency.append(np.mean(csv_data["UL Latency"]))

        ax[1, 1].plot(self.labels, task_processing_time, label="Processing Latency")
        ax[1, 1].plot(self.labels, ul_latency, label="Network Latency")
        ax[1, 1].set_xlabel("Num of Users")
        ax[1, 1].set_ylabel("Time(ms)")
        ax[1, 1].title.set_text("Random")
        ax[1, 1].legend(loc=0)

        plt.show()

    def task_size_vs_num_of_users(self):
        task_processing_latency_11250 = []
        task_processing_latency_45000 = []
        self.labels = []

        for i in range(50, 300, 50):
            self.pf_11250_files.append(os.pardir + '/results/sigcomm/Proportional_Fair_num_of_users_' +
                                       str(i) + 'cycles_per_bit_11250.csv')
            self.pf_45000_files.append(os.pardir + '/results/sigcomm/Proportional_Fair_num_of_users_' +
                                       str(i) + 'cycles_per_bit_45000.csv')
            self.labels.append(str(i))

        for file in self.pf_11250_files:
            csv_data = pd.read_csv(file)
            task_processing_latency_11250.append(np.mean(csv_data["Total Latency"] - csv_data["UL Latency"]))

        for file in self.pf_45000_files:
            csv_data = pd.read_csv(file)
            task_processing_latency_45000.append(np.mean(csv_data["Total Latency"] - csv_data["UL Latency"]))

        print(task_processing_latency_45000)
        print(task_processing_latency_11250)

        plt.plot(self.labels, task_processing_latency_11250, label="250 Million Instructions")
        plt.plot(self.labels, task_processing_latency_45000, label="1000 Million Instructions")
        print(self.labels)
        plt.xlabel("Num of Users")
        plt.ylabel("Task Processing Latency")
        plt.legend()
        plt.show()


class AutoscalingPlots:
    def __init__(self):
        self.labels = []
        self.rr_autoscaling_files = []
        self.random_autoscaling_files = []
        self.rr_none_files = []
        self.random_none_files = []
        self.non_autoscaling_files = []
        for i in range(10, 160, 10):
            self.rr_autoscaling_files.append(os.pardir + '/results/sigcomm/May31/Round_Robin_num_of_users_' +
                                             str(i) + '_autoscaling.csv')
            self.random_autoscaling_files.append(os.pardir + '/results/sigcomm/May31/Random_num_of_users_' +
                                                 str(i) + '_autoscaling.csv')
            self.rr_none_files.append(os.pardir + '/results/sigcomm/May31/Round_Robin_num_of_users_' +
                                      str(i) + '_None.csv')
            self.random_none_files.append(os.pardir + '/results/sigcomm/May31/Random_num_of_users_' +
                                          str(i) + '_None.csv')
            self.labels.append(str(i))

    def total_latency_vs_user(self):
        total_latency_rr_as = []
        total_latency_random_as = []
        total_latency_rr_none = []
        total_latency_random_none = []
        for file in self.rr_autoscaling_files:
            csv_data = pd.read_csv(file)
            total_latency_rr_as.append(np.mean(csv_data["Processing Time"]))
        for file in self.rr_none_files:
            csv_data = pd.read_csv(file)
            total_latency_rr_none.append(np.mean(csv_data["Processing Time"]))

        print('Total Latency AS')
        print(total_latency_rr_as)
        print('Total Latency None')
        print(total_latency_rr_none)

        plt.plot(self.labels, total_latency_rr_as, label="RR-AS")
        plt.plot(self.labels, total_latency_rr_none, label="RR-None")
        plt.xlabel("Num of Users")
        plt.ylabel("Total Latency (ms)")
        plt.legend()
        plt.show()


class RadioAwareProcessingDesiredLatency30:

    def __init__(self):
        self.max_rate_radio_aware_files = []
        self.max_rate_non_radio_aware_files = []
        self.round_robin_radio_aware_files = []
        self.round_robin_non_radio_aware_files = []
        self.random_radio_aware_files = []
        self.random_non_radio_aware_files = []
        self.proportional_fair_radio_aware_files = []
        self.proportional_fair_non_radio_aware_files = []
        self.num_of_users = [300, 350, 400, 450, 500, 550, 600]

        radio_scheduling_algorithms = ["Proportional_Fair", "Random", "Round_Robin", "Max_Rate"]
        radio_aware_status = ["radio-aware", "None"]

        for i in self.num_of_users:
            for j in radio_aware_status:
                for k in radio_scheduling_algorithms:
                    if k == "Proportional_Fair":
                        if j == "radio-aware":
                            self.proportional_fair_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June4/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')
                        else:
                            self.proportional_fair_non_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June4/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')

                    if k == "Random":
                        if j == "radio-aware":
                            self.random_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June4/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')
                        else:
                            self.random_non_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June4/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')

                    if k == "Max_Rate":
                        if j == "radio-aware":
                            self.max_rate_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June4/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')
                        else:
                            self.max_rate_non_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June4/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')

                    if k == "Round_Robin":
                        if j == "radio-aware":
                            self.round_robin_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June4/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')
                        else:
                            self.round_robin_non_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June4/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')

        print("RANDOM RADIO AWARE")
        print(self.random_radio_aware_files)

    def plot_TotalLatencyVsAlgorithm_desired_latency30(self):
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

        total_sent_packets = [i * 99 for i in self.num_of_users]
        print("TOTAL SENT PACKETS")
        print(total_sent_packets)

        for file in self.proportional_fair_radio_aware_files:
            data = pd.read_csv(file)
            pf_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            pf_radio_aware_completion_rate.append(len(data["Total Latency"] < 30))
        pf_radio_aware_completion_rate = np.divide(pf_radio_aware_completion_rate, total_sent_packets)

        for file in self.proportional_fair_non_radio_aware_files:
            data = pd.read_csv(file)
            pf_non_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            pf_non_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 30]))
        pf_non_radio_aware_completion_rate = np.divide(pf_non_radio_aware_completion_rate, total_sent_packets)

        for file in self.max_rate_radio_aware_files:
            data = pd.read_csv(file)
            mr_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            mr_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 30]))

        mr_radio_aware_completion_rate = np.divide(mr_radio_aware_completion_rate, total_sent_packets)

        for file in self.max_rate_non_radio_aware_files:
            data = pd.read_csv(file)
            mr_non_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            mr_non_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 30]))

        mr_non_radio_aware_completion_rate = np.divide(mr_non_radio_aware_completion_rate, total_sent_packets)

        for file in self.round_robin_radio_aware_files:
            data = pd.read_csv(file)
            rr_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            rr_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 30]))

        rr_radio_aware_completion_rate = np.divide(rr_radio_aware_completion_rate, total_sent_packets)

        for file in self.round_robin_non_radio_aware_files:
            data = pd.read_csv(file)
            rr_non_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            rr_non_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 30]))

        rr_non_radio_aware_completion_rate = np.divide(rr_non_radio_aware_completion_rate, total_sent_packets)

        for file in self.random_radio_aware_files:
            data = pd.read_csv(file)
            random_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            random_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 30]))
        random_radio_aware_completion_rate = np.divide(random_radio_aware_completion_rate, total_sent_packets)

        for file in self.random_non_radio_aware_files:
            data = pd.read_csv(file)
            random_non_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            random_non_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 30]))
        random_non_radio_aware_completion_rate = np.divide(random_non_radio_aware_completion_rate, total_sent_packets)

        # print("Proportional Fair Radio Aware")
        # print(pf_radio_aware_latencies)
        # print("Max Rate Non Radio Aware")
        # print(mr_radio_aware_latencies)

        plt.plot(self.num_of_users, random_radio_aware_completion_rate, label="Random-RA")
        plt.plot(self.num_of_users, random_non_radio_aware_completion_rate, label="Random-RNA")
        plt.plot(self.num_of_users, mr_radio_aware_completion_rate, label="MaxRate-RA")
        plt.plot(self.num_of_users, mr_non_radio_aware_completion_rate, label="MaxRate-RNA")
        plt.plot(self.num_of_users, rr_radio_aware_completion_rate, label="RoundRobin-RA")
        plt.plot(self.num_of_users, rr_non_radio_aware_completion_rate, label="RoundRobin-RNA")
        plt.plot(self.num_of_users, pf_radio_aware_completion_rate, label="ProportionallyFair-RA")
        plt.plot(self.num_of_users, pf_non_radio_aware_completion_rate, label="ProportionallyFair-RNA")
        #
        #
        # plt.legend()
        # plt.show()
        #
        # print("PF RA")
        # print(pf_radio_aware_completion_rate)
        # print("PF NONE")
        # print(pf_non_radio_aware_completion_rate)
        # print("RR RA")
        # print(rr_radio_aware_completion_rate)
        # print("RR NONE")
        # print(rr_non_radio_aware_completion_rate)
        # print("MR RA")
        # print(mr_radio_aware_completion_rate)
        # print("MR NONE")
        # print(mr_non_radio_aware_completion_rate)
        # print("RANDOM RA")
        # print(random_radio_aware_completion_rate)
        # print("RANDOM NONE")
        # print(random_non_radio_aware_completion_rate)

        # plt.plot(self.num_of_users, pf_radio_aware_latencies, label="PF-RA")
        # plt.plot(self.num_of_users, mr_radio_aware_latencies, label="MR-RA")
        # plt.plot(self.num_of_users, rr_radio_aware_latencies, label="RR-RA")
        # plt.plot(self.num_of_users, random_radio_aware_latencies, label="Random-RA")
        # plt.plot(self.num_of_users, pf_non_radio_aware_latencies, label="PF-RNA")
        # plt.plot(self.num_of_users, mr_non_radio_aware_latencies, label="MR-RNA")
        # plt.plot(self.num_of_users, rr_non_radio_aware_latencies, label="RR-RNA")
        # plt.plot(self.num_of_users, random_non_radio_aware_latencies, label="Random-RNA")
        plt.xlabel("Number of Users")
        # plt.ylabel("Average Task Processing Latency (ms)")
        plt.ylabel("On-Time Completion Rate of Tasks")
        plt.legend()
        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        plt.show()


class RadioAwareProcessingDesiredLatency50:

    def __init__(self):
        self.max_rate_radio_aware_files = []
        self.max_rate_non_radio_aware_files = []
        self.round_robin_radio_aware_files = []
        self.round_robin_non_radio_aware_files = []
        self.random_radio_aware_files = []
        self.random_non_radio_aware_files = []
        self.proportional_fair_radio_aware_files = []
        self.proportional_fair_non_radio_aware_files = []
        self.num_of_users = [300, 350, 400, 450, 500]

        radio_scheduling_algorithms = ["Proportional_Fair", "Random", "Round_Robin", "Max_Rate"]
        radio_aware_status = ["radio-aware", "None"]

        for i in self.num_of_users:
            for j in radio_aware_status:
                for k in radio_scheduling_algorithms:
                    if k == "Proportional_Fair":
                        if j == "radio-aware":
                            self.proportional_fair_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June5/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')
                        else:
                            self.proportional_fair_non_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June5/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')

                    if k == "Random":
                        if j == "radio-aware":
                            self.random_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June5/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')
                        else:
                            self.random_non_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June5/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')

                    if k == "Max_Rate":
                        if j == "radio-aware":
                            self.max_rate_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June5/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')
                        else:
                            self.max_rate_non_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June5/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')

                    if k == "Round_Robin":
                        if j == "radio-aware":
                            self.round_robin_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June5/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')
                        else:
                            self.round_robin_non_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June5/tti_100_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')

        print("RANDOM RADIO AWARE")
        print(self.random_radio_aware_files)

    def plot_TotalLatencyVsAlgorithm_desired_latency50(self):
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

        total_sent_packets = [i * 99 for i in self.num_of_users]
        print("TOTAL SENT PACKETS")
        print(total_sent_packets)

        for file in self.proportional_fair_radio_aware_files:
            data = pd.read_csv(file)
            pf_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            pf_radio_aware_completion_rate.append(len(data["Total Latency"] < 70))
        pf_radio_aware_completion_rate = np.divide(pf_radio_aware_completion_rate, total_sent_packets)

        for file in self.proportional_fair_non_radio_aware_files:
            data = pd.read_csv(file)
            pf_non_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            pf_non_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 70]))
        pf_non_radio_aware_completion_rate = np.divide(pf_non_radio_aware_completion_rate, total_sent_packets)

        for file in self.max_rate_radio_aware_files:
            data = pd.read_csv(file)
            mr_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            mr_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 70]))

        mr_radio_aware_completion_rate = np.divide(mr_radio_aware_completion_rate, total_sent_packets)

        for file in self.max_rate_non_radio_aware_files:
            data = pd.read_csv(file)
            mr_non_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            mr_non_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 70]))

        mr_non_radio_aware_completion_rate = np.divide(mr_non_radio_aware_completion_rate, total_sent_packets)

        for file in self.round_robin_radio_aware_files:
            data = pd.read_csv(file)
            rr_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            rr_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 70]))

        rr_radio_aware_completion_rate = np.divide(rr_radio_aware_completion_rate, total_sent_packets)

        for file in self.round_robin_non_radio_aware_files:
            data = pd.read_csv(file)
            rr_non_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            rr_non_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 70]))

        rr_non_radio_aware_completion_rate = np.divide(rr_non_radio_aware_completion_rate, total_sent_packets)

        for file in self.random_radio_aware_files:
            data = pd.read_csv(file)
            random_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            random_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 70]))
        random_radio_aware_completion_rate = np.divide(random_radio_aware_completion_rate, total_sent_packets)

        for file in self.random_non_radio_aware_files:
            data = pd.read_csv(file)
            random_non_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            random_non_radio_aware_completion_rate.append(len(data[data["Total Latency"] < 70]))
        random_non_radio_aware_completion_rate = np.divide(random_non_radio_aware_completion_rate, total_sent_packets)

        # print("Proportional Fair Radio Aware")
        # print(pf_radio_aware_latencies)
        # print("Max Rate Non Radio Aware")
        # print(mr_radio_aware_latencies)

        # plt.plot(self.num_of_users, random_radio_aware_completion_rate, label="Random-RA")#äü+ +üo
        # plt.plot(self.num_of_users, random_non_radio_aware_completion_rate, label="Random-RNA")
        # plt.plot(self.num_of_users, mr_radio_aware_completion_rate, label="MaxRate-RA")
        # plt.plot(self.num_of_users, mr_non_radio_aware_completion_rate, label="MaxRate-RNA")
        # plt.plot(self.num_of_users, rr_radio_aware_completion_rate, label="RoundRobin-RA")
        # plt.plot(self.num_of_users, rr_non_radio_aware_completion_rate, label="RoundRobin-RNA")
        # plt.plot(self.num_of_users, pf_radio_aware_completion_rate, label="ProportionallyFair-RA")
        # plt.plot(self.num_of_users, pf_non_radio_aware_completion_rate, label="ProportionallyFair-RNA")
        #
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
        # plt.plot(self.num_of_users, random_radio_aware_latencies, label="Random-RA")
        # plt.plot(self.num_of_users, pf_non_radio_aware_latencies, label="PF-RNA")
        # plt.plot(self.num_of_users, mr_non_radio_aware_latencies, label="MR-RNA")
        # plt.plot(self.num_of_users, rr_non_radio_aware_latencies, label="RR-RNA")
        # plt.plot(self.num_of_users, random_non_radio_aware_latencies, label="Random-RNA")
        plt.xlabel("Number of Users")
        # plt.ylabel("Average Task Processing Latency (ms)")
        plt.ylabel("On-Time Completion Rate of Tasks")
        plt.legend()
        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        plt.show()


class June6Plots:

    def __init__(self):
        self.max_rate_radio_aware_files = []
        self.max_rate_non_radio_aware_files = []
        self.round_robin_radio_aware_files = []
        self.round_robin_non_radio_aware_files = []
        self.random_radio_aware_files = []
        self.random_non_radio_aware_files = []
        self.proportional_fair_radio_aware_files = []
        self.proportional_fair_non_radio_aware_files = []
        self.num_of_users = [25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350]

        radio_scheduling_algorithms = ["Proportional_Fair", "Random", "Round_Robin", "Max_Rate"]
        radio_aware_status = ["radio-aware", "None"]

        for i in self.num_of_users:
            for j in radio_aware_status:
                for k in radio_scheduling_algorithms:
                    if k == "Proportional_Fair":
                        if j == "radio-aware":
                            self.proportional_fair_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June6-2/tti_10_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')
                        else:
                            self.proportional_fair_non_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June6-2/tti_10_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')

                    if k == "Random":
                        if j == "radio-aware":
                            self.random_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June6-2/tti_10_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')
                        else:
                            self.random_non_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June6-2/tti_10_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')

                    if k == "Max_Rate":
                        if j == "radio-aware":
                            self.max_rate_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June6-2/tti_10_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')
                        else:
                            self.max_rate_non_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June6-2/tti_10_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')

                    if k == "Round_Robin":
                        if j == "radio-aware":
                            self.round_robin_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June6-2/tti_10_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')
                        else:
                            self.round_robin_non_radio_aware_files.append(
                                os.pardir + '/results/sigcomm/June6-2/tti_10_num_of_user_' +
                                str(i) + '_' + str(j) + '_' + str(k) + '.csv')

    def plot_TotalLatencyVsAlgorithm_desired_latency50(self):
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

        for file in self.round_robin_radio_aware_files:
            data = pd.read_csv(file)
            rr_radio_aware_latencies.append(np.mean(data["Total Latency"]))
            rr_radio_aware_completion_rate.append(len(data[data["Total Latency"] < desired_latency]))

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
        plt.plot(self.num_of_users, mr_radio_aware_completion_rate, label="MaxRate-RA", marker="o")
        plt.plot(self.num_of_users, mr_non_radio_aware_completion_rate, label="MaxRate-RNA", marker="v")
        plt.plot(self.num_of_users, rr_radio_aware_completion_rate, label="RoundRobin-RA", marker="d")
        plt.plot(self.num_of_users, rr_non_radio_aware_completion_rate, label="RoundRobin-RNA", marker="D")
        plt.plot(self.num_of_users, pf_radio_aware_completion_rate, label="ProportionallyFair-RA", marker="s")
        plt.plot(self.num_of_users, pf_non_radio_aware_completion_rate, label="ProportionallyFair-RNA", marker="P")
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
        plt.xlabel("Number of Users")
        # plt.ylabel("Average Task Processing Latency (ms)")
        plt.ylabel("On-Time Completion Rate of Tasks")
        plt.legend(fontsize="10")
        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        # plt.show()
        tikzplotlib.save("completion_rate_vs_num_users.tex")


class NumberOfInstancesVsTaskCompletionRate:
    def __init__(self):
        self.num_of_instances_files = []
        self.num_of_users = [10, 11, 12, 13]

        for i in self.num_of_users:
            self.num_of_instances_files.append(
                os.pardir + '/results/sigcomm/June7/tti_10_num_of_instances_' +
                str(i) + '.csv')

    def plot_graph(self):
        desired_latency = 100
        task_completion_rates = []
        num_of_packets = 998 * 150
        for file in self.num_of_instances_files:
            data = pd.read_csv(file)
            task_completion_rates.append(len(data[data["Total Latency"] < desired_latency]) / num_of_packets)

        plt.xlabel("Number of Instances per Server")
        # plt.ylabel("Average Task Processing Latency (ms)")
        plt.ylabel("On-Time Completion Rate of Tasks")
        # plt.legend(fontsize="10")
        plt.plot(self.num_of_users, task_completion_rates, marker="o")
        fig = plt.gcf()
        # print(task_completion_rates)
        plt.show()
        # tikzplotlib.save("completion_rate_vs_num_instances.tex")


class June8Plots:
    def __init__(self):
        self.num_of_users = [50, 100, 150, 200, 250, 300]
        self.radio_scheduling_algo = ["Proportional_Fair", "Max_Rate", "Round_Robin"]
        self.edge_scheduling = ["radio-aware", "None"]
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
            for j in self.edge_scheduling:
                for k in self.radio_scheduling_algo:
                    for l in self.seeds:
                        if k == "Proportional_Fair":
                            if j == "radio-aware":
                                self.proportional_fair_radio_aware_files[i].append(
                                    os.pardir + '/results/sigcomm/June8/tti_10_num_of_user_' +
                                    str(i) + '_' + str(j) + '_' + str(k) + '_' + str(l) + '.csv')
                            else:
                                self.proportional_fair_non_radio_aware_files[i].append(
                                    os.pardir + '/results/sigcomm/June8/tti_10_num_of_user_' +
                                    str(i) + '_' + str(j) + '_' + str(k) + '_' + str(l) + '.csv')

                        if k == "Max_Rate":
                            if j == "radio-aware":
                                self.max_rate_radio_aware_files[i].append(
                                    os.pardir + '/results/sigcomm/June8/tti_10_num_of_user_' +
                                    str(i) + '_' + str(j) + '_' + str(k) + '_' + str(l) + '.csv')
                            else:
                                self.max_rate_non_radio_aware_files[i].append(
                                    os.pardir + '/results/sigcomm/June8/tti_10_num_of_user_' +
                                    str(i) + '_' + str(j) + '_' + str(k) + '_' + str(l) + '.csv')

                        if k == "Round_Robin":
                            if j == "radio-aware":
                                self.round_robin_radio_aware_files[i].append(
                                    os.pardir + '/results/sigcomm/June8/tti_10_num_of_user_' +
                                    str(i) + '_' + str(j) + '_' + str(k) + '_' + str(l) + '.csv')
                            else:
                                self.round_robin_non_radio_aware_files[i].append(
                                    os.pardir + '/results/sigcomm/June8/tti_10_num_of_user_' +
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
            num_of_packets = 498 * num_user
            for file in self.max_rate_radio_aware_files[num_user]:
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
        # data_groups = [data_group_5, data_group_6]

        print(mr_radio_aware_completion_rate)
        print(mr_non_radio_aware_completion_rate)
        print(pf_radio_aware_completion_rate)
        print(pf_non_radio_aware_completion_rate)
        print(rr_radio_aware_completion_rate)
        print(rr_non_radio_aware_completion_rate)
        print("\n")
        print(mr_radio_aware_completion_rate_avg)
        print(mr_non_radio_aware_completion_rate_avg)
        print(pf_radio_aware_completion_rate_avg)
        print(pf_non_radio_aware_completion_rate_avg)
        print(rr_radio_aware_completion_rate_avg)
        print(rr_non_radio_aware_completion_rate_avg)

        # # --- Labels for your data:
        x_values = ['50', '100', '150', "200", "250", "300"]
        width = 5 / len(x_values)
        xlocations = [x * ((1 + len(data_groups)) * width) for x in range(len(data_group_1))]
        colors = ["blue", "lightblue", "green", "lightgreen", "red", "pink"]
        # colors = ["red", "pink"]
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
        # labels = ["RR-RASQ", "RR-FCFS"]

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

            # for i, label in enumerate(labels):
            #     ax.annotate(label, (i + 1, np.max(dg[i])), xytext=(10, 10), textcoords='offset points', ha='center')

            box_plots.append(bp)
            for m in bp['medians']:
                [[x0, x1], [y0, y1]] = m.get_data()
                X.append(np.mean((x0, x1)))
                Y.append(np.mean((y0, y1)))

            plt.plot(X, Y, color=c)

        ax.legend([element["boxes"][0] for element in box_plots],
                  [labels[idx] for idx, _ in enumerate(data_groups)], bbox_to_anchor=(0.5, 1.08),
                  fontsize=fontsize - 10, ncol=3, loc='center')

        ax.set_xticks(xlocations)
        ax.set_xticklabels(x_values, rotation=0, fontsize=fontsize)
        ax.tick_params(axis='both', which='major', labelsize=fontsize)
        plt.rc('ytick', labelsize=fontsize)
        fig = plt.gcf()
        fig.set_size_inches(18, 10)

        # plt.rcParams['font.size'] = 25
        # plt.show()

        # plt.plot(self.num_of_users, random_radio_aware_completion_rate, label="Random-RA")
        # plt.plot(self.num_of_users, random_non_radio_aware_completion_rate, label="Random-RNA")
        # plt.plot(self.num_of_users, mr_radio_aware_completion_rate_avg.values(), label="MaxRate-RA", marker="o")
        # plt.plot(self.num_of_users, mr_non_radio_aware_completion_rate_avg.values(), label="MaxRate-RNA", marker="v")
        # plt.plot(self.num_of_users, rr_radio_aware_completion_rate_avg.values(), label="RoundRobin-RA", marker="d")
        # plt.plot(self.num_of_users, rr_non_radio_aware_completion_rate_avg.values(), label="RoundRobin-RNA", marker="D")
        # plt.plot(self.num_of_users, pf_radio_aware_completion_rate_avg.values(), label="ProportionallyFair-RA", marker="s")
        # plt.plot(self.num_of_users, pf_non_radio_aware_completion_rate_avg.values(), label="ProportionallyFair-RNA", marker="P")
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
        # ax.legend(fontsize=fontsize)
        # fig = plt.gcf()
        # fig.set_size_inches(18, 10)
        # # plt.show()
        # tikzplotlib.save("completion_rate_vs_num_users.tex")

        # plt.xlabel("Number of Instances per Server")
        # plt.ylabel("Average Task Processing Latency (ms)")
        # plt.ylabel("On-Time Completion Rate of Tasks")
        # plt.legend(fontsize="10")
        # plt.plot(self.num_of_users, task_completion_rates, marker="o")
        fig = plt.gcf()
        # plt.legend()
        fig.savefig('completion_rate_vs_num_of_users_boxplot_rectangle.pdf', format='pdf', dpi=800)
        # plt.show()
        # tikzplotlib.save("completion_rate_vs_num_users_boxplot_rectangle.tex")


# June6Plots().plot_TotalLatencyVsAlgorithm_desired_latency100()

# RadioAwareProcessingDesiredLatency50().plot_TotalLatencyVsAlgorithm_desired_latency100()

# NumberOfInstancesVsTaskCompletionRate().plot_graph()

# June8Plots().plot_graph()

class June9InstancePlots:
    def __init__(self):
        self.num_of_instances = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        self.num_users = [50, 150]
        self.edge_scheduling = ["radio-aware", "None"]
        self.seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.radio_scheduling = ["Round_Robin"]

        self.rr_radio_aware_files = {}
        self.rr_none_files = {}
        self.rr_radio_aware_completion_rate = {}
        self.rr_radio_aware_completion_rate_avg = {}
        self.rr_none_completion_rate = {}
        self.rr_none_completion_rate_avg = {}

        for num_user in self.num_users:
            self.rr_radio_aware_files[num_user] = {}
            self.rr_none_files[num_user] = {}
            for num_instance in self.num_of_instances:
                self.rr_radio_aware_files[num_user][num_instance] = []
                self.rr_none_files[num_user][num_instance] = []

        for num_user in self.num_users:
            for i in self.num_of_instances:
                for j in self.edge_scheduling:
                    for k in self.radio_scheduling:
                        for l in self.seeds:
                            if k == "Round_Robin":
                                if j == "radio-aware":
                                    self.rr_radio_aware_files[num_user][i].append(
                                        os.pardir + '/results/sigcomm/June9-campaign3/tti_10_num_of_user_' + str(
                                            num_user) + '_' +
                                        str(j) + '_' + str(k) + '_' + str(l) + '_' + str(i) + '.csv')
                                else:
                                    self.rr_none_files[num_user][i].append(
                                        os.pardir + '/results/sigcomm/June9-campaign3/tti_10_num_of_user_' + str(
                                            num_user)
                                        + '_' + str(j) + '_' + str(k) + '_' + str(l) + '_' + str(i) + '.csv')

    def plot_graph(self):
        # print(self.rr_radio_aware_files)
        # print(self.rr_none_files)
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
                num_of_packets = 498 * num_user
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
        # data_groups = [data_group_1, data_group_2]

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

            # for i, label in enumerate(labels):
            #     ax.annotate(label, (i + 1, np.max(dg[i])), xytext=(10, 10), textcoords='offset points', ha='center')

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
        fig.savefig('completion_rate_vs_num_of_instances_boxplot_rectangle.pdf', format='pdf', dpi=800)
        # plt.show()
        # print("RADIO AWARE")
        print(self.rr_radio_aware_completion_rate)
        print(self.rr_none_completion_rate)
        print(self.rr_radio_aware_completion_rate_avg)
        print(self.rr_none_completion_rate_avg)


June8Plots().plot_graph()
# June9InstancePlots().plot_graph()
