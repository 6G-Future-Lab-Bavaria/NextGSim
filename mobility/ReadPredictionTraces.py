import pickle as pkl
import numpy as np
from runtime.data_classes import HandoverAlgorithms


class ReadPredictionTraces:
    def __init__(self, sim_params):
        self.sim_params = sim_params
        self.time_steps = None
        self.num_users = None

    def read_mobility_traces(self):

        """
        testX: actual trajectory of the users (DL model input) for the simulator
        testY: the known future trajectory (ground truth label) for ECHO with known trajectory
        testYPredict: the predicted values (model prediction) for ECHO with predictions
        X and Y here relate to DL, not to X and Y positions.
        """

        filename = self.sim_params.scenario.mobility_traces_filename
        end = int(self.sim_params.num_TTI / self.sim_params.t_gap_slaw)
        num_users = self.sim_params.scenario.max_num_devices_per_scenario
        start_offset = self.sim_params.start_offset
        end += start_offset
        user_id = self.sim_params.user_id

        if self.sim_params.handover_algorithm in \
                [HandoverAlgorithms.echo_with_look_ahead, HandoverAlgorithms.echo_with_current_look_ahead]:
            self.sim_params.look_ahead = 5
        look_ahead = self.sim_params.look_ahead


        # assert start_offset == 0, f"Start offset must be zero or small, not {start_offset}. Pred set is only 2.7h"
        with open(filename, 'rb') as file_pi:
            testX, testY, testYPredict = pkl.load(file_pi)
        # Drop look_back and set look_ahead
        testX = testX[:, 0, :]
        if look_ahead:
            testY = testY[:, :look_ahead, :]
            testYPredict = testYPredict[:, :look_ahead, :]
            assert testY.shape[2] != look_ahead, testY.shape
            assert testYPredict.shape[2] != look_ahead, testYPredict.shape
        else:
            testY = testY[:, 0, :]
            testYPredict = testYPredict[:, 0, :]

        # Reshape to have 30 users
        testX = np.reshape(testX, (30, testX.shape[0] // 30, 2))
        if look_ahead:
            testY = np.reshape(testY, (30, testY.shape[0] // 30, look_ahead, 2))
            testYPredict = np.reshape(testYPredict, (30, testYPredict.shape[0] // 30, look_ahead, 2))
        else:
            testY = np.reshape(testY, (30, testY.shape[0] // 30, 2))
            testYPredict = np.reshape(testYPredict, (30, testYPredict.shape[0] // 30, 2))


        # Take required num_users and num_TTIs
        testX = testX[user_id:num_users+user_id, start_offset:end, :]
        testY = testY[user_id:num_users+user_id, start_offset:end, :]
        testYPredict = testYPredict[user_id:num_users+user_id, start_offset:end, :]
        # print(f"X (model input) has shape: {testX.shape}")
        # print(f"Y (ground truth) has shape: {testY.shape}")
        # print(f"YPredict (prediction) has shape: {testYPredict.shape}")
        return testX, testY, testYPredict