import numpy as np
from channel.ChannelModel import ChannelUMiUMa, ChannelIndoor
from channel.ChannelModelInF import ChannelModelInF
from runtime.InitialSetUp import InitialSetUpIndoor, InitialSetUpOutdoor, InitialSetUpIndoorFactory
from runtime.RunTimeSetUp import RunTime
from SD_RAN.Scheduler import RadioResourceSchedulers
from gnb.ThroughputCalculation import ThroughputCalculation
from runtime.data_classes import MeasurementParams
from runtime.EventChain import EventChain
from device.TrafficGenerator import TrafficGenerator
from device.ManageDevices import ManageDevices
import plotting.ScenarioVisualization
from runtime.utilities import block_print, enable_print, utility
import time
import threading
import matplotlib.pyplot as plt
import os
import csv
import pandas as pd

np.set_printoptions(threshold=np.inf)
utility.format_figure()
main_path = os.path.dirname(os.path.abspath('Simulation.py'))
#matplotlib.use('macosx')


# utility.set_path()


class RANSimulation(threading.Thread):
    def __init__(self, main_simulation):
        threading.Thread.__init__(self)
        self.main_simulation = main_simulation
        self.sim_params = main_simulation.sim_params
        # self.applications = main_simulation.applications
        self.env = self.main_simulation.env
        ' --------------------- For activation of devices and generation of device packets ---------------'
        self.event_chain = EventChain()
        self.traffic_generator = TrafficGenerator(self)
        self.running = RunTime(self)
        self.manage_devices = None
        self.expected_num_device_arrivals = None
        '-------Important for keeping tract of the number of gNBs and devices in our scenario--------------'
        # TODO: Turn the id and objects into dictionary. Easier to work with
        self.devices_per_scenario = main_simulation.devices_per_scenario  # what is the difference btw devices and devices_ID?
        self.devices_per_scenario_ID = list(range(0, len(self.devices_per_scenario)))
        self.user_coordinates = main_simulation.user_coordinates
        self.all_active_devices_ID = []
        self.gNBs_per_scenario_ID = list(range(0, self.sim_params.num_cells))
        self.gNBs_per_scenario = main_simulation.gNBs_per_scenario
        '--------------------- Generation of the RAN channel ---------------------------------------------'
        self.channel = None
        self.blockage_info = None
        # Generation of the scheduler at gNB side
        self.ctrl_scheduler = None
        self.throughput_calc = None
        # Gneration of the mobility
        # Generation of the results and plotting
        self.visualization = plotting.ScenarioVisualization.scenario_visualization(self)
        self.plot_allocation_flag = False
        self.setup = main_simulation.setup
        self.seed = None
        self.TTI = None
        self.throughput_history = []
        self.num_users = self.sim_params.scenario.max_num_devices_per_scenario
        self.num_PRBs = self.sim_params.scenario.num_PRBs
        self.history = np.ones(self.num_users)
        self.result_path = os.path.join(main_path, '../results')
        self.latency_writer = None
        self._stop_event = threading.Event()
        self.initialize_RANenvironment()

    def run(self):
        self.env.process(self.radio_resource_allocation())

    def initialize_RANenvironment(self):
        print(f"Simulating time = {self.sim_params.num_TTI / 10 ** 3} s = {self.sim_params.num_TTI} TTIs")
        print(f"[Environment] {self.sim_params.scenario.scenario} scenario")
        # TODO: check this line if needed
        self.sim_params.scenario.print_sim_params()
        self.set_channel()
        self.throughput_calc = ThroughputCalculation(self)
        # self.manage_devices = ManageDevices(self)
        # self.distance_2d =self.manage_devices.select_cell()  # initial association of users to gNBs in the idle state
        self.manage_devices = ManageDevices(self)
        self.distance_2d = self.manage_devices.select_cell()
        # self.expected_num_device_arrivals = self.traffic_generator.traffic_per_cell_generation()


    def radio_resource_allocation(self):
        """ We run the ran_simulation for a predefined period of time, where first we set up the static environment and
        afterwards deploy the dynamics of the users, related to the mobility and the protocols they follow.
        Every predefined scheduling slot the devices have the SNR information related to the channel condition and
        perform UL scheduling depending on the choosen scheme in the simulator.
        The simulator will be extended with the deployment of MEC servers that can be associated to only one or to
        multiple base stations.
        This function simulates the procedure described above for the specified running time of the simulator.
        """

        enable_print()
        t1 = time.time()
        if self.sim_params.visualise_scenario:
            self.visualization.visualize(predefined=self.sim_params.predefined_gNB_coord)
            plt.ion()
            plt.show()
        if self.sim_params.store_latency:
            file_path = os.path.join(self.result_path, self.sim_params.scheduler_type + '_latency.csv')
            data_file = open(file_path, 'a', newline='')
            self.latency_writer = csv.writer(data_file, delimiter=',')

        while not self.main_simulation.stop:
            for i in range(int(self.sim_params.num_TTI / self.sim_params.TTI_duration)):
                next_tti = self.main_simulation.tti_dist.next()
                self.set_at_tti(i)
                self.print_tti(t1)

                if self.TTI % MeasurementParams.channel_measurement_periodicity == 0:
                    # TODO: commented the SINR and RSRP and stored just SINR
                    # self.channel.calculate_final_SINR_RSRP()
                    # print(str("[Simulation] TTI= " + str(self.TTI)) + "--------------------------------------------------")
                    # distance = self.manage_devices.calc_distance_users_gnbs_2d()
                    '--------------------- Generating tasks ------------------------------------------------------'
                    user_packet_data, user_packet_cycles, user_packet_delay = self.running.gen_user_task()
                    '-------------------- Obtaining channel quality -----------------------------------------------'
                    channel_quality = self.channel.calc_SNR()
                    '--------------------- Scheduling Radio Resource Blocks (PRBs) --------------------------------'
                    if self.sim_params.schedule_PRBs:
                        PRB_scheduler = RadioResourceSchedulers(self, channel_quality=channel_quality,
                                                                scheduler_type=self.sim_params.scheduler_type)
                        if self.sim_params.scheduler_type == 'Round_Robin':
                            PRB_assignment_matrix, BS_per_UE = PRB_scheduler.schedule_round_robin()
                            user_PRB_throughput, user_throughput = PRB_scheduler.calc_achieved_throughput()
                            self.throughput_history.append(user_throughput)
                        elif self.sim_params.scheduler_type == 'Random':
                            PRB_assignment_matrix, BS_per_UE = PRB_scheduler.schedule_random()
                            user_PRB_throughput, user_throughput = PRB_scheduler.calc_achieved_throughput()
                            self.throughput_history.append(user_throughput)
                        elif self.sim_params.scheduler_type == 'Proportional_Fair' or self.sim_params.scheduler_type == 'Max_Rate':
                            if self.throughput_history:
                                history_last = np.mean(self.throughput_history, axis=0)
                            else:
                                history_last = np.zeros(self.num_users)
                            PRB_assignment_matrix, BS_per_UE = PRB_scheduler.schedule_proportional_fair(self.history)
                            user_PRB_throughput, user_throughput = PRB_scheduler.calc_achieved_throughput()
                            T = self.TTI + 1
                            for user in range(self.num_users):
                                self.history[user] = (1 - 1 / T) * history_last[user] + (1 / (T)) * user_throughput[user]
                            self.throughput_history.append(user_throughput)
                    '------------------------ Transmission delay -------------------------------------------------'
                    transmission_latency = np.divide(user_packet_data, user_throughput) * 1000
                    transmission_latency[transmission_latency == np.inf] = None
                    if self.sim_params.store_latency:
                        self.latency_writer.writerow(transmission_latency)
                    # # # writing to csv file to transmit RAN information to MEC
                    # if self.sim_params.include_MEC:
                    self.main_simulation.ran_data = self.running.write_RAN_to_DF(BS_per_UE, user_throughput,
                                                                                 transmission_latency, user_packet_data,
                                                                                 user_packet_cycles, user_packet_delay)
                    if self.sim_params.visualise_scenario:
                        self.visualization.visualize_UEs(RRC_states=self.sim_params.traffic_model,
                                                         connection=self.sim_params.show_connections)
                    for user in self.devices_per_scenario:
                        if self.TTI % MeasurementParams.update_ue_position_gap == 0:
                            user.update_location()
                    for gNB in self.gNBs_per_scenario:
                        gNB.reset_statistics()
                    self.distance_2d = self.manage_devices.select_cell()

                yield self.env.timeout(next_tti)

                # if self.sim_params.traffic_model:
                #     self.event_chain.remove_TTI_events(self.TTI)
                #     self.upd_buffers()

        '---------------------------------- Storing data ----------------------------------------------------'
        if self.sim_params.store_throughput:
            df = pd.DataFrame(self.throughput_history)
            df.to_csv(self.sim_params.scheduler_type + '.csv')

        enable_print()
        t2 = time.time()
        print(f"Finished. Simulation of {self.sim_params.num_TTI} TTIs took {round((t2 - t1) / 60, 1)} min.")

        self.delete_objects()

        # self.stop_thread()
        return

    def stop_thread(self):
        self._stop_event.set()

    def set_channel(self):
        if self.sim_params.scenario.scenario == "UMi":
            self.channel = ChannelUMiUMa(simulation=self, simparams=self.sim_params)
        elif self.sim_params.scenario.scenario == "Indoor":
            self.channel = ChannelIndoor(simulation=self, simparams=self.sim_params)
        elif self.sim_params.scenario.scenario == "Indoor factory":
            self.channel = ChannelModelInF(simulation=self, simparams=self.sim_params)
        else:
            raise NameError(f"No such scenario name {self.sim_params.scenario.scenario}")

    def delete_objects(self):
        del self.channel
        del self.setup.hexagon_maker
        del self.setup

    def sim_visualization(self):
        # if self.TTI == 0:  # or self.plot_allocation_flag:
        self.plot_allocation_flag = True


    def set_at_tti(self, i):
        self.seed = i
        self.TTI = i * self.sim_params.TTI_duration
        np.random.seed(self.seed)
        self.throughput_calc.data_rate = np.zeros((len(self.devices_per_scenario), len(self.gNBs_per_scenario)), float)

    def print_tti(self, t1):
        if self.TTI % 60000 == 0:
            t2 = time.time()
            enable_print()
            print(f"\nTTI = {self.TTI}. So far it took {round((t2 - t1) / 60, 1)} min")
            block_print(self.sim_params.disable_print)
        pass
