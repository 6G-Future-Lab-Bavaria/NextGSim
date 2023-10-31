""" Implemented from:
3GPP Standardized 5G Channel Model for IIoT Scenarios: A Survey
https://www.etsi.org/deliver/etsi_tr/138900_138999/138901/16.01.00_60/tr_138901v160100p.pdf
"""

import numpy as np
from itertools import product
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import random
import warnings


class ChannelModelInF():
    """
    The indoor factory (InF) scenario focuses on factory halls of varying sizes and with varying levels of density of
    "clutter", e.g. machinery, assembly lines, memory shelves, etc
    """

    def __init__(self, simulation, simparams):
        self.LOS = True
        self.NLOS = False
        self.fcGHz = 3
        self.simulation = simulation
        self.sim_params = simparams
        self.scenario = self.sim_params.scenario
        self.user_coordinates = self.simulation.user_coordinates
        self.num_users = len(self.user_coordinates)
        self.num_RB = self.simulation.sim_params.scenario.num_PRBs
        self.PRB_bandwidth = self.simulation.sim_params.scenario.PRB_bandwidth * 10 ** 3  # Hz
        self.noise_figure = 7
        self.num_BSs = len(self.scenario.gNB_coordinates)
        self.num_samples = self.num_users * self.num_RB * self.num_BSs
        self.distance_2D = self.calc_dist_2d()
        # self.distance_2D =np.array([range(0, 15)])
        self.distance_3D = self.calc_dist_3d()
        self.center_freq = self.scenario.center_freq
        self.k_subsce = None
        self.d_clutter = self.scenario.clutter_size  # clutter size
        self.r = self.scenario.clutter_density  # clutter density
        self.height_BS = self.scenario.gNB_height  # antenna height of BS
        self.height_UE = self.scenario.UE_height  # antenna height of UT
        self.h_c = self.scenario.clutter_height  # clutter hight
        self.V = self.scenario.hall_width * self.scenario.hall_length * self.scenario.room_height  # factory volume
        self.S = 2 * (self.scenario.hall_width * self.scenario.room_height) + \
                 2 * (self.scenario.hall_length * self.scenario.room_height) + \
                 2 * (
                             self.scenario.hall_width * self.scenario.hall_length)  # sum of surface aea of wall, ceiling and floor
        self.los_probability = np.zeros((self.num_BSs, self.num_users, self.num_RB))
        self.pathloss_los = np.zeros((self.num_BSs, self.num_users, self.num_RB))
        self.pathloss_nlos = np.zeros((self.num_BSs, self.num_users, self.num_RB))
        self.pathloss = np.zeros((self.num_BSs, self.num_users, self.num_RB))
        self.SNR = np.zeros((self.num_BSs, self.num_users, self.num_RB))
        self.m_numOfCluster = 25
        self.m_raysPerCluster = 20
        self.m_uLgDS = np.log10(26.0 * (30.0) + 14.0) - 9.35
        self.m_sigLgDS = 0.15
        self.m_uLgASD = 1.56
        self.m_sigLgASD = 0.25
        self.m_uLgASA = -0.18 * np.log10(1 + self.fcGHz) + 1.781
        self.m_sigLgASA = 0.12 * np.log10(1 + self.fcGHz) + 0.2
        self.m_uLgZSA = -0.2 * np.log10(1 + self.fcGHz) + 1.5
        self.m_sigLgZSA = 0.35
        self.m_uLgZSD = 1.35
        self.m_sigLgZSD = 0.35
        self.m_offsetZOD = 0
        self.m_cDS = 3.91 * 10 ** (-9)
        self.m_cASD = 5
        self.m_cASA = 8
        self.m_cZSA = 9
        self.m_uK = 7
        self.m_sigK = 8
        self.m_rTau = 2.7
        self.m_uXpr = 12
        self.m_sigXpr = 6
        self.m_perClusterShadowingStd = 4

    def calc_dist_2d(self):
        distance_users_gnbs_2d = np.zeros((self.num_BSs, self.num_users, self.num_RB), float)
        for gNB in range(self.num_BSs):
            distance = np.sqrt(
                (self.user_coordinates[:, 0] - self.scenario.gNB_coordinates[gNB, 0]) ** 2 +
                (self.user_coordinates[:, 1] - self.scenario.gNB_coordinates[gNB, 1]) ** 2)
            distance_users_gnbs_2d[gNB, :, :] = np.tile(distance, (self.num_RB, 1)).transpose()
        return distance_users_gnbs_2d

    def calc_dist_3d(self):
        distance_users_PRB_gnbs_3d = np.zeros((self.num_BSs, self.num_users, self.num_RB), float)
        for gNB in range(self.num_BSs):
            if self.scenario.gNB_height > 10.0:
                warnings.warn("[Warning - Channel Model InF] The LOS probability was derived assuming BS antenna \
                heights of <10 m")
            distance = np.sqrt(
                self.distance_2D[gNB, :, 1] ** 2 + (self.scenario.UE_height - self.scenario.gNB_height) ** 2)
            if distance.any() < 1.0 or distance.any() > 600.0:
                warnings.warn("[Warning - Channel Model InF] The 3D distance is outside the validity range, \
                the pathloss value may not be accurate")
            distance_users_PRB_gnbs_3d[gNB, :, :] = np.tile(distance, (self.num_RB, 1)).transpose()
        return distance_users_PRB_gnbs_3d

    def generate_test_users(self):
        """ We will have just the device coordinates and not device objects in order to test the channel model"""
        a = np.random.uniform(-20, 20, size=(5000, 2))
        x_coordinates = random.sample(range(1, 300), 20)
        y_coordinates = random.sample(range(1, 300), 20)
        z_coordinates = [self.scenario.UE_height]
        user_coordinates_tuple = list(product(x_coordinates, y_coordinates, z_coordinates))
        user_coordinates = np.array(list(map(list, user_coordinates_tuple)))
        return user_coordinates

    def calc_rician_fading(self):
        """
        Rician fading envelope is simulated for various non centrality parameter )s) and sigma square = 1, considering
        two Gausian random variables X and Y. The random variables X and Y used to generate the Rician distribution
        differ only in their meas. Their variances remain the same, For the convenience, one of the Gaussian random
        variable (say X) is generated with mean=s (the non centrality parameter) and variance= sigma square. The other
        radom variable say Y is generated with mean =0 and variance=sigma 2
        Original code in book: Simulation of Digital Communication systems using Matlab
        :return: rician fading values
        """
        sigma = 1  # Variance of underlying Gaussian Variables
        s = 2  # Non-Centrality Parameter
        X = s + sigma * np.random.randn(1, self.num_samples)  # Gaussian RV with mean=s and given sigma
        Y = 0 + sigma * np.random.randn(1, self.num_samples)  # Gaussian RV with mean=0 and same sigma as Y
        rician_fading = (20 * np.log10(np.sqrt(X ** 2 + Y ** 2))).reshape((self.num_BSs, self.num_users, self.num_RB))
        return rician_fading

    def calc_pathloss_los(self):
        # problems will be caused when the distance is 0
        # TODO: shadowing changes for downlink channel model
        shadow_fading = np.random.normal(0, self.scenario.LOS_sigma, self.num_samples).reshape(
            (self.num_BSs, self.num_users, self.num_RB))
        self.pathloss_los = self.scenario.LOS_beta + 10 * self.scenario.LOS_alpha * np.log10(
            self.distance_3D) + 10 * self.scenario.LOS_gamma * np.log10(
            self.center_freq) - shadow_fading  # - self.calc_rician_fading()#
        return self.pathloss_los

    def calc_pathloss_nlos(self):
        shadow_fading = np.random.normal(0, self.scenario.NLOS_sigma, self.num_samples).reshape(
            (self.num_BSs, self.num_users, self.num_RB))
        self.pathloss_nlos = self.scenario.NLOS_beta + 10 * self.scenario.NLOS_alpha * np.log10(
            self.distance_3D) + 10 * self.scenario.NLOS_gamma * np.log10(self.center_freq) + shadow_fading
        if self.scenario.subscenario == 'SL' or self.scenario.subscenario == 'SH' or self.scenario.subscenario == 'DH':
            self.pathloss_nlos = np.maximum(self.pathloss_nlos, self.pathloss_los)
        elif self.scenario.subscenario == 'DL':
            pathloss_nlos_SL = 33 + 25.5 * np.log10(self.distance_3D) + 20 * np.log10(
                self.center_freq) + np.random.normal(0, 5.7, self.num_samples).reshape(
                (self.num_BSs, self.num_users, self.num_RB)) - self.calc_rayleigh_fading()
            self.pathloss_nlos = np.maximum(np.maximum(self.pathloss_nlos, self.pathloss_los), pathloss_nlos_SL)
        else:
            exit('Wrong subscenario for Indoor Factory scenario.')
        return self.pathloss_nlos

    def calc_rayleigh_fading(self):
        # TODO: Check if the implementation of the rayleigh fading is correct
        """
        The delays associated with different signal paths in a multipath fading channel change in an unpredictable
        manner and can only be characterized statistically. When there are a large number of paths, the central limit
        theorem can be applied to model the time-variant impulse response of thechannel as a complex-valued Gaussian
        random process. When the impulse response is modeled as azero-mean complex-valued Gaussian process, the channel
        is said to be a Rayleigh fading channel.

        Here the Rayleigh Fading model is assumed to have only two multipath components X(t) and Y(t).
        Rayleigh Fading can be obtained from zero-mean complex Gaussian processes (X(t) and Y(t) ).
        Simply adding the two Gaussian Random variables and taking the square root (envelope) gives a
        single tap Rayleigh distributed process. The phase of such random variable follows uniform
        distribution

        :return: Rayleigh fading values
        """
        #  Independent Gaussian random variables with zero mean and unit variance
        X = np.random.randn(1, self.num_samples)
        Y = np.random.randn(1, self.num_samples)
        rayleigh_fading = (20 * np.log10(np.sqrt(X ** 2 + Y ** 2))).reshape((self.num_BSs, self.num_users, self.num_RB))
        return rayleigh_fading

    def calc_los_probability(self):
        """ The LOS probability model is used to determine whether the state of a channel is LOS or NLOS
        at e certain distance. The model considers the antenna height and clutter density at the same time.
        It is based on the deployment assumption rather than measurement data or ray-tracing ran_simulation results.
        """
        if self.scenario.gNB_height >= 10:
            self.los_probability = np.ones((self.num_BSs, self.num_users, self.num_RB))
        else:
            if self.scenario.subscenario == 'SL' or self.scenario.subscenario == 'DL':
                if self.scenario.clutter_density < 0.04:
                    self.d_clutter = 10
                elif self.scenario.clutter_density > 0.4:
                    self.d_clutter = 2
                self.k_subsce = - (self.d_clutter / np.log2((1 - self.r)))
            elif self.scenario.subscenario == 'SH' or self.scenario.subscenario == 'DH':
                if self.h_c > 10.0:
                    warnings.warn("[Warning - Channel Model InF] Clutter hight does not apply")
                if self.height_UE > self.h_c:
                    warnings.warn("[Warning - Channel Model InF] The hight of the UE  should be smaller that clutter")
                    self.los_probability = np.zeros((self.num_BSs, self.num_users, self.num_RB))
                if self.scenario.clutter_density <= 0.0:
                    self.los_probability = np.ones((self.num_BSs, self.num_users, self.num_RB))
                if self.scenario.clutter_density < 0.04:
                    self.d_clutter = 10
                elif self.scenario.clutter_density > 0.4:
                    self.d_clutter = 2
                self.k_subsce = - (self.d_clutter / np.log2((1 - self.r))) * (
                        (self.height_BS - self.height_UE) / (self.h_c - self.height_UE))
            else:
                exit('Wrong subscenario for Indoor Factory scenario.')
        los_probability_temp = np.exp(-(np.array(self.distance_2D)) / self.k_subsce)
        self.los_probability = np.where(los_probability_temp >= 0.5, 1, 0)
        return self.los_probability

    def gen_cluster_delay(self):
        K_factor = LSPs[1] * self.m_sigK + self.m_uK
        DS = 10 ** (LSPs[2] * self.m_sigLgDS + self.m_uLgDS)
        ASD = 10 ** (LSPs[3] * self.m_sigLgASD + self.m_uLgASD)
        ASA = 10 ** (LSPs[4] * self.m_sigLgASA + self.m_uLgASA)
        ZSD = 10 ** (LSPs[5] * self.m_sigLgZSD + self.m_uLgZSD)
        ZSA = 10 ** (LSPs[6] * self.m_sigLgZSA + self.m_uLgZSA)
        ASD = min(ASD, 104.0)
        ASA = min(ASA, 104.0)
        ZSD = min(ZSD, 52.0)
        ZSA = min(ZSA, 52.0)
        clusterDelay = []
        minTau = 100.0
        for c in range(0, len(self.m_numOfCluster)):
            tau = -1 * self.m_rTau * DS * np.log10(random.uniform(0, 1))
            if minTau > tau:
                minTau = tau
            clusterDelay.append(tau)

        for c in range(0, len(self.m_numOfCluster)):
            clusterDelay[c] -= minTau
        clusterDelay.sort()

        clusterPower = []
        powerSum = 0
        for c in range(0, len(self.m_numOfCluster)):
            power = np.exp(-1 * clusterDelay[c] * (self.m_rTau - 1) / (self.m_rTau * DS)) * 10 ** (
                        -1 * random.uniform(0, 1) * (self.m_perClusterShadowingStd / 10))
            powerSum += power
            clusterPower.append(power)

        powerMax = 0
        for c in range(0, len(self.m_numOfCluster)):
            clusterPower[c] = clusterPower[c] / powerSum

        clusterPowerForAngles = []
        K_linear = 10 ** (K_factor / 10)

        for c in range(0, len(self.m_numOfCluster)):
            if c == 0:
                clusterPowerForAngles.append(clusterPower[c] / (1 + K_linear) + K_linear / (1 + K_linear))
            else:
                clusterPowerForAngles.append(clusterPower[c] / (1 + K_linear))
            if powerMax < clusterPowerForAngles[c]:
                powerMax = clusterPowerForAngles[c]
        thresh = 0.0032
        for c in range(0, len(self.m_numOfCluster)):
            if clusterPowerForAngles[c - 1] < thresh * powerMax:
                clusterPowerForAngles.pop(c - 1)
                clusterPower.pop(c - 1)
                clusterDelay.pop(c - 1)
        m_numCluster = len(clusterPower)
        C_tau = 0.7705 - 0.0433 * K_factor + 2e-4 * K_factor ** 2 + 17e-6 * K_factor ** 3
        for c in range(0, m_numCluster):
            clusterDelay[c] = clusterDelay[c] / C_tau

    def calc_pathloss(self):
        los_probability = self.calc_los_probability()
        # self.pathloss =  self.calc_pathloss_los()
        self.pathloss = los_probability * self.calc_pathloss_los() + (1 - los_probability) * self.calc_pathloss_nlos()
        return self.pathloss

    def calc_noise_power(self):
        # thermal noise + noise figure of receiver (system aspects lecture 2)
        noise = -174 + 10 * np.log10(self.PRB_bandwidth) + self.noise_figure
        return noise

    def calc_SNR(self):
        """
        https://www.etsi.org/deliver/etsi_ts/138100_138199/138104/15.03.00_60/ts_138104v150300p.pdf"""
        transmit_power = - 29 * np.log10(self.num_RB)
        self.SNR = transmit_power - self.calc_pathloss() - self.calc_noise_power()
        # print("SNR matrix dimensions" + str(self.SNR.shape))
        return self.SNR
        # SNR = power - pathloss_shadowing + fast_fading -system_noise

    def test_channel_model(self):
        p = self.calc_los_probability()
        for gNB in range(self.num_BSs):
            plt.plot(self.distance_2D[gNB, :, :], p[gNB, :, :])
            plt.show()

    def calc_delay_spread(self):
        """
        Four candidate models: distance-dependent model, antenna-dependent model, frequency-dependent model,
        volume-dependent model. From 3GPP results, the RMS delay spread is supposed to be volume dependent and
        it does not correlate with frequency, distance, antenna height and subscenario.
        """
        mu_delay_spread_los = np.log10(26 * (self.V / self.S) + 14) - 9.35
        sigma_delay_spread_los = 0.15
        mu_delay_spread_nlos = np.log10(30 * (self.V / self.S) + 32) - 9.44
        sigma_delay_spread_nlos = 0.19
        lgDS_los = mu_delay_spread_los + 2.33 * sigma_delay_spread_los
        lgDS_nlos = mu_delay_spread_nlos + 2.33 * sigma_delay_spread_nlos
        return lgDS_los, lgDS_nlos

    def calc_angular_spread(self):
        ASD_los = 1.56
        ASD_nlos = 1.57
        center_freq_los = []
        y = []
        for self.center_freq in range(0, 100):
            ASA_los = -0.18 * np.log10(1 + self.center_freq) + 1.78
            y.append(ASA_los)
            center_freq_los.append(self.center_freq)
        plt.plot(center_freq_los, y)
        plt.show()
        ASA_nlos = 1.72
        ZSA_los = -0.2 * np.log10(1 + self.center_freq) + 1.5
        ZSA_nlos = -0.13 * np.log10(1 + self.center_freq) + 1.45
        ZSD_los = 1.35
        ZSD_nlos = 1.2
        pass

    def plot(self):
        # c = np.reshape(np.where(self.los_probability > 0.5, 'r', 'b'), -1)
        # print(c)
        gNB_coordinates_tuple = tuple(self.scenario.gNB_coordinates)
        fig = plt.figure(linewidth=10)
        ax = fig.gca()
        for axis in ['top', 'bottom', 'left', 'right']:
            ax.spines[axis].set_linewidth(3)
        plt.scatter(*zip(*gNB_coordinates_tuple))
        plt.scatter(self.user_coordinates[:, 0], self.user_coordinates[:, 1])
        plt.xlim((0, self.scenario.hall_length))
        plt.ylim((0, self.scenario.hall_width))
        plt.show()

        fig = plt.figure(figsize=(16, 9))
        ax = plt.axes(projection="3d")
        ax.set_xlim((0, self.scenario.hall_length))
        ax.set_ylim((0, self.scenario.hall_width))
        ax.set_zlim((0, 10))
        # Creating color map
        my_cmap = plt.get_cmap('hsv')
        a = [*zip(*gNB_coordinates_tuple)]
        sctt = ax.scatter3D(*zip(*gNB_coordinates_tuple), alpha=1, c=a[2], cmap=my_cmap)
        ax.set_xlabel('Factory hall length')
        ax.set_ylabel('Factory hall width')
        ax.set_zlabel('Factory hall hight')
        fig.colorbar(sctt, ax=ax, shrink=0.5, aspect=4)
        azim = 135
        elev = 25
        ax.view_init(elev, azim)
        plt.show()
