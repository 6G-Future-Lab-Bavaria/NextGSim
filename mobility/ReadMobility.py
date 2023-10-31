# @Author: Anna Prado
# @Date: 2020-11-15
# @Email:  anna.prado@tum.de
# @Last modified by: Alba Jano

import scipy.io
import matplotlib.pyplot as plt
import numpy as np
from random import randint
from tabulate import tabulate
np.set_printoptions(suppress=True)


def generate_color_list(n):
    colors = []
    for i in range(n):
        colors.append('#%06X' % randint(0, 0xFFFFFF))
    return colors


class ReadMobility:
    def __init__(self, filename):
        self.num_pauses = 0
        self.filename = filename
        self.time_steps = None
        self.num_users = None
        self.measurement_interval = 60  # sec  # hardcoded

    def check_if_any_user_paused(self, x0, y0, x1, y1):
        # round the position, otherwise all the numbers are different because they are floats
        x0 = round(x0, 2)
        y0 = round(y0, 2)
        x1 = round(x1, 2)
        y1 = round(y1, 2)
        if (x0, y0) == (x1, y1):
            self.num_pauses += 1
            # print(f"User: {x0},{y0} ----> {x1},{y1}")

    @staticmethod
    def drawArrow(A, B, color):
        plt.arrow(A[0], A[1], B[0] - A[0], B[1] - A[1],
                  head_width=2, length_includes_head=True, color=color)

    def get_SLAW_params(self, mat):
        min_pause = float(mat['MIN_PAUSE'])
        max_pause = float(mat['MAX_PAUSE'])
        beta = float(mat['beta'])
        dist_alpha = float(mat['dist_alpha'])
        size_max = int(mat['size_max'])
        num_wp = int(mat['n_wp'])
        hours = float(mat['Thours'])
        v_Hurst = float(mat['v_Hurst'])
        B_range = float(mat['B_range'])
        t_gap = int(mat['t_gap'])
        velocity = float(mat['velocity'])
        self.print_slaw_params(velocity, t_gap, v_Hurst, size_max, min_pause, max_pause, hours, num_wp, B_range, dist_alpha, beta)

    @staticmethod
    def print_slaw_params(velocity, t_gap, v_Hurst, size_max, min_pause, max_pause, hours, num_wp, B_range, dist_alpha, beta):
        print("\nSLAW mobility model parameters:")
        print(tabulate([[velocity, t_gap, v_Hurst, size_max, min_pause, max_pause, hours, num_wp, B_range, dist_alpha, beta]],
            headers=["Velocity (m/s)", "Sampling freq (sec)", "Hurst", "Size max (m)", "Min pause (sec)", "Max Pause (sec)", "Duration (hours)", "Num waypoins", "B range (m)", "alpha", "beta"]))

    def read_SLAW_output(self, num_users, start_offset, num_time_steps):
        self.num_users = num_users
        self.time_steps = num_time_steps
        mat = scipy.io.loadmat(self.filename)
        self.get_SLAW_params(mat)
        total_num_users = mat['trace'].shape[0]
        total_time_steps = mat['trace'].shape[1]

        if not self.num_users:
            self.num_users = total_num_users
        if not self.time_steps:
            self.time_steps = total_time_steps

        msg = f'SLAW data: number of users = {total_num_users}, number of time steps = {total_time_steps}'
        print(msg)
        X = mat['trace'][:, :, 0]
        Y = mat['trace'][:, :, 1]
        # T = mat['trace'][:, :, 2]
        return X[:self.num_users, start_offset:self.time_steps], Y[:self.num_users, start_offset:self.time_steps]

    def plot_mobility(self, X, Y, num_users):
        colors = generate_color_list(num_users+1)
        for user_id in range(num_users):
            plt.plot(X[user_id, :], Y[user_id, :], color=colors[user_id])
            plt.scatter(X[user_id, 0], Y[user_id, 0], color=colors[user_id], marker='*')
            # for t in range(self.time_steps - 2):
            #     self.drawArrow((X[user_id, t], Y[user_id, t]), (X[user_id, t + 1], Y[user_id, t + 1]),
            #                         color=colors[user_id])
            #     self.check_if_any_user_paused(X[user_id, t], Y[user_id, t], X[user_id, t + 1], Y[user_id, t + 1])
        plt.savefig('results/slaw_mobility.png')

    def get_speed(self, X, Y):
        speed_per_ue_dict = {}
        num_ues = len(X)
        for ue_id in range(num_ues):
            X_diff = X[ue_id, 1:] - X[ue_id, :-1]
            Y_diff = Y[ue_id, 1:] - Y[ue_id, :-1]
            speed = np.sqrt(X_diff**2 + Y_diff**2) / self.measurement_interval
            mean = np.mean(speed)
            std = np.std(speed)
            speed_per_ue_dict[ue_id] = (mean, std)
        return speed_per_ue_dict


def main():
    filename = 'mobility_traces/slaw_data_1000m/vary_tgap/tgap_1.mat'
    t_gap = 1  # s
    time_steps = int(1 * 3600 / t_gap)  # 1h
    num_users = 20

    readmobility = ReadMobility(filename)
    X, Y, T = readmobility.read_SLAW_output(num_users, time_steps)
    print(X.shape, Y.shape, T.shape)

    readmobility.plot_mobility(X, Y, num_users)
    # for ue_id in range(num_users-1):
    #     assert T[ue_id, :].all() == T[ue_id+1, :].all()
    speed = readmobility.get_speed(X, Y)
    print(f"UE mean and std speed (m/s) {speed}")
    print(f"Number of pauses made by {readmobility.num_users} users over {readmobility.time_steps} time steps is {readmobility.num_pauses}")


if __name__ == '__main__':
    main()

