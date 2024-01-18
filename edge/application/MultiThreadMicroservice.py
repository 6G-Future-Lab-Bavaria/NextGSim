import simpy
import numpy as np
import copy
import logging
import random

from edge.application.Message import Message
from edge.entities.Entity import Entity, get_sim
from edge.application.Microservice import Microservice
from edge.application.Application import get_AppName_to_AppInst_Map


class MultithreadMicroservice(Microservice):
    def __init__(self, name=None,
                 app=None,
                 app_name=None,
                 input_messages=None,
                 output_messages=None,
                 generated_message=None,
                 distribution=None,
                 request_cpu_share=0.1,
                 allocated_cpu_share=None,
                 limit_cpu_share=0.1,
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
        super().__init__(name,
                         app,
                         app_name,
                         input_messages,
                         output_messages,
                         generated_message,
                         distribution,
                         request_cpu_share,
                         limit_cpu_share,
                         required_gpu_share,
                         required_memory,
                         destination_service,
                         is_deployed_at_edge,
                         is_shared,
                         desired_latency,
                         radio_aware,
                         **param)

        self.num_threads = np.floor(limit_cpu_share / request_cpu_share)
    #
    # def set_queues(self, env):
    #     self.message_receive_queue = simpy.Store(env)
    #     self.message_send_queue = simpy.Store(env)
    #     self.processing_queue = [[] for _ in range(self.num_threads)]





