from edge.application.Application import Application, add_app
from edge.application.Message import Message
from edge.application.Microservice import Microservice
from edge.application.LatencyAwareMicroservice import LatencyAwareMicroservice


class Offloaded_Data(Message):
    def __init__(self):
        super().__init__(name="Offloaded Data",
                         source_service="Data Generation",
                         msg_type="SOURCE",
                         destination_service="Data_Processing",
                         instructions=1000000,
                         bytes=100)


class DataProcessing(LatencyAwareMicroservice):
    name = "Data_Processing"
    app_name = "RANApplicationPublicRadioAware"
    user = "public"
    required_cpu_share = 1
    required_memory = 1
    is_deployed_at_edge = True
    input_messages = Offloaded_Data
    is_shared = True
    desired_latency = 100

    def __init__(self):
        super().__init__(name=DataProcessing.name,
                         app_name=DataProcessing.app_name,
                         required_cpu_share=DataProcessing.required_cpu_share,
                         required_memory=DataProcessing.required_memory,
                         is_deployed_at_edge=DataProcessing.is_deployed_at_edge,
                         input_messages=DataProcessing.input_messages,
                         is_shared=DataProcessing.is_shared,
                         desired_latency=DataProcessing.desired_latency,
                         radio_aware=True)


class DataGeneration(Microservice):
    name = "Data_Generation"
    app_name = "RANApplicationPublicRadioAware"
    user = None
    required_cpu_share = 0.1
    required_memory = 0.1
    is_deployed_at_edge = False
    output_message = Offloaded_Data
    is_shared = False


    def __init__(self):
        super().__init__(name=DataGeneration.name,
                         app_name=DataGeneration.app_name,
                         required_cpu_share=DataGeneration.required_cpu_share,
                         required_memory=DataGeneration.required_memory,
                         is_deployed_at_edge=DataGeneration.is_deployed_at_edge,
                         output_messages=DataGeneration.output_message,
                         is_shared=DataGeneration.is_shared,
                         radio_aware=True)


class RANApplicationPublicRadioAware(Application):
    name = "RANApplicationPublicRadioAware"
    services = [DataGeneration, DataProcessing]
    number_of_service_instances = {"Data_Processing": 10}
    cycles_per_bit_min = 25
    cycles_per_bit_max = 45
    delay_min = 30
    delay_max = 31
    data_size_min = 30
    data_size_max = 31

    def __init__(self, user_id=None):
        super().__init__(name="RANApplicationPublicRadioAware")
        self.set_user_id(user_id)
        self.set_services(RANApplicationPublicRadioAware.services,
                          RANApplicationPublicRadioAware.number_of_service_instances)
        add_app(self)
