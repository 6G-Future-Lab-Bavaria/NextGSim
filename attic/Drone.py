from entities.mobile_device import MobileDevice
from entities.sensor import Sensor
from entities.actuator import Actuator
from network.network_topology import add_link


class Drone(MobileDevice):
    def __init__(self, entity_id=None, model='drone', user_id=None, location=None,
                 attached_bs=None, velocity=1):
        super().__init__(entity_id, model, user_id, location, attached_bs, velocity)

        self.is_mobile_device = True

        self.camera = Sensor(model="camera", user_id=self.user_id)

        self.imu = Sensor(model="imu", user_id=self.user_id)

        self.actuator = Actuator(model="actuator_device", user_id=self.user_id)

        add_link(source=self.camera, destination=self, bandwidth=1000, latency=0)
        add_link(source=self.imu, destination=self, bandwidth=1000, latency=0)
        add_link(source=self, destination=self.actuator, bandwidth=1000, latency=0)
