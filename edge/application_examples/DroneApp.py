from edge.application import Application, Microservice, Message


class DroneApp(Application):
    pass

class Image(Message):
    def __init__(self):
        super().__init__(name="Image",
                         source_service="Image_Acquisition",
                         destination_service="Frontend",
                         instructions=1000000,
                         bytes=100)


class DetectedFeatures(Message):
    def __init__(self):
        super().__init__(name="Detected_Features",
                         source_service="Frontend",
                         destination_service="Backend",
                         instructions=1000000,
                         bytes=100)


class CorrectedPose(Message):
    def __init__(self):
        super().__init__(name="Corrected_Pose",
                         source_service="Backend",
                         destination_service="Prediction",
                         instructions=1000000,
                         bytes=100)

class ImageAcquisition(Microservice):
    name = "Image_Acquisition"
    app_name = "DroneApp"
    user = None
    required_cpu_share = 1
    required_memory = 1
    is_deployed_at_edge = True
    output_messages = Image
    is_shared = None
    desired_latency = 100

    def __init__(self):
        super().__init__(name=ImageAcquisition.name,
                         app_name=ImageAcquisition.app_name,
                         required_cpu_share=ImageAcquisition.required_cpu_share,
                         required_memory=ImageAcquisition.required_memory,
                         is_deployed_at_edge=ImageAcquisition.is_deployed_at_edge,
                         input_messages=ImageAcquisition.input_messages,
                         is_shared=ImageAcquisition.is_shared,
                         desired_latency=ImageAcquisition.desired_latency,
                         radio_aware=False)


class Backend(Microservice):
    name = "Backend"
    app_name = "DroneApp"
    user = None
    required_cpu_share = 1
    required_memory = 1
    is_deployed_at_edge = True
    output_messages = Image
    is_shared = None
    desired_latency = 100

    def __init__(self):
        super().__init__(name=Backend.name,
                         app_name=Backend.app_name,
                         required_cpu_share=Backend.required_cpu_share,
                         required_memory=Backend.required_memory,
                         is_deployed_at_edge=Backend.is_deployed_at_edge,
                         input_messages=Backend.input_messages,
                         is_shared=Backend.is_shared,
                         desired_latency=Backend.desired_latency,
                         radio_aware=False)


class Frontend(Microservice):
    name = "Image_Acquisition"
    app_name = "DroneApp"
    user = None
    required_cpu_share = 1
    required_memory = 1
    is_deployed_at_edge = True
    output_messages = Image
    is_shared = None
    desired_latency = 100

    def __init__(self):
        super().__init__(name=Frontend.name,
                         app_name=Frontend.app_name,
                         required_cpu_share=Frontend.required_cpu_share,
                         required_memory=Frontend.required_memory,
                         is_deployed_at_edge=Frontend.is_deployed_at_edge,
                         input_messages=Frontend.input_messages,
                         is_shared=Frontend.is_shared,
                         desired_latency=Frontend.desired_latency,
                         radio_aware=False)


class Prediction(Microservice):
    name = "Image_Acquisition"
    app_name = "DroneApp"
    user = None
    required_cpu_share = 1
    required_memory = 1
    is_deployed_at_edge = True
    output_messages = Image
    is_shared = None
    desired_latency = 100

    def __init__(self):
        super().__init__(name=Prediction.name,
                         app_name=Prediction.app_name,
                         required_cpu_share=Prediction.required_cpu_share,
                         required_memory=Prediction.required_memory,
                         is_deployed_at_edge=Prediction.is_deployed_at_edge,
                         input_messages=Prediction.input_messages,
                         is_shared=Prediction.is_shared,
                         desired_latency=Prediction.desired_latency,
                         radio_aware=False)


