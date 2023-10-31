import unittest

import numpy as np
from device.Device import Device
from runtime.Simulation import Simulation
from runtime.EventChain import SimEvent

class TestDeviceBuffer(unittest.TestCase):
    def setUp(self):

        config = {'always_los_flag': False,
                  'handover_algorithm': 'Normal'}
        self.sim = Simulation(config)
        self.sim.initialize_RANenvironment()

        self.dev = Device(0, 0, 0, 0, self.sim)

    def test_event_order(self):
        ev = SimEvent(30, 1, self.sim.traffic_generator.packet_size())
        self.dev.add_to_buffer(ev)
        ev = SimEvent(10, 1, self.sim.traffic_generator.packet_size())
        self.dev.add_to_buffer(ev)
        ev = SimEvent(20, 1, self.sim.traffic_generator.packet_size())
        self.dev.add_to_buffer(ev)
        ev = self.dev._pop_from_buffer(0)

        self.assertEqual(ev.packet_timestamp, 10)

        ev = self.dev._pop_from_buffer(0)

        self.assertEqual(ev.packet_timestamp, 20)

        ev = self.dev._pop_from_buffer(0)

        self.assertEqual(ev.packet_timestamp, 30)

    def test_buffer_len(self):

        for _ in range(5):
            ev = SimEvent(np.random.randint(0, 100), 1, self.sim.traffic_generator.packet_size())
            self.dev.add_to_buffer(ev)

        #self.assertNotEqual(self.dev.get_buffer_stats(), 5)
        self.assertEqual(self.dev.get_buffer_stats(), 0)

        self.dev.update_buffer_stats()

        self.assertEqual(self.dev.get_buffer_stats(), 5)

        self.dev._pop_from_buffer(0)
        self.dev.update_buffer_stats()

        self.assertEqual(self.dev.get_buffer_stats(), 4)

    def test_update_buffer(self):
        for _ in range(4):
            ev = SimEvent(np.random.randint(0, 100), 1, self.sim.traffic_generator.packet_size())
            self.dev.add_to_buffer(ev)
        self.dev.update_buffer(0, self.sim.traffic_generator.packet_size() * 3.5)
        self.dev.update_buffer_stats()

        self.assertEqual(self.dev.get_buffer_stats(), 1)

    def test_max_buffer_len(self):
        for _ in range(self.dev._max_buffer_len + 100):
            ev = SimEvent(np.random.randint(0, 100), 1, self.sim.traffic_generator.packet_size())
            self.dev.add_to_buffer(ev)
        self.dev.update_buffer_stats()
        self.assertEqual(self.dev.get_buffer_stats(), self.dev._max_buffer_len)
        self.assertEqual(self.dev.dropped_packets, 100)



if __name__ == "__main__":
    unittest.main()

