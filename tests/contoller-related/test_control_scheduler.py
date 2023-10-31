import unittest

from runtime.Simulation import Simulation
from runtime.data_classes import States

class TestControlScheduler(unittest.TestCase):
    def setUp(self):

        config = {'always_los_flag': False,
                  'handover_algorithm': 'Normal'}
        self.sim = Simulation(config)
        self.sim.sim_params.scenario.max_num_devices_per_scenario = 3
        self.sim.sim_params.num_cells = 3
        self.sim.sim_params.num_controllers = 1
        self.sim.devices_per_scenario_ID = list(range(0, self.sim.sim_params.scenario.max_num_devices_per_scenario))
        self.sim.gNBs_per_scenario_ID = list(range(0, self.sim.sim_params.num_cells))
        self.controllers_per_scenario_ID = list(range(0, self.sim.sim_params.num_controllers))
        self.sim.initialize_RANenvironment()
        for i in range(len(self.sim.devices_per_scenario)):
            self.sim.devices_per_scenario[i].my_gnb = self.sim.gNBs_per_scenario[i]
        for i in range(len(self.sim.gNBs_per_scenario)):
            self.sim.controllers_per_scenario[0].gnbs.append(self.sim.gNBs_per_scenario[i])
        for i in range(len(self.sim.devices_per_scenario)):
            self.sim.ctrl_scheduler.users[0].append(self.sim.devices_per_scenario[i])
        for i in range(len(self.sim.controllers_per_scenario)):
            self.sim.ctrl_scheduler.sum_PRBs[i] = self.sim.controllers_per_scenario[i].available_resources

    def test_equal_scheduler(self):
        self.sim.ctrl_scheduler.SINRs = [[10, 10, 10]]
        self.sim.ctrl_scheduler.queued_data = [[1, 1, 1]]
        for i in range(len(self.sim.devices_per_scenario)):
            self.sim.devices_per_scenario[i].state = States.rrc_connected

        self.sim.ctrl_scheduler.schedule()

        self.assertEqual(self.sim.gNBs_per_scenario[0].available_resources, self.sim.sim_params.scenario.num_PRBs)
        self.assertEqual(self.sim.gNBs_per_scenario[1].available_resources, self.sim.sim_params.scenario.num_PRBs)
        self.assertEqual(self.sim.gNBs_per_scenario[2].available_resources, self.sim.sim_params.scenario.num_PRBs)

    def test_disconnected_ues(self):
        self.sim.ctrl_scheduler.SINRs = [[10, 10, 10]]
        self.sim.ctrl_scheduler.queued_data = [[1, 1, 1]]
        self.sim.devices_per_scenario[0].state = States.rrc_connected
        self.sim.devices_per_scenario[1].state = States.rrc_idle
        self.sim.devices_per_scenario[2].state = States.rrc_idle
        self.sim.ctrl_scheduler.schedule()

        self.assertGreater(self.sim.gNBs_per_scenario[0].available_resources, self.sim.gNBs_per_scenario[1].available_resources)
        self.assertGreater(self.sim.gNBs_per_scenario[0].available_resources, self.sim.gNBs_per_scenario[2].available_resources)
        self.assertEqual(sum(self.sim.gNBs_per_scenario[i].available_resources for i in range(3)), self.sim.ctrl_scheduler.sum_PRBs)

    def test_different_sinrs(self):
        self.sim.ctrl_scheduler.SINRs = [[30, 10, 10]]
        self.sim.ctrl_scheduler.queued_data = [[1, 1, 1]]
        for i in range(len(self.sim.devices_per_scenario)):
            self.sim.devices_per_scenario[i].state = States.rrc_connected
        self.sim.ctrl_scheduler.schedule()

        self.assertEqual(sum(self.sim.gNBs_per_scenario[i].available_resources for i in range(3)), self.sim.ctrl_scheduler.sum_PRBs)
        self.assertLess(self.sim.gNBs_per_scenario[0].available_resources, self.sim.gNBs_per_scenario[1].available_resources)
        self.assertLess(self.sim.gNBs_per_scenario[0].available_resources, self.sim.gNBs_per_scenario[2].available_resources)

    def test_different_buffers(self):
        self.sim.ctrl_scheduler.SINRs = [[10, 10, 10]]
        self.sim.ctrl_scheduler.queued_data = [[10, 1, 1]]
        for i in range(len(self.sim.devices_per_scenario)):
            self.sim.devices_per_scenario[i].state = States.rrc_connected
        self.sim.ctrl_scheduler.schedule()

        self.assertGreater(self.sim.gNBs_per_scenario[0].available_resources,
                           self.sim.gNBs_per_scenario[1].available_resources)
        self.assertGreater(self.sim.gNBs_per_scenario[0].available_resources,
                           self.sim.gNBs_per_scenario[2].available_resources)
        self.assertEqual(sum(self.sim.gNBs_per_scenario[i].available_resources for i in range(3)),
                         self.sim.ctrl_scheduler.sum_PRBs)


if __name__ == "__main__":
    unittest.main()
