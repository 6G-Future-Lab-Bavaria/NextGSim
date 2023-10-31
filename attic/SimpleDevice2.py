from entities.mobile_device import MobileDevice
from entities.sensor import Sensor
from entities.actuator import Actuator
from network.network_topology import add_link


class SimpleDevice2(MobileDevice):
    def __init__(self, entity_id=None, model='simple_device_2', user_id=None, location=None,
                 attached_bs=None, velocity=1):
        super().__init__(entity_id, model, user_id, location, attached_bs, velocity)

        self.sensor_1 = Sensor(model="sensor_1", user_id=self.entity_id)
        self.sensor_2 = Sensor(model="sensor_2", user_id=self.entity_id)
        self.actuator = Actuator(model="actuator", user_id=self.entity_id)

        add_link(source=self.sensor_1, destination=self, bandwidth=1000, latency=0)
        add_link(source=self.sensor_2, destination=self, bandwidth=1000, latency=0)
        add_link(source=self, destination=self.actuator, bandwidth=1000, latency=0)
