from attic.MobileDevice import MobileDevice
from attic.Sensor import Sensor
from attic.Actuator import Actuator
from edge.network.Link import add_link


class SimpleDevice1(MobileDevice):
    def __init__(self, name=None, entity_id=None, model='simple_device_1', user_id=None, num_of_cpus=1, location=None, attached_bs=None,
                 velocity=30):
        super().__init__(name=name, entity_id=entity_id, model=model, user_id=user_id,
                         location=location, attached_bs=attached_bs, velocity=velocity, num_of_cpus=num_of_cpus)

        self.sensor_1 = Sensor(user_id=self.user_id)
        self.actuator = Actuator(user_id=self.user_id)
        self.devices["sensor_1"] = self.sensor_1
        self.devices["actuator"] = self.actuator

        add_link(source=self.sensor_1, destination=self, bandwidth=1000, latency=0)
        add_link(source=self, destination=self.actuator, bandwidth=1000, latency=0)
