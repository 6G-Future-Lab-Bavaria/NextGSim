import simpy
import copy
import random
import logging

from edge.application.Microservice import Microservice
from edge.application.Message import Message
from edge.entities.Entity import Entity, get_sim
from edge.application.Application import get_AppName_to_AppInst_Map
from edge.entities.Entity import Entity, get_sim
from edge.application.Microservice import ServiceName_to_ProcessID_Map, \
    ProcessID_to_NodeID_Map, ProcessID_to_Service_Map


class LoadBalancerService(Microservice):
    def __init__(self,
                 app=None,
                 app_name=None,
                 balanced_service=None,
                 is_deployed_at_edge=True,
                 is_shared=True,
                 balanced_servers=None,
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
        super().__init__(
            name=balanced_service + "LoadBalancer",
            app_name=app_name,
            destination_service=balanced_service,
            is_deployed_at_edge=is_deployed_at_edge,
            is_shared=is_shared,
            **param)

        if balanced_servers is None:
            self.balanced_servers = []

        self.balanced_service = balanced_service
        self.balanced_servers = balanced_servers
        self.balanced_service_instances = []
        self.avg_processing_time_of_services = {}
        self.avg_processing_time_of_users = {}

        for server in self.balanced_servers:
            balanced_instances = server.find_services(app_name, balanced_service,
                                                      "public")  # TODO: It doesn't have to be public
            self.balanced_service_instances.extend(balanced_instances)

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
        mec_sim.env.process(self.forward_messages())
        mec_sim.env.process(self.update_processing_time_information())

    def forward_messages(self):
        mec_sim = get_sim()
        while not mec_sim.stop:
            message = yield self.message_receive_queue.get()
            destination_service = self.select_services(self.balanced_service_instances, message)
            message.sender_id = self.host_entity.entity_id
            message.destination_service = self.balanced_service
            message.destination_service_id = destination_service.process_id
            message.destination_id = destination_service.host_entity.entity_id
            message.location = self.host_entity.entity_id
            message.app_name = self.app_name
            mec_sim.logger.debug("(App:%s #Process:%i #%s) LoadBalancer is Forwarding Message: %s at time T : %s\n" % (
                self.app_name, self.process_id, self.name, message.name, mec_sim.env.now))
            mec_sim.send_message(message)

    def update_processing_time_information(self):
        mec_sim = get_sim()
        while True:
            next_update_time = mec_sim.service_update_distribution.next()
            yield mec_sim.env.timeout(next_update_time)
            for service in self.balanced_service_instances:
                avg_processing_time_of_users = service.get_average_processing_time_per_user()
                avg_processing_time_of_service = service.get_average_processing_time()
                self.avg_processing_time_of_services[service] = avg_processing_time_of_service
                for user in avg_processing_time_of_users:
                    self.avg_processing_time_of_users[user] = avg_processing_time_of_users[user]

            print("AVG PROCESSING TIME OF USERS")
            print(self.avg_processing_time_of_users)
            print("AVG PROCESSING TIME")
            print(self.avg_processing_time_of_services)



    # def update

    def select_services(self, candidate_services, message):
        destination_service = random.choice(candidate_services)
        return destination_service
