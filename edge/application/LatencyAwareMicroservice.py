from edge.application.Microservice import Microservice
from edge.application.Message import Message
from edge.entities.Entity import Entity, get_sim
from edge.application.Application import get_AppName_to_AppInst_Map


class LatencyAwareMicroservice(Microservice):
    def __init__(self, name=None,
                 app=None,
                 app_name=None,
                 input_messages=None,
                 output_messages=None,
                 generated_message=None,
                 distribution=None,
                 request_cpu_share=1,
                 limit_cpu_share=None,
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
        super().__init__(
            name=name,
            app=app,
            app_name=app_name,
            input_messages=input_messages,
            output_messages=output_messages,
            generated_message=generated_message,
            distribution=distribution,
            request_cpu_share=request_cpu_share,
            limit_cpu_share=limit_cpu_share,
            required_memory=required_memory,
            destination_service=destination_service,
            is_deployed_at_edge=is_deployed_at_edge,
            is_shared=is_shared,
            desired_latency=desired_latency,
            radio_aware=radio_aware,
            **param)

    def receive_messages(self):
        sim = get_sim()
        process_id = self.process_id
        while not sim.stop:
            received_message = yield self.message_receive_queue.get()
            if received_message.ul_latency > self.desired_latency:
                sim.messages_in_the_backhaul.remove(received_message)
                pass
            else:
                if received_message.msg_type == "SINK":
                    sim.logger.debug("(App:%s #Process:%i #%s) Received Message: %s at time T : %s\n" % (
                        self.app_name, self.process_id, self.name, received_message.name, sim.env.now))
                    get_AppName_to_AppInst_Map()[self.app_name][self.app.user_id].latest_ending_time = sim.env.now
                else:
                    sim.logger.debug(
                        "(App:%s #Process:%i #%s) Processing Message: %s with Sequence Number : %d at T: %s \n" % (
                            self.app_name, process_id, self.name, received_message.name,
                            received_message.sequence_number,
                            sim.env.now))
                    received_message.start_of_processing = sim.env.now

                    self.processing_queue[self.rr_counter].append(received_message)
                    self.rr_counter = (self.rr_counter + 1) % self.num_threads

            self.host_entity.orchestrator.collect_message_for_analytics(received_message)
