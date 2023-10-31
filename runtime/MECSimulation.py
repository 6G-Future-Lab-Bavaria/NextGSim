import logging

import simpy
import threading
import json
import os

import numpy as np
import pandas as pd


from edge.network.NetworkTopology import NetworkTopology
from edge.network.Routing import get_path
from edge.network.Link import add_bidirectional_link
from edge.entities.Entity import get_entity_by_id, get_edge_servers, get_cpus, getDeviceID_to_EntityID_Map, getBaseStationID_to_EntityID_Map, \
    map_entity_id_to_device_id, set_sim, get_routers, get_orchestrators, map_user_id_to_entity
from edge.application.Microservice import getProcessID_to_NodeID_Map, \
    getProcessID_to_Service_Map
from edge.entities.EdgeServer import EdgeServer
from edge.entities.Router import Router
from edge.entities.orchestrator.EdgeOrchestrator import EdgeOrchestrator
from edge.util.DistributionFunctions import DeterministicDistributionWithStartingTime
from edge.util.Util import closest_node

from definitions import CONFIGURATION_DIR

BACKHAUL_DEVICES = ['EdgeServer', 'Router', 'Vm', 'GnB']
EPSILON_SCALING = 0.001
SEQ_NUM = 0


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
        # threading.Thread.__init__(self)
        threading.Thread.__init__(self, target=self, args=(main_simulation.ran_data, main_simulation.mec_data,))
        self.mec_applications = None
        self.mec_links = None
        self.mec_entities = None
        if MECSimulation.INSTANCE is not None:
            pass
        else:
            MECSimulation.INSTANCE = self

            set_sim(self)
            self.stop = False
            self.main_simulation = main_simulation
            self.env = main_simulation.env
            self.network_message_queue = simpy.Store(self.env)
            self.topology = NetworkTopology()
            self.sim_params = main_simulation.sim_params
            self.simulation_time = self.sim_params.num_TTI
            self.config_file = self.sim_params.config_file
            self.logger = logger or logging.getLogger(__name__)
            self.logger.setLevel(self.main_simulation.logging_level)
            self.reporting_distribution = DeterministicDistributionWithStartingTime(starting_time=1, period=2)
            self.service_update_distribution = DeterministicDistributionWithStartingTime(
                name="Service Update Period",
                starting_time=self.sim_params.service_update_period,
                period=self.sim_params.service_update_period)
            self.messages_in_the_backhaul = []
            self.initialize_MEC_environment()

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
        self.env.process(self.receive_ran_data())
        self.__computing_process()
        self.env.process(self.__network_process())
        self.env.process(self.__report_backhaul_status())
        # self.env.process(self.__update_service_locations(self.sim_params.service_replacement_algorithm))
        self.logger.debug('Starting Simulation')
        # self.topology.show_topology()
        self.env.run(self.simulation_time)  # fixme: hardcoded running time
        return
        # self.topology.show_topology()

    def DeviceID_to_EntityID_Map(self):
        return getDeviceID_to_EntityID_Map()

    def BaseStationID_to_EntityID_Map(self):
        return getBaseStationID_to_EntityID_Map()

    def initialize_MEC_environment(self):
        if self.config_file:
            self.parse_ConfigFile_mec()

    def parse_ConfigFile_mec(self):
        with open(self.config_file, 'r') as myfile:
            data = myfile.read()

        config = json.loads(data)
        orchestrator = EdgeOrchestrator()
        routers = get_routers()

        self.mec_entities = config["mec_entities"]
        self.mec_links = config["mec_links"]
        self.mec_applications = config["mec_applications"]
        self.simulation_time = config["simulation_time"]
        self.sim_params.service_placement_algorithm = config["service_placement_algorithm"]
        self.sim_params.computing_period = config["computing_period"]
        entity_tags = {}

        for entity in self.mec_entities:
            if self.mec_entities[entity]["model"] == "edge_server":
                entity_tags[entity] = EdgeServer(location=self.mec_entities[entity]["location"])
                self.main_simulation.edge_servers_per_scenario.append(entity_tags[entity])
                entity_tags[entity].bind_to_orchestrator(orchestrator)
            if self.mec_entities[entity]["model"] == "router":
                entity_tags[entity] = Router(location=self.mec_entities[entity]["location"])
                self.main_simulation.routers_per_scenario.append(entity_tags[entity])

        for link in self.mec_links:
            src = str(self.mec_links[link]["src"])
            dst = str(self.mec_links[link]["dst"])
            if self.mec_links[link]["latency"]:
                latency = self.mec_links[link]["latency"]
            else:
                latency = None

            if self.mec_links[link]["bandwidth"]:
                bandwidth = self.mec_links[link]["bandwidth"]
            else:
                bandwidth = None

            add_bidirectional_link(entity_tags[src], entity_tags[dst], bandwidth=bandwidth, latency=latency)

        for base_station in self.main_simulation.gNBs_per_scenario:
            closest_router = closest_node(routers, base_station)
            add_bidirectional_link(closest_router, base_station)

        for device_type in self.mec_applications:
            if device_type == "edge_servers":
                for application_deployment in self.mec_applications[device_type]:
                    application_deployment_information = self.mec_applications[device_type][application_deployment]
                    print("ALL INFO")
                    print(self.mec_applications[device_type])
                    print("APP NAME")
                    print(application_deployment_information["application"])
                    for i in range(int(application_deployment_information["from"]) - 1,
                                   int(application_deployment_information["to"])):
                        self.main_simulation.edge_servers_per_scenario[i].bind_to_orchestrator(orchestrator)
                        self.main_simulation.edge_servers_per_scenario[i].deploy_app(
                            application_deployment_information["application"],
                            int(application_deployment_information["num_of_instances"]))
            if device_type == "mobile_devices":
                for application_deployment in self.mec_applications[device_type]:
                    application_deployment_information = self.mec_applications[device_type][application_deployment]
                    if application_deployment_information["to"] == "all":
                        application_deployment_information["to"] = len(self.main_simulation.devices_per_scenario)
                    for i in range(int(application_deployment_information["from"]) - 1,
                                   int(application_deployment_information["to"])):
                        self.main_simulation.devices_per_scenario[i].bind_to_orchestrator(orchestrator)
                        self.main_simulation.devices_per_scenario[i].deploy_app(
                            application_deployment_information["application"])

        orchestrator.place_services(self.sim_params.service_placement_algorithm)

    def __transfer_message(self, message, latency):
        """
        Simulates the transfer behavior of a message on a link
        """
        yield self.env.timeout(latency)
        self.network_message_queue.put(message)

    def __computing_process(self):
        self.logger.debug("Starting Compute Processes")
        for cpu in get_cpus():
            cpu.start_processing(self)

    def __network_process(self):
        self.logger.debug("Starting Network Processes")
        self.last_activity = {}

        while not self.stop:
            message = yield self.network_message_queue.get()

            if message.sender_id == message.receiver_id:
                if message.destination_service_id in getProcessID_to_Service_Map():
                    message.location = message.receiver_id
                    getProcessID_to_Service_Map()[message.destination_service_id].insert_message(message)
                    self.logger.debug(
                        "(App:%s #Process:%i #%s) Received Message : %s at time T : %f - (Receiver: %s), Path : %s \n "
                        % (message.app_name, message.destination_service_id, message.destination_service, message.name,
                           self.env.now, message.receiver_id, message.path))
                else:
                    pass


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
                    transmit = (message.bits * 8) / (tmp_edge["bandwidth"] * 1000000.0)  # Mbits
                    propagation = tmp_edge["latency"]
                    link_latency = transmit + propagation
                    self.env.process(self.__transfer_message(message, link_latency))

    def __update_service_locations(self, algorithm=None):
        while True:
            next_update_time = self.service_update_distribution.next()
            yield self.env.timeout(next_update_time)
            for orchestrator in get_orchestrators():
                # orchestrator.replace_services(algorithm=algorithm)
                orchestrator.perform_analytics()
                orchestrator.share_analytic_with_services()

    def send_message(self, message):
        """
        Any exchange of source messages between all services is done in this function and metrics are updated when the output_message
        arrives at the receiver.
        """
        path = get_path(self.topology, int(message.sender_id),
                        int(message.destination_id))

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
            completion percentage of the processing, latency experienced by the app_name in the backhaul, and a boolean value indicating if the output_message is waiting to be scheduled by a base station or not ( if this value is None, the output_message is not meant
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
            yield self.env.timeout(next_report_time)
            current_reporting_time = self.env.now
            messages_to_remove = []
            data_to_csv = []
            process_ids = []
            process_names = []
            sequence_numbers = []
            user_ids = []
            server_ids = []
            processing_percentages = []
            latencies = []
            scheduling_status = []
            packet_data_sizes = []
            reporting_time = [current_reporting_time]
            edge_server_list = []
            edge_servers_available_cpu_shares = []
            edge_servers_available_gpus = []
            edge_servers_available_storage = []

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
                        app = message.destination_service_instance.app
                        process_ids.append(message.destination_service_id)
                        process_names.append(message.destination_service)
                        sequence_numbers.append(message.sequence_number)
                        user_ids.append(map_entity_id_to_device_id(message.source_id))
                        server_ids.append(message.destination_id)
                        # reporting_time.append(current_reporting_time)

                        if location_entity.__class__.__name__ == "BaseStation":
                            processing_percentages.append("N/A")
                            scheduling_status.append(message.is_scheduled_by_ran)
                            packet_data_sizes.append(message.bits * 8)
                        else:
                            tmp_processing_percentage = round((message.instructions -
                                                               message.remaining_instructions_to_compute) /
                                                              message.instructions * 100, 2)
                            processing_percentages.append(tmp_processing_percentage)
                            scheduling_status.append("N/A")
                            packet_data_sizes.append(message.bits)
                            latencies.append(round(message.ul_latency + self.env.now - message.entry_time_to_backhaul, 2))

            for message in messages_to_remove:
                self.messages_in_the_backhaul.remove(message)

            edge_servers = get_edge_servers()

            for server in edge_servers:
                edge_server_list.append(server.entity_id)
                edge_servers_available_cpu_shares.append(round(server.available_cpu_share, 3))
                edge_servers_available_storage.append(server.memory)

            if len(edge_server_list) < len(process_ids):
                for i in range(len(process_ids) - len(edge_server_list)):
                    edge_server_list.append(None)
                    edge_servers_available_cpu_shares.append(None)
                    edge_servers_available_gpus.append(None)
                    edge_servers_available_storage.append(None)

            elif len(edge_server_list) > len(process_ids):
                for i in range(len(edge_server_list) - len(process_ids)):
                    process_ids.append(None)
                    process_names.append(None)
                    sequence_numbers.append(None)
                    user_ids.append(None)
                    server_ids.append(None)
                    processing_percentages.append(None)
                    latencies.append(None)
                    scheduling_status.append(None)
                    packet_data_sizes.append(None)

            for i in range(max(len(edge_server_list), len(process_ids))-1):
                reporting_time.append(0)

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
            self.logger.debug(len(reporting_time))
            self.logger.debug("\n")

            MEC_to_RAN_column = np.column_stack((edge_server_list, edge_servers_available_cpu_shares,
                                                edge_servers_available_storage,
                                                process_ids, process_names, user_ids, server_ids, processing_percentages,
                                                latencies, scheduling_status, packet_data_sizes, reporting_time))
            df = pd.DataFrame(MEC_to_RAN_column, columns=["Edge Server List", "Available CPU Shares", "Available Storage",
                                                          "Process IDs", "Process Names", "User IDs", "Server IDs", "Processing Percentages",
                                                          "Latencies", "Scheduling Status", "Packet Data Sizes", "Reporting Time"])
            self.main_simulation.mec_data = df

    def receive_ran_data(self):
        sim = self.main_simulation
        while not sim.stop:
            next_tti = self.main_simulation.tti_dist.next()
            self.parse_RAN_data(sim.ran_data)
            yield self.env.timeout(next_tti)


    def parse_RAN_data(self, ran_data):
        global SEQ_NUM
        arrived_packets = []

        for index, row in ran_data.iterrows():
            user_id = index
            arriving_base_station = row[0]
            throughput = row[1]
            latency = row[2]
            if latency == '' or throughput == '':
                continue

            packet_data_size = row[3]
            instruction_per_bit = row[4]
            delay_tolerance = row[5]
            tmp_packet = RanPacket(user_id, arriving_base_station, throughput, latency, packet_data_size,
                                   instruction_per_bit, delay_tolerance)
            arrived_packets.append(tmp_packet)

        while arrived_packets:
            packet = arrived_packets[0]
            source_entity = get_entity_by_id(self.DeviceID_to_EntityID_Map()[int(packet.user_id)])
            service_information = source_entity.get_service_information()
            app_name = service_information["app_name"]
            service = service_information["service"]
            ran_message = service.output_message()
            ran_message.set_instructions(packet.size * 10 ** 3 * packet.instructions_per_bit)
            ran_message.set_bits(packet.size * 10 ** 3)
            ran_message.set_delay_budget(packet.delay_budget)
            ran_message.sequence_number = SEQ_NUM
            ran_message.timestamp = self.env.now
            ran_message.sender_id = self.BaseStationID_to_EntityID_Map()[int(packet.received_bs)]
            ran_message.source_service = service.name
            ran_message.source_service_id = service.process_id
            ran_message.source_id = source_entity.entity_id
            ran_message.user_id = packet.user_id
            ran_message.location = ran_message.sender_id
            ran_message.app_name = app_name
            ran_message.destination_service_instance = \
                map_user_id_to_entity(packet.user_id).assigned_services[ran_message.app_name][ran_message.destination_service]
            ran_message.destination_service_id = ran_message.destination_service_instance.process_id
            ran_message.destination_id = getProcessID_to_NodeID_Map()[ran_message.destination_service_id]
            ran_message.ul_latency = packet.latency
            ran_message.entry_time_to_backhaul = self.env.now
            self.messages_in_the_backhaul.append(ran_message)
            self.send_message(ran_message)
            arrived_packets.remove(packet)

        SEQ_NUM += 1


class RanPacket:
    def __init__(self, sender_id, received_bs, throughput, latency, packet_size, instructions_per_bit, delay_budget):
        self.user_id = int(sender_id)
        self.received_bs = int(float(received_bs))
        if throughput != '':
            self.throughput = float(throughput)
        if latency != '':
            self.latency = float(latency)
        self.size = float(packet_size)
        self.instructions_per_bit = float(instructions_per_bit)
        self.delay_budget = float(delay_budget)
