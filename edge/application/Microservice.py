import simpy
import copy
import random
import logging

from edge.application.Message import Message
from edge.entities.Entity import Entity, get_sim
from edge.application.Application import get_AppName_to_AppInst_Map

epsilon = 0.0001
ServiceName_to_ProcessID_Map = {}
ProcessID_to_NodeID_Map = {}
ProcessID_to_Service_Map = {}

process_id_counter = 0
logger = logging.getLogger(__name__)


def get_process_id():
    global process_id_counter
    prev_process_id = process_id_counter
    process_id_counter += 1
    return prev_process_id


class Microservice(Entity):
    def __init__(self, name=None,
                 app=None,
                 app_name=None,
                 input_messages=None,
                 output_messages=None,
                 generated_message=None,
                 distribution=None,
                 required_cpu_share=0.1,
                 cpu_share_limit=None,
                 required_gpu_share=0,
                 required_memory=0,
                 destination_service=None,
                 is_deployed_at_edge=False,
                 is_shared=False,
                 desired_latency=100000,
                 radio_aware=False,
                 **param):

        """
        Args:
            name:
            required_memory:
            service_type:
            host_entity_model:
            message_in:
            message_out:
            required_cpu:
            module_dest:
            **param:
        """
        super().__init__()
        self.name = name
        self.app = app
        self.app_name = app_name
        self.host_entity = None
        self.user = None
        self.user_list = []  # Only used for public services
        self.process_id = get_process_id()
        self.required_cpu_share = required_cpu_share
        self.cpu_share_limit = cpu_share_limit
        self.required_memory = required_memory
        self.destination_service = destination_service
        self.sequence_number = 0
        self.is_deployed_at_edge = is_deployed_at_edge
        self.is_shared = is_shared
        self.params = param
        self.message_receive_queue = None
        self.message_send_queue = None
        self.processing_queue = None
        self.generated_message = generated_message
        self.generation_distribution = distribution
        self.average_latency = 0
        self.user_information_from_orchestrator = {}
        self.desired_latency = desired_latency
        self.radio_aware = radio_aware

        if isinstance(input_messages, Message):
            self.input_messages = [input_messages]
        else:
            self.input_messages = input_messages

        if isinstance(output_messages, Message):
            self.output_messages = [output_messages]
        else:
            self.output_messages = output_messages

    def set_user(self, user):
        self.user = user

    def set_queues(self, env):
        """
        Sets queues for sending, receiving and processing.
        """
        self.message_receive_queue = simpy.Store(env)
        self.message_send_queue = simpy.Store(env)
        self.processing_queue = []

    def update_average_processing_latency(self, processing_time):
        if self.average_latency is not None:
            self.average_latency = 0.5 * self.average_latency + 0.5 * processing_time
        else:
            self.average_latency = processing_time

    def update_user_information_from_orchestrator(self, information):
        self.user_information_from_orchestrator = information

    def get_average_radio_latency(self):
        average_radio_latencies_of_users = {}
        for user in self.user_list:
            if user in self.user_information_from_orchestrator:
                if "average_radio_latency" in self.user_information_from_orchestrator[user]:
                    average_radio_latencies_of_users[user] = \
                        self.user_information_from_orchestrator[user]["average_radio_latency"]
                else:
                    average_radio_latencies_of_users[user] = 0
            else:
                average_radio_latencies_of_users[user] = 0

        return average_radio_latencies_of_users

    def insert_message(self, message):
        self.message_receive_queue.put(message)

    def deploy(self, host_entity, user=None):
        mec_sim = get_sim()
        self.set_queues(mec_sim.env)
        self.host_entity = host_entity
        self.user = user
        ProcessID_to_NodeID_Map[self.process_id] = host_entity.entity_id
        ProcessID_to_Service_Map[self.process_id] = self
        if self.app_name not in ServiceName_to_ProcessID_Map:
            ServiceName_to_ProcessID_Map[self.app_name] = {}
        if self.name not in ServiceName_to_ProcessID_Map[self.app_name]:
            ServiceName_to_ProcessID_Map[self.app_name][self.name] = {}
        if self.user not in ServiceName_to_ProcessID_Map[self.app_name][self.name]:
            ServiceName_to_ProcessID_Map[self.app_name][self.name][self.user] = []
        ServiceName_to_ProcessID_Map[self.app_name][self.name][self.user].append(self.process_id)
        mec_sim.env.process(self.generate_messages())
        mec_sim.env.process(self.receive_messages())
        mec_sim.env.process(self.process_messages())

    def delete_service(self):
        del ProcessID_to_NodeID_Map[self.process_id]
        del ProcessID_to_Service_Map[self.process_id]
        ServiceName_to_ProcessID_Map[self.app_name][self.name][self.user].remove(self.process_id)

    def register_user(self, user):
        self.user_list.append(user)

    def deregister_user(self, user):
        self.user_list.remove(user)

    def migrate(self, migrated_node):
        logger.debug('Service %s with process id: %d is being migrated from node:%d to node:%d' % (
            self.name, self.process_id, self.host_entity.entity_id, migrated_node.entity_id))
        self.host_entity.undeploy_service(self)
        self.host_entity = migrated_node
        ProcessID_to_NodeID_Map[self.process_id] = migrated_node.entity_id

    def generate_messages(self):
        mec_sim = get_sim()
        process_id = self.process_id
        generation_distribution = self.generation_distribution
        if self.generated_message is not None:
            while not mec_sim.stop:
                next_time = generation_distribution.next()
                yield mec_sim.env.timeout(next_time)
                message = copy.copy(self.generated_message)
                mec_sim.logger.debug("(App:%s #Process:%i #%s) Generating Source Message: %s at T: %s \n" % (
                    self.app.name, process_id, message.source_service, message.name, mec_sim.env.now))
                self.host_entity.update_service_map()
                message.timestamp = mec_sim.env.now
                message.sequence_number = self.sequence_number
                self.sequence_number += 1
                message.source_service_id = process_id
                message.user_id = self.host_entity.entity_id
                message.sender_id = self.host_entity.entity_id
                message.source_id = message.sender_id
                destination_services = self.host_entity.find_services(self.app.name, self.destination_service,
                                                                      self.user)
                if len(destination_services) == 1:
                    destination_service = destination_services[0]
                    message.destination_service_id = destination_service.process_id
                    message.destination_id = destination_service.host_entity.entity_id
                else:
                    print("Service Not Found : %s" % message.destination_service)
                    break

                message.location = message.sender_id
                message.app_name = self.app.name
                self.app.latest_starting_time = mec_sim.env.now
                mec_sim.send_message(message)
        else:
            return

    def receive_messages(self):
        sim = get_sim()
        process_id = self.process_id
        while not sim.stop:
            received_message = yield self.message_receive_queue.get()
            if received_message.msg_type == "SINK":
                sim.logger.debug("(App:%s #Process:%i #%s) Received Message: %s at time T : %s\n" % (
                    self.app.name, self.process_id, self.name, received_message.name, sim.env.now))
                get_AppName_to_AppInst_Map()[self.app.name][self.app.user_id].latest_ending_time = sim.env.now
            else:
                sim.logger.debug(
                    "(App:%s #Process:%i #%s) Processing Message: %s with Sequence Number : %d at T: %s \n" % (
                        self.app_name, process_id, self.name, received_message.name,
                        received_message.sequence_number,
                        sim.env.now))
                received_message.start_of_processing = sim.env.now
                self.host_entity.orchestrator.collect_message_for_analytics(received_message)
                self.processing_queue.append(received_message)

    def process_messages(self):
        mec_sim = get_sim()
        while not mec_sim.stop:
            output_message = yield self.message_send_queue.get()
            self.host_entity.update_service_map()
            mec_sim.logger.debug("(App:%s #Process:%i #%s) Sending Message: %s at time T : %s\n" % (
                self.app.name, self.process_id, self.name, output_message.name, mec_sim.env.now))
            output_message.timestamp = mec_sim.env.now
            output_message.source_id = self.host_entity.entity_id
            output_message.source_service_id = self.process_id
            output_message.sender_id = self.host_entity.entity_id
            destination_services = self.host_entity.find_services(self.app.name, self.destination_service, self.user)
            if len(destination_services) == 1:  # TODO : What if there are more than 1 service?
                destination_service = destination_services[0]
                output_message.destination_service_id = destination_service.process_id
                output_message.destination_id = destination_service.host_entity.entity_id
                output_message.location = self.host_entity.entity_id
                output_message.app_name = self.app.name
                mec_sim.send_message(output_message)
            else:
                print("Service Not Found : %s" % output_message.destination_service)
                continue


def getServiceName_to_ProcessID_Map():
    return ServiceName_to_ProcessID_Map


def getProcessID_to_NodeID_Map():
    return ProcessID_to_NodeID_Map


def getProcessID_to_Service_Map():
    return ProcessID_to_Service_Map
