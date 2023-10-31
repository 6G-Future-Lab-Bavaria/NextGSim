import csv
import logging
import os

import simpy
import threading

import networkx as nx
from pathlib import Path

from edge.network.NetworkTopology import NetworkTopology
from edge.network.Routing import get_path
from edge.network.Link import add_link
from Server import RanData, Server
from edge.entities.Entity import get_entity_by_id, get_edge_servers, get_cpus, get_entity_list, \
    ENTITY_LIST, getDeviceID_to_EntityID_Map, getBaseStationID_to_EntityID_Map, map_entity_id_to_device_id, set_sim
from edge.application.Microservice import getServiceName_to_ProcessID_Map, getProcessID_to_NodeID_Map, \
    getProcessID_to_Service_Map
from edge.entities.EdgeServer import EdgeServer
from edge.application.Application import get_AppName_to_AppInst_Map
from edge.entities.orchestrator.EdgeOrchestrator import EdgeOrchestrator
from edge.util.DistributionFunctions import DeterministicDistribution, DeterministicDistributionWithStartingTime
from edge.application_examples.RANApp import RANApplication
from SimParams import SimParams

BACKHAUL_DEVICES = ['EdgeServer', 'Gateway', 'Vm', 'BaseStation']
EPSILON = 0.001


def get_sim():
    return MECSimulation.INSTANCE


class MECSimulation(threading.Thread):
    """

    This class contains the discrete-event ran_simulation environment that is responsible for orchestration of the
    ran_simulation.

        Args:
           logger (Logger) : Logger settings for the ran_simulation log.
    """

    INSTANCE = None

    def __init__(self, main_simulation, logger=None):
        threading.Thread.__init__(self)
        if MECSimulation.INSTANCE is not None:
            pass
        else:
            MECSimulation.INSTANCE = self

            set_sim(self)
            self.stop = False
            self.main_simulation = main_simulation
            self.env = simpy.Environment()
            self.network_message_queue = simpy.Store(self.env)
            self.topology = NetworkTopology()
            self.sim_params = SimParams()
            self.logger = logger or logging.getLogger(__name__)
            self.reporting_distribution = DeterministicDistributionWithStartingTime(starting_time=1,
                                                                                    period=self.sim_params.TTI_duration / 2)

            self.mec_csv_distribution = DeterministicDistribution(name="RAN.csv Granularity",
                                                                  period=self.sim_params.TTI_duration + EPSILON)
            self.messages_in_the_backhaul = []
            self.next_reporting_time = 0
            self.next_computing_time = 0
            self.ran_server = Server()
            # nx.draw(self.topology.G)

    def __new__(cls, *args, **kwargs):
        if MECSimulation.INSTANCE:
            return MECSimulation.INSTANCE
        else:
            inst = object.__new__(cls)
            return inst

    def run(self, test_initial_deployment=False):
        """

        Starts the ran_simulation.

        Args:
            test_initial_deployment (bool): Test initial deployment

        """
        # self.topology.load(get_entity_list(), get_link_list())
        self.initialize_MEC_environment()
        self.ran_server.create_socket()
        self.env.process(self.ran_server.receive_and_send_files(self))
        self.__compute_process()
        self.env.process(self.__network_process())
        self.env.process(self.__report_backhaul_status())
        self.logger.debug('Starting Simulation')
        self.env.run(1000)  # fixme: hardcoded running time

    def DeviceID_to_EntityID_Map(self):
        return getDeviceID_to_EntityID_Map()

    def BaseStationID_to_EntityID_Map(self):
        return getBaseStationID_to_EntityID_Map()

    def initialize_MEC_environment(self):  # fixme: this is a dummy implementation, needs to be changed
        orchestrator = EdgeOrchestrator()
        for es in self.main_simulation.edge_servers_per_scenario:
            es.bind_to_orchestrator(orchestrator)
            for base_station in self.main_simulation.gNBs_per_scenario:
                add_link(es, base_station)
                add_link(base_station, es)

        for device in self.main_simulation.devices_per_scenario:
            device.bind_to_orchestrator(orchestrator)
            if self.main_simulation.sim_params.application == "RANApplication":
                device.deploy_app(RANApplication(device.ID))

        orchestrator.place_services()

        # self.topology.show_topology()

    def __transfer_message(self, message, latency):
        """
        Simulates the transfer behavior of a message on a link
        """
        yield self.env.timeout(latency)
        self.network_message_queue.put(message)

    def __compute_process(self):
        self.logger.debug("Starting Compute Processes")
        for cpu in get_cpus():
            cpu.start_processing(self)

    def __network_process(self):
        self.logger.debug("Starting Network Processes")
        self.last_activity = {}

        while not self.stop:
            message = yield self.network_message_queue.get()

            if get_entity_by_id(
                    message.receiver_id).__class__.__name__ in BACKHAUL_DEVICES and message not in self.messages_in_the_backhaul:
                self.messages_in_the_backhaul.append(message)
                get_AppName_to_AppInst_Map()[message.app_name].entry_time_to_backhaul = self.env.now

            if message.sender_id == message.receiver_id:
                self.logger.debug(
                    "(App:%s #Process:%i #%s) Received Message : %s at time T : %f - (Receiver: %s), Path : %s \n "
                    % (message.app_name, message.destination_service_id, message.destination_service, message.name,
                       self.env.now, message.receiver_id, message.path))
                getProcessID_to_Service_Map()[message.destination_service_id].insert_message(message)
                message.location = message.receiver_id

            else:
                self.logger.debug(
                    "(App:%s #Process:%i #%s) Sending Message : %s at time T : %f - (Sender: %s, Receiver: %s), Path : %s \n "
                    % (message.app_name, message.source_service_id, message.source_service, message.name,
                       self.env.now, message.sender_id, message.receiver_id, message.path))

                link = (message.sender_id, message.receiver_id)
                message.is_scheduled_by_ran = False
                message.location = message.receiver_id
                message.sender_id = message.receiver_id
                if message.receiver_id != message.path[-1]:
                    message.receiver_id = message.path[message.path.index(message.receiver_id) + 1]

                """
                Computing output_message latency
                """
                tmp_edge = self.topology.get_edge(link)
                if not tmp_edge:
                    self.network_message_queue.put(message)
                else:
                    transmit = message.bytes / (tmp_edge["bandwidth"] * 1000000.0)  # MBITS!
                    propagation = tmp_edge["latency"]
                    link_latency = transmit + propagation
                    self.env.process(self.__transfer_message(message, link_latency))

    # def get_process_id(self):
    #     """
    #     A process has a unique identifier
    #     """
    #     self.process_id_counter += 1
    #     return self.process_id_counter

    def send_message(self, message):
        """
        Any exchange of source messages between all_services is done in this function and metrics are updated when the output_message
        arrives at the receiver.
        """

        path = get_path(self.topology, message.sender_id,
                        message.destination_id)
        message.path = path
        message.location = message.sender_id
        if len(message.path) == 1:
            message.receiver_id = message.path[0]
        else:
            message.receiver_id = message.path[message.path.index(message.sender_id) + 1]
        self.network_message_queue.put(message)

    def __report_backhaul_status(self):
        """
            Reports information about the messages in backhaul such as : process entity_id of the process they belong, ID of the device they serve, ID of the entity_id that the output_message is being or going to be processed,
            completion percentage of the processing, latency experienced by the app in the backhaul, and a boolean value indicating if the output_message is waiting to be scheduled by a base station or not ( if this value is None, the output_message is not meant
            to be sent by a base station ).

            It can report them as a log, or if enabled, it can output them as a .csv file to be used by the RAN simulator.

            e.g :

                Messages in the Backhaul at time : 879

                Sensor_1_Data_APP4

                Percentage : 53.54330708661415

                Location : 12 - server

                Processed_Sensor_Data_APP4

                Percentage : 0

                Location : 8 - base_station

                Processed_Sensor_Data_APP4

                Percentage : 0

                Location : 3 - base_station

                ['Process ID', 21, 31, 25]

                ['User ID', 21, 30, 24]

                ['Server ID', 12, 30, 24]

                ['Processing Percentage', 53.54330708661415, 0, 0]

                ['Latency', None, 12.800000004062326, 12.800000008062284]

                ['Waiting to be Scheduled', False, True, True]

            """
        while not self.stop:
            next_report_time = self.reporting_distribution.next()
            current_reporting_time = round(self.env.now, 2)
            yield self.env.timeout(next_report_time)
            messages_to_remove = []
            data_to_csv = []
            process_ids = ["Process ID"]
            process_names = ["Process Name"]
            sequence_numbers = ["Sequence Number"]
            user_ids = ["User ID"]
            server_ids = ["Computing Node ID"]
            processing_percentages = ["Processing Percentage"]
            latencies = ["Latency(ms)"]
            scheduling_status = ["Is Scheduled?"]
            packet_data_sizes = ["Packet Data Sizes(bits)"]

            reporting_time = ["Reporting Time(ms)", current_reporting_time]
            edge_server_list = ["Edge Server IDs"]
            edge_servers_available_cpu_shares = ["Available CPU"]
            edge_servers_available_gpus = ["Available GPU Cores"]
            edge_servers_available_storage = ["Available Storage"]

            edge_servers = get_edge_servers()

            for message in self.messages_in_the_backhaul:
                if message.remaining_instructions_to_compute == 0:
                    messages_to_remove.append(message)
                    continue
                else:
                    location_entity = get_entity_by_id(message.location)
                    if location_entity.__class__.__name__ not in BACKHAUL_DEVICES:
                        messages_to_remove.append(message)
                        continue
                    else:
                        app = get_AppName_to_AppInst_Map()[message.app_name]
                        process_ids.append(message.destination_service_id)
                        process_names.append(message.destination_service)
                        sequence_numbers.append(message.sequence_number)
                        user_ids.append(map_entity_id_to_device_id(message.source_id))
                        server_ids.append(message.destination_id)
                        reporting_time.append(current_reporting_time)

                        if location_entity.__class__.__name__ == "BaseStation":
                            processing_percentages.append("N/A")
                            scheduling_status.append(message.is_scheduled_by_ran)
                            packet_data_sizes.append(message.bytes * 8)
                        else:
                            tmp_processing_percentage = round((message.instructions -
                                                               message.remaining_instructions_to_compute) /
                                                              message.instructions * 100, 2)
                            processing_percentages.append(tmp_processing_percentage)
                            scheduling_status.append("N/A")
                            packet_data_sizes.append(message.bytes)
                        if (app.exit_time_from_backhaul - app.entry_time_to_backhaul) > 0:
                            latency = round(app.exit_time_from_backhaul - app.entry_time_to_backhaul, 2)
                            latencies.append(latency)
                        else:
                            latencies.append(round(app.ul_latency + self.env.now - app.entry_time_to_backhaul, 2))

            for msg in messages_to_remove:
                self.messages_in_the_backhaul.remove(msg)

            for server in edge_servers:
                edge_server_list.append(server.entity_id)
                edge_servers_available_cpu_shares.append(round(server.available_cpu_share, 3))
                edge_servers_available_storage.append(server.storage)

            self.logger.debug(edge_server_list)
            self.logger.debug(edge_servers_available_cpu_shares)
            self.logger.debug(edge_servers_available_storage)
            self.logger.debug(process_ids)
            self.logger.debug(process_names)
            self.logger.debug(sequence_numbers)
            self.logger.debug(user_ids)
            self.logger.debug(server_ids)
            self.logger.debug(processing_percentages)
            self.logger.debug(latencies)
            self.logger.debug(scheduling_status)
            self.logger.debug(packet_data_sizes)
            self.logger.debug(reporting_time)
            print("\n")

            if len(edge_server_list) < len(process_ids):
                for i in range(len(process_ids) - len(edge_server_list)):
                    edge_server_list.append(None)
                    edge_servers_available_cpu_shares.append(None)
                    edge_servers_available_gpus.append(None)
                    edge_servers_available_storage.append(None)

            data_to_csv.append(edge_server_list)
            data_to_csv.append(edge_servers_available_cpu_shares)
            data_to_csv.append(edge_servers_available_gpus)
            data_to_csv.append(edge_servers_available_storage)
            data_to_csv.append(process_ids)
            data_to_csv.append(process_names)
            data_to_csv.append(user_ids)
            data_to_csv.append(server_ids)
            data_to_csv.append(processing_percentages)
            data_to_csv.append(latencies)
            data_to_csv.append(scheduling_status)
            data_to_csv.append(packet_data_sizes)
            data_to_csv.append(reporting_time)

            data_to_csv = zip(*data_to_csv)
            with open('../MEC_Server.csv', 'w') as file:
                writer = csv.writer(file)
                writer.writerows(data_to_csv)
