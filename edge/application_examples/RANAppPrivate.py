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


class DataProcessingPrivate(Microservice):
    name = "Data_Processing"
    app_name = "RANApplicationPrivate"
    user = "public"
    required_cpu_share = 1
    required_memory = 1
    is_deployed_at_edge = True
    input_messages = OffloadedData
    is_shared = False
    desired_latency = 100

    def __init__(self):
        super().__init__(name=DataProcessingPrivate.name,
                         app_name=DataProcessingPrivate.app_name,
                         required_cpu_share=DataProcessingPrivate.required_cpu_share,
                         required_memory=DataProcessingPrivate.required_memory,
                         is_deployed_at_edge=DataProcessingPrivate.is_deployed_at_edge,
                         input_messages=DataProcessingPrivate.input_messages,
                         is_shared=DataProcessingPrivate.is_shared,
                         desired_latency=DataProcessingPrivate.desired_latency,
                         radio_aware=False)


class DataGenerationPrivate(Microservice):
    name = "Data_Generation"
    app_name = "RANApplicationPrivate"
    user = None
    required_cpu_share = 0.1
    required_memory = 0.1
    is_deployed_at_edge = False
    output_message = OffloadedData
    is_shared = False

    def __init__(self):
        super().__init__(name=DataGenerationPrivate.name,
                         app_name=DataGenerationPrivate.app_name,
                         required_cpu_share=DataGenerationPrivate.required_cpu_share,
                         required_memory=DataGenerationPrivate.required_memory,
                         is_deployed_at_edge=DataGenerationPrivate.is_deployed_at_edge,
                         output_messages=DataGenerationPrivate.output_message,
                         is_shared=DataGenerationPrivate.is_shared,
                         radio_aware=False)


class RANApplicationPrivate(Application):
    name = "RANApplicationPrivate"
    services = [DataGenerationPrivate, DataProcessingPrivate]
    number_of_service_instances = {"Data_Processing": 1}
    cycles_per_bit_min = 225
    cycles_per_bit_max = 235
    delay_min = 30
    delay_max = 31
    data_size_min = 30
    data_size_max = 31

    def __init__(self, user_id=None):
        super().__init__(name="RANApplicationPrivate")
        self.set_user_id(user_id)
        self.set_services(RANApplicationPrivate.services,
                          RANApplicationPrivate.number_of_service_instances)
        add_app(self)
