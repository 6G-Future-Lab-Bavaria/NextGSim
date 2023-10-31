from edge.application.Application import Application
from edge.application.Microservice import Microservice
from edge.application.Message import Message
from edge.util.DistributionFunctions import DeterministicDistributionWithStartingTime


class ARPipeline(Application):
    def __init__(self, name="ARPipeline", user_id=None):
        super().__init__(name=name)

        frame_generation_rate = DeterministicDistributionWithStartingTime(
            name="Deterministic_" + str(self.user_id) + "_1", period=300, starting_time=7)

        self.set_user_id(user_id)
        # region App Description
        m_camera_frame = Message(name="Camera Frame",
                                 msg_type="SOURCE",
                                 source_service="client_send_request",
                                 destination_service="primary",
                                 instructions=1000000,
                                 bytes=100)

        m_processed_frame = Message(name="Processed Frame",
                                    msg_type="COMPUTE",
                                    source_service="primary",
                                    destination_service="sift",
                                    instructions=10000000,
                                    bytes=200)

        m_orig_descp = Message(name="Original Descriptors",
                               msg_type="COMPUTE",
                               source_service="sift",
                               destination_service="encoding",
                               instructions=1000000,
                               bytes=200)

        m_fisher_vec = Message(name="Fisher Vector",
                               msg_type="COMPUTE",
                               source_service="encoding",
                               destination_service="lsh",
                               instructions=1000000,
                               bytes=200)

        m_nearest_neighbours = Message(name="Nearest Neighbours",
                                       msg_type="COMPUTE",
                                       source_service="lsh",
                                       destination_service="matching",
                                       instructions=1000000,
                                       bytes=200)

        m_result = Message(name="Result",
                           msg_type="SINK",
                           source_service="matching",
                           destination_service="client_receive_response",
                           instructions=10000,
                           bytes=200)

        client_send_request = Microservice(name='client_send_request',
                                           host_entity_model="mobile_device",
                                           generated_message=m_camera_frame,
                                           distribution=frame_generation_rate,
                                           app=self)

        client_receive_response = Microservice(name='client_receive_response',
                                               host_entity_model="mobile_device",
                                               input=m_camera_frame,
                                               app=self)

        primary = Microservice(name='primary',
                               required_memory=1000,
                               service_type="COMPUTE",
                               is_deployed_at_edge=True,
                               required_cpu_share=1,
                               input_messages=m_camera_frame,
                               output_messages=m_processed_frame,
                               app=self)

        sift = Microservice(name='sift',
                            required_memory=1000,
                            service_type="COMPUTE",
                            is_deployed_at_edge=True,
                            required_cpu_share=1,
                            input_messages=m_processed_frame,
                            output_messages=m_orig_descp,
                            app=self)

        encoding = Microservice(name='encoding',
                                required_memory=1000,
                                service_type="COMPUTE",
                                is_deployed_at_edge=True,
                                required_cpu_share=1,
                                input_messages=m_orig_descp,
                                output_messages=m_fisher_vec,
                                app=self)

        lsh = Microservice(name='lsh',
                           required_memory=1000,
                           service_type="COMPUTE",
                           is_deployed_at_edge=True,
                           required_cpu_share=1,
                           input_messages=m_fisher_vec,
                           output_messages=m_nearest_neighbours,
                           app=self)

        matching = Microservice(name='matching',
                                required_memory=1000,
                                service_type="COMPUTE",
                                is_deployed_at_edge=True,
                                required_cpu_share=1,
                                input_messages=m_fisher_vec,
                                output_messages=m_result,
                                app=self)

        number_of_service_instances = {"client": 1,
                                       "primary": 1,
                                       "sift": 1,
                                       "encoding": 1,
                                       "lsh": 1,
                                       "matching": 1}

        # endregion
        self.set_services([client_send_request, primary, sift, encoding, lsh, matching, client_receive_response],
                          number_of_service_instances)
