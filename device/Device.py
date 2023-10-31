# @Author: Alba Jano, Anna Prado
# @Date: 2020-11-15
# @Email: alba.jano@tum.de, anna.prado@tum.de
# @Last modified by: Alba Jano

import numpy as np
from device.DeviceEnergyConsumption import DeviceEnergyConsumption
from runtime.data_classes import States
from runtime.EventChain import *
from edge.entities.ComputeNode import ComputeNode
from edge.entities.cpu.Cpu import Cpu
from edge.application.ApplicationRepository import get_app
import random


# TODO: create a data class with the device type ex. REdCap - -Alba


class Device(ComputeNode):
    def __init__(self, ID, x, y, min_x, max_x, min_y, max_y, max_speed, transmit_power, simulation):
        # self.sim_traffic = simulation.traffic_generator
        self.sim_param = simulation.sim_params
        self.event_chain = simulation.event_chain
        self.ID = ID
        self.x = x
        self.y = y
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.max_speed = max_speed
        self.direction_x = random.uniform(-1, 1)
        self.direction_y = random.uniform(-1, 1)
        self.speed = random.uniform(0, self.max_speed)
        self.indoor = self.set_indoor_field()
        self.my_gnb = None
        self.my_prbs = None
        self.my_rate = 0
        self.my_sinr = None
        self.state = States.rrc_idle
        self.transmit_power = transmit_power  # dBm
        self.energy_consumption = 0
        self.device_energy_calculation = DeviceEnergyConsumption()
        self.RRC_connected_data_inactivity_timer = 10  # ms
        self.my_connected_device_inactivity_time = 0
        # handover-related
        self.next_gnb = None
        self.hit_finish = None  # ms
        self.handover_prep_time_finish = None  # ms
        self.handover_prep_is_ongoing = False  # fixme: not needed; use handover_prep_time_finish instead
        self.ttt_finish = None  # ms
        self.rlf_finish_timer = None  # ms
        self.connected_to_gnbs = [None] * simulation.sim_params.num_TTI  # fixme: make it memory-efficient
        self.handover_t304_finish = None  # ms
        # CHO-related
        self.prepared_gnbs = {}
        self.currently_being_prep_cells_finish_time = {}
        self.x_next = None
        self.y_next = None
        self.ttt_MR_finish = {}  # ms
        # ECHO-related
        self.best_next_gnb_ids = None
        # self.handover_finish_time = None
        self._buffer = []
        self.delays = []
        self._buffer_len = 0

        # see https://www.etsi.org/deliver/etsi_ts/138300_138399/138306/15.03.00_60/ts_138306v150300p.pdf
        # formula MaxDLDataRate * RLC RTT + MaxULDataRate * RLC RTT is taken with omitted DL term
        self._max_buffer_len = None
        self.transmitted_packets = 0
        self.dropped_packets = 0

        # Edge Related Attributes (Added by Mert)
        self.clock_speed = 3 * 10 ** 9
        self.num_of_cpus = 1
        super().__init__(num_of_cpus=self.num_of_cpus, cpu_clock_speed=self.clock_speed)
        self.memory = 10
        self.app = None
        self.cpu = Cpu(clock_speed=self.clock_speed, host_entity=self)

    def update_location(self):
        new_x = self.x + self.direction_x * self.speed
        new_y = self.y + self.direction_y * self.speed

        # Check if new position is within bounds
        if self.min_x <= new_x <= self.max_x:
            self.x = new_x
        else:
            self.direction_x = -self.direction_x  # Reverse direction if hitting the boundary

        if self.min_y <= new_y <= self.max_y:
            self.y = new_y
        else:
            self.direction_y = -self.direction_y  # Reverse direction if hitting the boundary

    def init_buffer(self, simulation):
        # see https://www.etsi.org/deliver/etsi_ts/138300_138399/138306/15.03.00_60/ts_138306v150300p.pdf
        # formula MaxDLDataRate * RLC RTT + MaxULDataRate * RLC RTT is taken with omitted DL term
        self._max_buffer_len = int(simulation.sim_params.scenario.rlc_rtt *
                                   simulation.throughput_calc.calc_max_data_rate() * 1000 / (
                                           simulation.traffic_generator.packet_size() * 8))

    def RRC_Resume(self):
        self.state = States.rrc_connected
        self.energy_consumption += self.device_energy_calculation.RRC_Resume_relative_energy_consumption()

    def RRC_Setup(self):
        self.state = States.rrc_connected
        self.energy_consumption += self.device_energy_calculation.RRC_Setup_relative_energy_consumption()

    def RRC_Suspend(self):
        self.state = States.rrc_inactive
        self.my_connected_device_inactivity_time = 0

    def RRC_Release(self):
        self.state = States.rrc_idle
        self.my_connected_device_inactivity_time = 0

    def increase_inactivity_timer(self):
        self.my_connected_device_inactivity_time += 1

    def generate_device_traffic(self, system_time, duration):
        timestamp = system_time
        while timestamp < duration:  # self.sim_param.num_TTI
            packet_size = self.sim_traffic.packet_size()  # bits
            e = SimEvent(timestamp, self.ID, packet_size)
            # print('Added event', timestamp, 'at TTI', system_time, 'device', self.ID)
            self.event_chain.insert(e)
            IAT = self.sim_traffic.packet_inter_arrival_time()  # ms
            timestamp += IAT

    def packet_arrival(self, system_time):
        timestamp = system_time
        while True:
            IAT = self.sim_traffic.packet_inter_arrival_time()  # ms
            timestamp += IAT
            yield timestamp

    def set_indoor_field(self):
        if 'indoor' in self.sim_param.scenario.scenario.lower():
            return True
        else:
            return False

    def add_to_buffer(self, e):
        if len(self._buffer) >= self._max_buffer_len:
            self.dropped_packets += 1
        else:
            heapq.heappush(self._buffer, e)

    def _pop_from_buffer(self, timestamp):
        e = heapq.heappop(self._buffer)
        self.transmitted_packets += 1
        if not np.isnan(timestamp - e.packet_timestamp):
            self.delays.append(timestamp - e.packet_timestamp)
        return e

    def update_buffer(self, timestamp, volume):
        while volume >= self.sim_traffic.packet_size() and len(self._buffer):
            volume -= self.sim_traffic.packet_size()
            self._pop_from_buffer(timestamp)
        self.update_buffer_stats()

    def update_buffer_stats(self):
        self._buffer_len = len(self._buffer)

    def get_buffer_stats(self):
        return self._buffer_len

    # Added by Mert

    def bind_to_orchestrator(self, orchestrator):
        self.orchestrator = orchestrator
        self.orchestrator.connected_devices.append(self)

    def deploy_app(self, app_name):
        app = get_app(app_name)
        self.app = app
        for service in app.services:
            if service.is_deployed_at_edge:
                if service.is_shared:
                    self.orchestrator.request_assignment({"service": service, "user": self.ID})
                else:
                    self.orchestrator.request_deployment({"service": service, "user": self.ID})
            else:
                service_instance = service()
                app_instance = app()
                service_instance.app = app_instance
                service_instance.app_name = app.name
                self.deploy_service({"service": service_instance, "user": self.ID})

    def get_service_information(self):
        app_name = list(self.services.keys())[0]
        service_name = list(self.services[app_name].keys())[0]
        user_id = list(self.services[app_name][service_name].keys())[0]
        service = self.services[app_name][service_name][user_id][0]
        return {"app_name": app_name, "service_name": service_name, "service": service}
