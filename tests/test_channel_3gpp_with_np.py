import numpy as np
from device.Device import Device
from gnb.GnB import GnB
from channel.ChannelModel import ChannelUMiUMa
from runtime.Simulation import Simulation
from runtime.data_classes import States
from runtime.Scenarios import Outdoor


class ChannelTest:
    def __init__(self):
        self.num_cells = 1
        self.simulation = self.create_simulation_object()
        self.simulation.sim_params.num_cells = self.num_cells
        # UMi
        self.simulation.sim_params.scenario = Outdoor()
        self.simulation.sim_params.scenario.scenario = 'UMi'
        self.scenario_umi = Outdoor()
        self.channel_umi = ChannelUMiUMa(self.simulation, self.simulation.sim_params, print_flag=False)

    def create_simulation_object(self):
        simulation = Simulation()
        gnbs_pos = [[0, 0], [50, 30]]
        users_pos = [[-10, 5], [20, 15], [60, 55], [40, 35], [50, 10]]
        for i in range(len(users_pos)):
            x = users_pos[i][0]
            y = users_pos[i][1]
            user = Device(ID=i, transmit_power=23, x=x, y=y, simulation=simulation)
            user.state = States.rrc_connected
            simulation.devices_per_scenario.append(user)
        for i in range(self.num_cells):
            x = gnbs_pos[i][0]
            y = gnbs_pos[i][1]
            gnb = GnB(ID=i, x=x, y=y, simulation=simulation)
            simulation.gNBs_per_scenario.append(gnb)
        return simulation

    def test_break_point_distance_in_pathloss(self):
        channel = ChannelUMiUMa(self.simulation, self.simulation.sim_params, print_flag=False)
        self.simulation.sim_params.scenario.num_macro_gnbs = 1
        channel.init()
        assert channel.gnb_antenna_height[0][0] == 25
        assert channel.effective_env_height == 1
        assert channel.ue_antenna_height == 1.5
        assert channel.center_freq[0][0] == 0.5  # fixme
        assert channel.center_freq_multiplier == 10**9
        breakpoint_distance = channel.get_break_point_distance()
        assert round(breakpoint_distance[0][0], 1) == 80., breakpoint_distance  # todo: check this value

    def test_calc_distance(self):
        # done, checked by hand
        channel = ChannelUMiUMa(self.simulation, self.simulation.sim_params, print_flag=False)
        self.simulation.sim_params.scenario.num_macro_gnbs = 1
        channel.init()
        assert channel.gnb_antenna_height[0][0] == 25
        assert channel.effective_env_height == 1
        assert channel.ue_antenna_height == 1.5
        assert channel.center_freq[0][0] == 0.5  # fixme
        assert channel.center_freq_multiplier == 10 ** 9
        distance_2d_res = np.array([[11.18], [25.], [81.39], [53.15], [50.99]])
        distance_3d_res = np.array([[26.02], [34.31], [84.71], [58.11], [56.14]])
        distance_2d, distance_3d = channel.calc_distance_btw_users_gnbs()
        np.testing.assert_array_almost_equal(distance_2d, distance_2d_res, decimal=2)
        np.testing.assert_array_almost_equal(distance_3d, distance_3d_res, decimal=2)

    def test_calc_pathloss(self):
        x_y_gnb = [(0, 0), (5, 10)]
        x_y_user = [(11, 12), (-50, 100)]
        result = [52.9, 79]  # LOS
        result = [60.6, 87.5]  # NLOS
        channel = ChannelUMiUMa(self.simulation, self.simulation.sim_params, print_flag=False)
        self.simulation.sim_params.scenario.num_macro_gnbs = 1
        channel.init()
        assert channel.gnb_antenna_height[0][0] == 25
        assert channel.effective_env_height == 1
        assert channel.ue_antenna_height == 1.5
        assert channel.center_freq[0][0] == 0.5  # fixme
        assert channel.center_freq_multiplier == 10 ** 9
        _, distance_3d = channel.calc_distance_btw_users_gnbs()
        los_flag = np.zeros_like(distance_3d)
        final_pathloss_res = [[]]  # todo: calc by hand
        # final_pathloss = channel.calc_pathloss(distance_3d, los_flag) # does not work here
        # np.testing.assert_array_almost_equal(final_pathloss, final_pathloss_res, decimal=2)

    def test_calc_los_probability(self):
        channel = ChannelUMiUMa(self.simulation, self.simulation.sim_params, print_flag=False)
        self.simulation.sim_params.scenario.num_macro_gnbs = 1
        channel.init()
        _, distance_3d = channel.calc_distance_btw_users_gnbs()
        d_2dout = np.ones_like(distance_3d)
        # los_probability_res =   # todo: calc by hand
        # los_probability = channel.calc_los_probability(d_2dout=d_2dout)


if __name__ == "__main__":
    test = ChannelTest()
    test.test_break_point_distance_in_pathloss()
    test.test_calc_distance()
    test.test_calc_pathloss()
    test.test_calc_los_probability()