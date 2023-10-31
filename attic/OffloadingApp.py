from application.application import Application
from application.microservice import Microservice
from application.message import Message
from util.distribution_fncs import DeterministicDistributionWithStartingTime


class OffloadingApp(Application):
    def __init__(self, name="OffloadApp", user_id=None):
        super().__init__(name=name)
        self.set_user_id(user_id)
        # region App Description
        m_offloaded = Message(name="Offloaded Data",
                              source_service="Data Generation",
                              msg_type="SOURCE",
                              destination_service="Data_Processing",
                              instructions=1000000,
                              num_of_bytes=100)

        m_processed = Message(name="Processed_Data",
                              msg_type="SINK",
                              source_service="Compute Service",
                              destination_service="Data_Sink",
                              instructions=1,
                              num_of_bytes=200)

        deterministic_distribution = DeterministicDistributionWithStartingTime(
            name="Deterministic_" + str(self.user_id) + "_1", period=80, starting_time=7)

        data_gen = Microservice(name='Data_Generation', host_entity_model="sensor_1", generated_message=m_offloaded,
                                required_cpu_share=0.1, distribution=deterministic_distribution, app=self)
        data_processing = Microservice(name='Data_Processing', app=self, required_storage=5000,
                                       service_type="COMPUTE", is_deployed_at_edge=True, required_cpu_share=0.3,
                                       input_messages=m_offloaded, output_messages=m_processed)
        data_sink = Microservice(name="Data_Sink", host_entity_type='actuator', input_message=m_processed,
                                 app=self)

        number_of_service_instances = {"Data_Generation": 1,
                                       "Data_Processing": 1,
                                       "Data_Sink": 1}

        # endregion
        self.set_services([data_gen, data_processing, data_sink], number_of_service_instances)
