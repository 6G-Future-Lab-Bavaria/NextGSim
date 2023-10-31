from edge.application.Application import Application
from edge.application.Message import Message
from edge.application.Microservice import Microservice
from edge.network.Routing import ShortestPathRouting
from edge.util.DistributionFunctions import DeterministicDistributionWithStartingTime


def app_deployment_1(user_id=None):
    app = Application("SIMPLE_APP1")
    app.set_user_id(user_id)
    """
    Application Description
    """
    m_sensor_1_acq = Message(name="Sensor_1_Data_ACQ_APP1", source_service="Sensor_1_APP1",
                             destination_service="Sensor_1_Acquisition_APP1",
                             instructions=10000, bytes=0)
    m_sensor_1 = Message(name="Sensor_1_Data_APP1", source_service="Sensor_1_Acquisition_APP1",
                         destination_service="Sensor_Data_Processing_APP1",
                         instructions=1270000, bytes=40000)
    m_processed_data = Message(name="Processed_Sensor_Data_APP1", source_service="Sensor_Data_Processing_APP1",
                               destination_service="Actuator_Driver_APP1",
                               instructions=127000, bytes=200)
    m_actuator = Message(name="Actuator_Action", source_service="Actuator_Driver_APP1",
                         destination_service="Actuator_SINK_APP1",
                         instructions=1000, bytes=100)

    deterministic_distribution = DeterministicDistributionWithStartingTime(
        name="Deterministic_" + str(app.user_id) + "_1", period=80, starting_time=7)

    sensor_1 = SourceService('Sensor_1_APP1', host_entity_model="sensor_1", output_message=m_sensor_1_acq,
                             distribution=deterministic_distribution, app=app)
    sensor_1_acq = Microservice(name='Sensor_1_Acquisition_APP1', app=app, required_memory=5000,
                                service_type="COMPUTE",
                                required_cpu_share=0.3, input_messages=m_sensor_1_acq, output_messages=m_sensor_1)
    sensor_data_processing = Microservice(name='Sensor_Data_Processing_APP1', app=app, required_memory=5000,
                                          service_type="COMPUTE",
                                          input_messages=m_sensor_1, output_messages=m_processed_data,
                                          is_deployed_at_edge=True)
    actuator_driver = Microservice(name='Actuator_Driver_APP1', app=app, required_memory=5000,
                                   service_type="COMPUTE",
                                   input_messages=m_processed_data, output_messages=m_actuator)
    actuator_sink = SinkService("Actuator_SINK_APP1", host_entity_type='actuator', input_message=m_actuator,
                                app=app)

    number_of_service_instances = {"Sensor_1_APP1": 1,
                                   "Sensor_1_Acquisition_APP1": 1,
                                   "Sensor_Data_Processing_APP1": 1,
                                   "Actuator_Driver_APP1": 1,
                                   "Actuator_SINK_APP1": 1}

    app.set_services([sensor_1, sensor_1_acq, sensor_data_processing, actuator_driver, actuator_sink],
                     number_of_service_instances)

    return app


def offloading_app(user_id=None):
    app = Application("OFFLOAD_APP")
    app.set_user_id(user_id)
    """
    Application Description
    """
    m_offloaded = Message(name="Offloaded Data", source_service="Data Generation",
                          destination_service="Compute",
                          instructions=10000, bytes=100)

    m_processed = Message(name="Processed_Data", source_service="Compute Service",
                          destination_service="Data Sink",
                          instructions=0, bytes=200)

    deterministic_distribution = DeterministicDistributionWithStartingTime(
        name="Deterministic_" + str(app.user_id) + "_1", period=80, starting_time=7)

    data_gen = SourceService('Data Generation', host_entity_model="sensor_1", output_message=m_offloaded,
                             distribution=deterministic_distribution, app=app)
    data_processing = Microservice(name='Data Processing', app=app, required_memory=5000,
                                   service_type="COMPUTE",
                                   required_cpu_share=0.3, input_messages=m_offloaded, output_messages=m_processed)
    data_sink = SinkService("Data Sink", host_entity_type='actuator', input_message=m_processed,
                            app=app)

    number_of_service_instances = {"Sensor_1_APP1": 1,
                                   "Sensor_1_Acquisition_APP1": 1,
                                   "Sensor_Data_Processing_APP1": 1,
                                   "Actuator_Driver_APP1": 1,
                                   "Actuator_SINK_APP1": 1}

    app.set_services([data_gen, data_processing, data_sink], number_of_service_instances)


def app_deployment_2(user_id):
    app = Application("SIMPLE_APP2_" + str(user_id))
    app.set_user_id(user_id)

    """
    Application Description
    """
    m_sensor_acq = Message(name="Sensor_Data_ACQ_APP2", source_service="Sensor_APP2",
                           destination_service="Sensor_Data_Acquisition_APP2",
                           instructions=1, bytes=0)
    m_sensor = Message(name="Sensor_Data_APP2", source_service="Sensor_Data_Acquisition_APP2",
                       destination_service="Sensor_Data_Processing_APP2",
                       instructions=127000, bytes=40000)
    m_processed_data = Message(name="Processed_Sensor_Data_APP2", source_service="Sensor_Data_Processing_APP2",
                               destination_service="Actuator_Driver_APP2",
                               instructions=127000, bytes=200)
    m_actuator = Message(name="Actuator_Action_APP2", source_service="Actuator_Driver_APP2",
                         destination_service="Actuator_Sink_APP2",
                         instructions=1000, bytes=100)

    sensor = Microservice('Sensor_APP2', service_type="SOURCE", output_messages=m_sensor_acq)
    sensor_acq = Microservice('Sensor_Data_Acquisition_APP2', required_memory=5000,
                              service_type=Application.TYPE_INTERMEDIATE,
                              input_messages=m_sensor_acq, output_messages=m_sensor)
    sensor_data_processing = Microservice('Sensor_Data_Processing_APP2', required_memory=5000,
                                          service_type="COMPUTE",
                                          input_messages=m_sensor, output_messages=m_processed_data,
                                          is_deployed_at_edge=True)
    actuator_driver = Microservice('Actuator_Driver_APP2', required_memory=5000, service_type="COMPUTE",
                                   input_messages=m_processed_data, output_messages=m_actuator)
    actuator_sink = Microservice("Actuator_Sink_APP2", input_messages=m_actuator, service_type="SINK")

    app.set_services([sensor, sensor_acq, sensor_data_processing, actuator_driver, actuator_sink])

    placement = SimpleServicePlacementRoundRobin("Placement_" + str(user_id))
    placement.set_number_of_services(
        {"Sensor_Data_Acquisition_APP2": 1,
         "Sensor_Data_Processing_APP2": 1,
         "Actuator_Driver_APP2": 1})

    data_flow = Statical("Statical_" + str(user_id))
    data_flow.add_data_sink(
        {"model": "actuator",
         "number": 1,
         "service": actuator_sink,
         "device": user_id})

    deterministic_distribution = DeterministicDistributionWithStartingTime(
        name="Deterministic_" + str(user_id), period=200, starting_time=7)

    data_flow.add_data_source(
        {"model": "sensor",
         "number": 1,
         "output_message": m_sensor_acq,
         "service": sensor,
         "generation_distribution": deterministic_distribution,
         "user_id": user_id})

    routing_type = ShortestPathRouting()

    return app, placement


def simple_ran_app_deployment(user_id):
    app = Application("SIMPLE_RAN_APP_" + str(user_id))
    app.set_user_id(user_id)

    """
    Application Description
    """
    m_sensor = Message(name="Sensor_Data", source_service="Sensor_Data_Acquisition",
                       destination_service="Sensor_Data_Processing",
                       instructions=127000, bytes=40000)

    m_processed_data = Message(name="Processed_Sensor_Data", source_service="Sensor_Data_Processing",
                               destination_service="Actuator_Driver",
                               instructions=127000, bytes=200)

    m_actuator = Message(name="Actuator_Action", source_service="Actuator_Driver",
                         destination_service="Actuator_Sink",
                         instructions=1000, bytes=100)

    sensor_data_processing = Microservice('Sensor_Data_Processing', required_memory=5000,
                                          service_type="COMPUTE",
                                          input_messages=m_sensor, output_messages=m_processed_data,
                                          is_deployed_at_edge=True)

    actuator_driver = Microservice('Actuator_Driver', required_memory=5000, service_type="COMPUTE",
                                   input_messages=m_processed_data, output_messages=m_actuator)

    actuator_sink = Microservice("Actuator_Sink", input_messages=m_actuator, service_type="SINK")

    app.set_services([sensor_data_processing, actuator_driver, actuator_sink])

    # placement_distribution = DeterministicDistribution(period=0)

    placement = SimpleServicePlacementRoundRobin(name="Placement_" + str(user_id), activation_distribution=None)
    placement.set_number_of_services(
        {"Sensor_Data_Processing": 1,
         "Actuator_Driver": 1})

    data_flow = Statical("Statical_" + str(user_id))
    data_flow.add_data_sink(
        {"model": "actuator",
         "number": 1,
         "service": actuator_sink,
         "device": user_id})

    return app, placement


def get_app(app_name):
    if app_name == "App1":
        return app_deployment_1()
    if app_name == "App2":
        return app_deployment_2()
    if app_name == "RanApp":
        return simple_ran_app_deployment()
