from edge.application.Application import Application, add_app
from edge.application.Message import Message
from edge.application.Microservice import Microservice


class OffloadedData(Message):
    def __init__(self):
        super().__init__(name="Offloaded Data",
                         source_service="Data Generation",
                         msg_type="SOURCE",
                         destination_service="Data_Processing",
                         instructions=1000000,
                         bytes=100)


class DataProcessing(Microservice):
    name = "Data_Processing"
    app_name = "RANApplicationPublic"
    user = "public"
    request_cpu_share = 1
    required_memory = 1
    is_deployed_at_edge = True
    input_messages = OffloadedData
    is_shared = True
    desired_latency = 100

    def __init__(self):
        super().__init__(name=DataProcessing.name,
                         app_name=DataProcessing.app_name,
                         request_cpu_share=DataProcessing.request_cpu_share,
                         required_memory=DataProcessing.required_memory,
                         is_deployed_at_edge=DataProcessing.is_deployed_at_edge,
                         input_messages=DataProcessing.input_messages,
                         is_shared=DataProcessing.is_shared,
                         desired_latency=DataProcessing.desired_latency,
                         radio_aware=False)


class DataGeneration(Microservice):
    name = "Data_Generation"
    app_name = "RANApplicationPublic"
    user = None
    request_cpu_share = 0.1
    required_memory = 0.1
    is_deployed_at_edge = False
    output_message = OffloadedData
    is_shared = True

    def __init__(self):
        super().__init__(name=DataGeneration.name,
                         app_name=DataGeneration.app_name,
                         request_cpu_share=DataGeneration.request_cpu_share,
                         required_memory=DataGeneration.required_memory,
                         is_deployed_at_edge=DataGeneration.is_deployed_at_edge,
                         output_messages=DataGeneration.output_message,
                         is_shared=DataGeneration.is_shared,
                         radio_aware=False)


class RANApplicationPublic(Application):
    name = "RANApplicationPublic"
    services = [DataGeneration, DataProcessing]
    number_of_service_instances = {"Data_Processing": 10}
    cycles_per_bit_min = 45
    cycles_per_bit_max = 55
    delay_min = 100
    delay_max = 101
    data_size_min = 30
    data_size_max = 31

    def __init__(self, user_id=None):
        super().__init__(name="RANApplicationPublic")
        self.set_user_id(user_id)
        self.set_services(RANApplicationPublic.services,
                          RANApplicationPublic.number_of_service_instances)
        add_app(self)
