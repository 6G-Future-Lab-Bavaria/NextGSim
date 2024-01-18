from edge.application import Application, Microservice


class DroneApp(Application):
    pass


class ImageAcquisition(Microservice):
    name = "Image_Acquisition"
    app_name = "DroneApp"
    user = "public"
    required_cpu_share = 1
    required_memory = 1
    is_deployed_at_edge = True
    input_messages = OffloadedData
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
                         radio_aware=False)
