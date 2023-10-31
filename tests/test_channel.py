import matplotlib.pyplot as plt
import numpy as np
from channel.ChannelModel import ChannelUMiUMa, ChannelIndoor
from runtime.Scenarios import Outdoor, Indoor
from runtime.Simulation import Simulation
from device.Device import Device
from gnb.GnB import GnB
from runtime.data_classes import States

NUM_CELLS = 2
NUM_USERS = 5


class TestChannel:
    def __init__(self):
        self.simulation = None

    def create_simulation_object(self):
        self.simulation = Simulation()
        gnbs_pos = [[0, 0], [50, 30]]
        users_pos = [[-10, 5], [20, 15], [60, 55], [40, 35], [50, 10]]
        for i in range(NUM_USERS):
            x = users_pos[i][0]
            y = users_pos[i][1]
            user = Device(ID=i, transmit_power=23, x=x, y=y, simulation=self.simulation)
            user.state = States.rrc_connected
            self.simulation.devices_per_scenario.append(user)
            # print(f"User {device.ID}: x = {device.x}, y = {device.y}")
        for i in range(NUM_CELLS):
            x = gnbs_pos[i][0]
            y = gnbs_pos[i][1]
            gnb = GnB(ID=i, x=x, y=y, simulation=self.simulation)
            self.simulation.gNBs_per_scenario.append(gnb)
            # print(f"gNB {gnb.ID}: x = {gnb.x}, y = {gnb.y}")

    def visualize(self):
        for user in self.simulation.devices_per_scenario:
            plt.scatter(user.x, user.y, label=f"user {user.ID}", s=15, marker='o')
        for gnb in self.simulation.gNBs_per_scenario:
            plt.scatter(gnb.x, gnb.y, label=f"gnb {gnb.ID}", s=60, marker='*')
        plt.legend()
        plt.show()

    def test_calc_distance_users_gnbs_2d(self):
        self.create_simulation_object()
        # Indoor
        scenario_indoor = Indoor()
        channel_indoor = ChannelIndoor(self.simulation, scenario_indoor, 'UL', print_flag=False)

        distance_users_gnbs_2d = channel_indoor.calc_distance_users_gnbs_2d()
        expected_distance = np.array([[11, 65], [25, 34], [81, 27], [53, 11], [51, 20]])
        distance_users_gnbs_2d = np.round(distance_users_gnbs_2d)
        assert np.array_equal(expected_distance, distance_users_gnbs_2d)

        # Outdoor
        scenario_umi = Outdoor()
        channel_umi = ChannelUMiUMa(self.simulation, scenario_umi, 'UL', print_flag=False)
        distance_users_gnbs_2d = channel_umi.calc_distance_users_gnbs_2d()
        expected_distance = np.array([[11, 65], [25, 34], [81, 27], [53, 11], [51, 20]])
        distance_users_gnbs_2d = np.round(distance_users_gnbs_2d)
        assert np.array_equal(expected_distance, distance_users_gnbs_2d)

    def test_calc_distance_users_gnbs_3d(self):
        # 2D and 3D distance is almost the same, the difference is less than 1 m for Indoor
        # for antenna height 3 m and device height 1 m
        self.create_simulation_object()
        # Indoor
        scenario_indoor = Indoor()
        channel_indoor = ChannelIndoor(self.simulation, scenario_indoor, 'UL', print_flag=False)
        assert channel_indoor.gnb_antenna_height == 3, channel_indoor.ue_antenna_height == 1
        distance_users_gnbs_2d = channel_indoor.calc_distance_users_gnbs_2d()
        distance_users_gnbs_3d = channel_indoor.calc_distance_users_gnbs_3d(distance_users_gnbs_2d)
        expected_distance = np.array([[11, 65], [25, 34], [81, 27], [53, 11], [51, 20]])
        distance_users_gnbs_3d = np.round(distance_users_gnbs_3d)
        assert np.array_equal(expected_distance, distance_users_gnbs_3d)

        # Outdoor
        scenario_umi = Outdoor()
        channel_umi = ChannelUMiUMa(self.simulation, scenario_umi, 'UL', print_flag=False)
        assert channel_umi.gnb_antenna_height == 10, channel_umi.ue_antenna_height == 1.5
        distance_users_gnbs_2d = channel_umi.calc_distance_users_gnbs_2d()
        distance_users_gnbs_3d = channel_umi.calc_distance_users_gnbs_3d(distance_users_gnbs_2d)
        expected_distance = np.array([[14, 66], [26, 35], [82, 28], [54, 14], [52, 22]])
        distance_users_gnbs_3d = np.round(distance_users_gnbs_3d)
        assert np.array_equal(expected_distance, distance_users_gnbs_3d)

    def test_calc_pathloss(self):
        self.create_simulation_object()
        # Indoor
        scenario_indoor = Indoor()
        channel_indoor = ChannelIndoor(self.simulation, scenario_indoor, 'UL', print_flag=False)
        assert channel_indoor.gnb_antenna_height == 3, channel_indoor.ue_antenna_height == 1
        distance_users_gnbs_2d = channel_indoor.calc_distance_users_gnbs_2d()
        distance_users_gnbs_3d = channel_indoor.calc_distance_users_gnbs_3d(distance_users_gnbs_2d)
        # print(distance_users_gnbs_3d)
        # LoS
        pathloss_los = channel_indoor.calc_pathloss(distance_users_gnbs_3d, los_flag=True)
        pathloss_los = np.round(pathloss_los)
        expected_pathloss_los = np.array([[45, 58], [51, 53], [59, 51], [56, 45], [56, 49]])
        assert np.array_equal(expected_pathloss_los, pathloss_los)
        # NLoS
        pathlos_no_los = channel_indoor.calc_pathloss(distance_users_gnbs_3d, los_flag=False)
        pathlos_no_los = np.round(pathlos_no_los)
        expected_pathloss_no_los = np.array([[50, 79], [63, 68], [83, 65], [76, 50], [75, 60]])
        assert np.array_equal(expected_pathloss_no_los, pathlos_no_los)

        # Outdoor
        scenario_umi = Outdoor()
        channel_umi = ChannelUMiUMa(self.simulation, scenario_umi, 'UL', print_flag=False)
        assert channel_umi.gnb_antenna_height == 10, channel_umi.ue_antenna_height == 1.5
        distance_users_gnbs_2d = channel_umi.calc_distance_users_gnbs_2d()
        distance_users_gnbs_3d = channel_umi.calc_distance_users_gnbs_3d(distance_users_gnbs_2d)
        # LoS
        pathloss_los = channel_umi.calc_pathloss(distance_users_gnbs_3d, los_flag=True)
        pathloss_los = np.round(pathloss_los)
        # todo: calc these values by hand
        expected_pathloss_los = np.array([[50, 65], [56, 59], [67, 57], [63, 50], [62, 54]])
        # print(pathloss_los)
        assert np.array_equal(expected_pathloss_los, pathloss_los)

    def test_outdoor_to_indoor_penetration_loss(self):
        self.create_simulation_object()
        self.simulation.sim_params.num_cells = 2
        # Indoor
        scenario_indoor = Indoor()
        channel_indoor = ChannelIndoor(self.simulation, scenario_indoor, 'UL', print_flag=False)
        O2I_penetration_loss = channel_indoor.outdoor_to_indoor_penetration_loss(distance_indoor=1)
        assert np.mean(O2I_penetration_loss) == 20.5
        assert O2I_penetration_loss.shape == (len(self.simulation.devices_per_scenario), len(self.simulation.gNBs_per_scenario))


def main():
    test = TestChannel()
    test.test_calc_distance_users_gnbs_3d()
    test.test_calc_pathloss()
    test.test_outdoor_to_indoor_penetration_loss()
    print("done")


if __name__ == "__main__":
    main()
