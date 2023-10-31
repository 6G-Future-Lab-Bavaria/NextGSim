import numpy as np
from runtime.data_classes import MobilityModels, MeasurementParams
from mobility.random_waypoint import get_next_user_position


class Mobility:
    def __init__(self, simulation):
        self.simulation = simulation
        self.X_mobility = {}
        self.Y_mobility = {}

    def update_user_position(self, user):
        if self.simulation.sim_params.hardcoded_initial_setup:
            self.simulation.hardcoded_indoor_user_movement(user)
        else:
            if self.simulation.sim_params.with_mobility:
                positon_index = int(self.simulation.TTI / MeasurementParams.update_ue_position_gap)
                user.x = self.X_mobility[user.ID][positon_index]
                user.y = self.Y_mobility[user.ID][positon_index]
                assert type(user.x) in [float, np.float64], type(user.x)

    def set_positions(self):
        if self.simulation.sim_params.with_mobility:
            if self.simulation.sim_params.mobility_model == MobilityModels.random_waypoint:
                self.set_positions_rwp()
            elif self.simulation.sim_params.mobility_model == MobilityModels.slaw:
                # todo
                raise NotImplementedError
            else:
                # todo
                raise NotImplementedError

                min_velocity, max_velocity, mean_velocity = self.calc_actual_user_velocity()
                self.ran_simulation.visualization.user_speed_metrics = [min_velocity, max_velocity, mean_velocity]
        else:
            raise NotImplementedError  # todo

    def set_positions_rwp(self):
        num_user_positions = self.simulation.sim_params.num_TTI / MeasurementParams.update_ue_position_gap
        x_max = self.simulation.sim_params.scenario.x_max
        y_max = self.simulation.sim_params.scenario.y_max
        for user in self.simulation.devices_per_scenario:
            user_id = user.ID
            self.X_mobility[user_id], self.Y_mobility[user_id] = \
                get_next_user_position(num_user_positions, x_max, y_max, user.x,user.y)

    def hardcoded_indoor_user_movement(self, user):
        if self.simulation.setup.move_right:
            user.x += 1
            if user.x >= 95:
                self.simulation.setup.move_right = False
        else:
            user.x -= 1
            if user.x <= -20:
                self.simulation.setup.move_right = True

    def calc_actual_user_velocity(self):
        velocities = []
        for tti in range(len(self.X_mobility[0]) - 1):
            v = np.sqrt((self.X_mobility[0][tti + 1] - self.X_mobility[0][tti]) ** 2 +
                        (self.Y_mobility[0][tti + 1] - self.Y_mobility[0][tti]) ** 2)
            velocities.append(np.mean(v))
        mean_velocity = round(np.mean(velocities, axis=0), 1)
        min_velocity = round(float(min(velocities)), 1)
        max_velocity = round(float(max(velocities)), 1)
        print(f"Velocity: min={min_velocity}, max={max_velocity}, mean={mean_velocity} "
              f"meters per {MeasurementParams.update_ue_position_gap / 10 ** 3} s")
        return min_velocity, max_velocity, mean_velocity

    # def init_mobility_slaw(self):
    #     if self.ran_simulation.sim_params.with_mobility:
    #         if self.ran_simulation.sim_params.mobility_model == MobilityModels.slaw:
    #             generate_mob_traces_slaw(self)
    #             readmobility = ReadMobility(self.ran_simulation.sim_params.scenario.mobility_traces_filename)
    #             end = int(self.ran_simulation.sim_params.num_TTI / self.ran_simulation.sim_params.t_gap_slaw)
    #             num_users = self.ran_simulation.sim_params.scenario.max_num_devices_per_scenario
    #             start_offset = self.ran_simulation.sim_params.start_offset
    #             end += start_offset
    #             self.X_mobility, self.Y_mobility = readmobility.read_SLAW_output(num_users, start_offset, end)
    #             del readmobility
    #
    # def init_mobility_room_trace(self):
    #     folder = "mobility/mobility_traces/lab_room_mobility"
    #     data = pd.read_csv(os.path.join(folder, "traces.csv"))
    #     self.X_mobility, self.Y_mobility = [data["x"]], [data["y"]]
    #     # data.drop(['x', 'y'], axis = 1)  # how to drop x and y columns
    #     self.blockage_info = data
    #
    # def init_mobility_with_pred(self):
    #     if self.sim_params.with_mobility:
    #         if self.sim_params.mobility_model == MobilityModels.slaw:
    #             if 'predictions' not in self.sim_params.scenario.mobility_traces_filename:
    #                 assert 0, 'This func is only called on pred datasets'
    #             readmobility = ReadPredictionTraces(self.sim_params)
    #             testX, testY, testYPredict = readmobility.read_mobility_traces()
    #             self.X_mobility, self.Y_mobility = testX[:, :, 0], testX[:, :, 1]
    #
    #             if self.sim_params.handover_algorithm in \
    #                     [HandoverAlgorithms.echo_with_known_tr, HandoverAlgorithms.echo_with_current_look_ahead]:
    #                 self.handover.X_mobility, self.handover.Y_mobility = testY[:, :, 0], testY[:, :, 1]
    #                 del testYPredict
    #             elif self.sim_params.handover_algorithm == HandoverAlgorithms.echo_with_pred_tr:
    #                 self.handover.X_mobility, self.handover.Y_mobility = testYPredict[:, :, 0], testYPredict[:, :, 1]
    #                 del testY
    #             elif self.sim_params.handover_algorithm == HandoverAlgorithms.echo_with_look_ahead:
    #                 self.handover.X_mobility, self.handover.Y_mobility = testYPredict[:, :, :, 0], testYPredict[:, :, :,
    #                                                                                                1]
    #                 self.handover.X_mobility, self.handover.Y_mobility = \
    #                     testYPredict[:, :, :, 0], testYPredict[:, :, :, 1]
    #                 del testY
    #
    #             else:
    #                 del testY
    #                 del testYPredict
    #             del readmobility