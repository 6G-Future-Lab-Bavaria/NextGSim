from abc import ABC, abstractmethod
import numpy as np
from copy import deepcopy
from runtime.data_classes import Constants, MeasurementParams
'SINR [number of users, number of gNBs]'

# todo: distance between BS anf UE should be split into outside and inside
# https://www.etsi.org/deliver/etsi_tr/138900_138999/138901/14.03.00_60/tr_138901v140300p.pdf
# Channel models for 0.5-100 GHz


class ChannelModel(ABC):
    def __init__(self, simulation, sim_params):
        self.simulation = simulation
        self.num_PRBs = None
        self.ue_antenna_height = sim_params.scenario.ue_antenna_height
        self.gnb_antenna_height = None
        self.PRB_bandwidth = None
        self.center_freq = None
        self.center_freq_multiplier = sim_params.scenario.center_freq_multiplier
        self.communication_type = sim_params.communication_type
        self.k_factor = 3  # lin  # check the value
        self.noise_figure = None
        self.shadowing_std_los = sim_params.scenario.shadowing_std_los
        self.shadowing_std_nlos = sim_params.scenario.shadowing_std_nlos
        self.transmit_power = None
        self.set_noise_figure(sim_params.scenario)
        self.measured_SINR = None  # for TP calc and RLF monitoring
        self.measured_RSRP = None
        self.average_SINR = None   # for NHO and CHO
        self.average_RSRP = None
        self.sinr_list = []
        self.rsrp_list = []
        self.gnb_xy = None
        self.user_xy = None
        self.distance_users_gnbs_3d = None
        self.los_flag = None
        self.beta_l3_av = MeasurementParams.channel_measurement_periodicity/ MeasurementParams.snr_averaging_time

    def set_tx_power_per_PRB(self):
        # Paper: Deep Reinforcement Learning for 5G Networks: Joint Beamforming, Power Control, and Interference Coordination
        # Total transmit power is simply divided equally among all the PRBs and is therefore constant.
        # Pmax - 10logNprb + 10logNprballocated to the UE
        # RSRP should not depend on number of allocated PRBs here since it is measured on a pilot/sync signal.
        # Number of allocated PRBs is considered in the scheduler
        self.transmit_power -= 10*np.log10(self.num_PRBs)

    def set_noise_figure(self, scenario):
        if self.communication_type == 'UL':
            self.noise_figure = scenario.UE_noise_figure
        elif self.communication_type == 'DL':
            self.noise_figure = scenario.BS_noise_figure

    def create_gnb_postion_matrix(self):
        self.gnb_xy = np.zeros((len(self.simulation.gNBs_per_scenario), 2))
        for gNB in self.simulation.gNBs_per_scenario:
            self.gnb_xy[gNB.ID, 0] = gNB.x
            self.gnb_xy[gNB.ID, 1] = gNB.y

    def create_user_position_matrix(self, next_pos):
        self.user_xy = np.zeros((len(self.simulation.devices_per_scenario), 2))
        for user in self.simulation.devices_per_scenario:
            if next_pos:
                self.user_xy[user.ID, 0] = user.x_next
                self.user_xy[user.ID, 1] = user.y_next
            else:
                self.user_xy[user.ID, 0] = user.x
                self.user_xy[user.ID, 1] = user.y

    def calc_distance_btw_users_gnbs(self, next_pos=False):
        """2D_users_gNBs_distance [number of users, number of gNBs]"""
        """3D_users_gNBs_distance [number of users, number of gNBs]"""
        self.create_user_position_matrix(next_pos)
        # if not self.gnb_xy:
        self.create_gnb_postion_matrix()  # gNBs are static, call only once
        distance_users_gnbs_2d = np.zeros(
            (len(self.simulation.devices_per_scenario), len(self.simulation.gNBs_per_scenario)), float)
        distance_users_gnbs_3d = np.zeros(
            (len(self.simulation.devices_per_scenario), len(self.simulation.gNBs_per_scenario)), float)
        for gNB in self.simulation.gNBs_per_scenario:
            distance_users_gnbs_2d[:, gNB.ID] = np.sqrt((self.user_xy[:, 0] - self.gnb_xy[gNB.ID, 0]) ** 2 +
                                                        (self.user_xy[:, 1] - self.gnb_xy[gNB.ID, 1]) ** 2)
            distance_users_gnbs_3d[:, gNB.ID] = np.sqrt(distance_users_gnbs_2d[:, gNB.ID] ** 2 +
                                                        (self.gnb_antenna_height[
                                                             0, gNB.ID] - self.ue_antenna_height) ** 2)
        if not next_pos:
            self.distance_users_gnbs_3d = deepcopy(distance_users_gnbs_3d)
        return deepcopy(distance_users_gnbs_2d), deepcopy(distance_users_gnbs_3d)

    # TODO:The same for all devices?
    def outdoor_to_indoor_penetration_loss(self, distance_indoor):
        """penetration_loss [number of users, number of gNBs]"""
        # check: should only be considered for indoor users (in UMi 80% of users are indoors)
        assert self.center_freq <= 6, "This O2I penetration loss model is for freq up to 6 GHz"
        # O2I_penetration_loss = np.zeros((len(self.ran_simulation.devices_per_scenario),
        #                                  len(self.ran_simulation.gNBs_per_scenario)), float)
        bld_though_wall = 20  # dB
        inside_loss = 0.5 * distance_indoor
        O2I_penetration_loss = bld_though_wall + inside_loss
        return O2I_penetration_loss

    @abstractmethod
    def calc_pathloss(self, distance_btw_ue_and_gnb_3d, los_flag):
        pass

    @abstractmethod
    def calc_pathloss_with_los(self, distance_btw_ue_and_gnb_3d):
        pass

    @abstractmethod
    def calc_pathloss_with_nlos(self, distance_btw_ue_and_gnb_3d, pathloss_los):
        pass

    @abstractmethod
    def calc_los_probability(self, distance_btw_ue_and_gnb_2d):
        pass

    def calc_rician_fading(self):
        # wiki: Rician fading is a stochastic model for radio propagation anomaly caused by
        # partial cancellation of a radio signal by itself — the signal arrives at the receiver by several
        # different paths (hence exhibiting multipath interference), and at least one of the paths is changing (
        # lengthening or shortening). Rician fading occurs when one of the paths, typically a line of sight signal or
        # some strong reflection signals, is much stronger than the others.
        if self.simulation.seed:
            np.random.seed(self.simulation.seed)
        """Rician fading[number of users, number of RBs, number of gNBs]"""
        k = 10 ** (self.k_factor / 10)
        sigma = np.sqrt(1 / (2 * (k + 1)))
        mu = np.sqrt(k / (k + 1))

        theta = 0  # any real value where mu=mu1+mu2
        mu1 = mu * np.sin(theta)
        mu2 = mu * np.cos(theta)

        x = sigma * np.random.normal(size=(len(self.simulation.devices_per_scenario),
                                           len(self.simulation.gNBs_per_scenario))) + mu1
        y = sigma * np.random.normal(size=(len(self.simulation.devices_per_scenario),
                                           len(self.simulation.gNBs_per_scenario))) + mu2

        rician_fading = 20 * np.log10(np.sqrt(x ** 2 + y ** 2))  # Rician random numbers
        # self.log_channel(f"Rician fading is {rician_fading}")
        return rician_fading

    def calc_shadowing(self, los_flag):
        # Log-normal distribution according to 3GPP TR 38.901, page 26, however, papers use normal
        # slow fading
        if self.simulation.seed:
            np.random.seed(self.simulation.seed)

        standart_normal_dis_samples = np.random.normal(size=len(self.simulation.gNBs_per_scenario))
        shadowing_los = self.shadowing_std_los * standart_normal_dis_samples
        shadowing_nlos = self.shadowing_std_nlos * standart_normal_dis_samples
        shadowing = los_flag * shadowing_los + ~los_flag * shadowing_nlos

        # log_normal_dis_samples = np.random.lognormal(size=len(self.ran_simulation.gNBs_per_scenario))
        # shadowing_los = self.shadowing_std_los * log_normal_dis_samples
        # shadowing_nlos = self.shadowing_std_nlos * log_normal_dis_samples
        # shadowing = los_flag * shadowing_los + ~los_flag * shadowing_nlos
        return shadowing

    def calc_noise_power(self, PRB_bandwidth):
        # thermal noise + noise figure of receiver (system aspects lecture 2)
        noise = -174 + 10 * np.log10(PRB_bandwidth) + self.noise_figure
        # self.log_channel(f"Noise is {noise}")
        return noise

    def calc_antenna_gain_device(self):
        # self.log_channel(f"Antenna gain is {self.ran_simulation.sim_params.scenario.UE_antenna_gain}")
        return self.simulation.sim_params.scenario.UE_antenna_gain

    def calc_antenna_gain_gNB(self):
        # self.log_channel(f"Antenna gain is {self.ran_simulation.sim_params.scenario.UE_antenna_gain}")
        return self.simulation.sim_params.scenario.UE_antenna_gain

    def calc_total_channel_loss(self, distance_btw_ue_and_gnb_2d, distance_btw_ue_and_gnb_3d, next_pos):
        if self.simulation.seed:
            np.random.seed(self.simulation.seed)

        if self.simulation.TTI == 0 or self.simulation.sim_params.los_update_periodicity and \
                self.simulation.TTI % self.simulation.sim_params.los_update_periodicity == 0:
            los_probability = self.calc_los_probability(distance_btw_ue_and_gnb_2d)
            random_matrix = np.random.rand(*los_probability.shape)
            self.los_flag = los_probability > random_matrix

        if self.simulation.sim_params.always_los_flag or next_pos:
            self.los_flag = np.ones_like(self.los_flag)
        elif self.simulation.sim_params.always_non_los_flag:
            self.los_flag = np.zeros_like(self.los_flag)

        loss = self.calc_pathloss(distance_btw_ue_and_gnb_3d, self.los_flag)
        loss += 2  # dB # cable loss
        loss += 3  # dB  # Body loss
        loss += 8.5  # dB  # Foliage loss
        loss += self.calc_shadowing(self.los_flag)
        # fixme: generate distance_indoor different for users indoor
        if self.simulation.sim_params.scenario.scenario == 'Indoor':
            loss += self.outdoor_to_indoor_penetration_loss(distance_indoor=1)
        # rician_fading = self.calc_rician_fading()
        # loss -= rician_fading  not in the 3GPP, if used then L1 filtering is required
        return loss

    def init(self):
        self.gnb_xy = None
        self.user_xy = None

    # @profile(stream=fp)
    def calculate_final_SINR_RSRP(self):
        """
        This function is used in the Simulation() to calculate SINR/RSRP at current TTI.
        """
        measured_SINR, measured_RSRP = self.calculate_measured_SINR_RSRP()
        self.set_SINR_RSRP(measured_SINR, measured_RSRP)

    def add_max_micro_interference(self, measured_RSRP):
        """
        Only for micro cells. Assume only interference from the micro cell with largest RSRP.
        Assume that there is always DL transmission (no interference coordination).
        :param measured_RSRP:
        :return: measured_RSRP + interference_micro
        """
        num_macro_gnbs = self.simulation.sim_params.scenario.num_macro_gnbs
        assert measured_RSRP.any() > 0, "RSRP must be negative. Otherwise the following code with abs() does not work"
        interference = np.max(measured_RSRP[:, num_macro_gnbs:], axis=1)
        interference = interference.reshape(len(interference), 1)
        measured_RSRP[:, num_macro_gnbs:] = measured_RSRP[:, num_macro_gnbs:] + interference  # add only to micro cells
        return measured_RSRP

    def add_micro_interference_within_a_cell(self, measured_RSRP):
        self.micro_neigh = {4:[5, 6], 5:[4, 6], 6:[4, 5], 7:[], 8:[9, 10], 9:[8, 10], 10:[8, 9], 11:[12, 13], 12:[11, 13],
                            13:[11, 12], 14:[15, 16], 15:[14, 16], 16:[14, 15], 17:[18, 19], 18:[17, 19], 19:[17, 18],
                            20:[], 21:[22, 23], 22:[21, 23], 23:[21, 22], 24:[]} # cell id: list of neighboring cell ids
        # to add this interference, we need a for loop, which will slow down the simulaiton
        raise NotImplemented

    def calculate_measured_SINR_RSRP(self, next_pos=False):
        """
      This function calculates the actual SINR and RSRP for every device (connected, idle, etc) at every TTI.
        This function is used to calculate SINR/RSRP at next current TTI if next_pos is True.
      :param next_pos: Flag is set to true when called from ECHO to calculate future SINR, otherwise False.
      :return: Return only if next_pos is True, otherwise set self variables.
              """
        self.init()
        # print(f"Tx power: {self.transmit_power}")
        # print(f"Num PRBs: {self.num_PRBs}")
        self.set_tx_power_per_PRB()
        # print(f"Tx power per PRB: {self.transmit_power}")
        distance_btw_ue_and_gnb_2d, distance_btw_ue_and_gnb_3d = self.calc_distance_btw_users_gnbs(next_pos)
        loss = self.calc_total_channel_loss(distance_btw_ue_and_gnb_2d, distance_btw_ue_and_gnb_3d, next_pos)
        noise = self.calc_noise_power(self.PRB_bandwidth)
        measured_RSRP = self.transmit_power - 10 * np.log10(self.num_PRBs) + self.calc_antenna_gain_device() + \
                        self.calc_antenna_gain_gNB() - loss
        # print("Before")
        # print(measured_RSRP)
        if self.simulation.sim_params.with_interference:
            measured_RSRP = self.add_max_micro_interference(measured_RSRP)
        # print("After")
        measured_SINR = measured_RSRP - noise
        return measured_SINR, measured_RSRP   # check if deep copy is required

    def set_SINR_RSRP(self, measured_SINR, measured_RSRP):
        self.measured_SINR = measured_SINR
        self.measured_RSRP = measured_RSRP

        if self.simulation.sim_params.snr_averaging:
            self.average_SINR = self.average_signal(measured_SINR, self.sinr_list)
            self.average_RSRP = self.average_signal(measured_RSRP, self.rsrp_list)
            # self.average_SINR = self.apply_l3_filtering(self.average_SINR, measured_SINR)
            # self.average_RSRP = self.apply_l3_filtering(self.average_RSRP, measured_RSRP)
        else:
            self.average_SINR = measured_SINR
            self.average_RSRP = measured_RSRP

    def average_signal(self, current, lst):
        AVG_N = int(MeasurementParams.snr_averaging_time / MeasurementParams.channel_measurement_periodicity)
        lst.append(current)
        if len(lst) > AVG_N:
            lst.pop(0)

        if len(lst) == 1:
            return current
        elif len(lst) <= AVG_N:
            return np.mean(lst, axis=0)
        else:
            raise ValueError(f"len(self.sinr_list) should be smaller or equal to {AVG_N}, but it is {len(self.sinr_list)}")

    def apply_l3_filtering(self, average, current):
        if average is None:
            return current
        else:
            return self.beta_l3_av * current + (1-self.beta_l3_av)*average


class ChannelIndoor(ChannelModel):
    def __init__(self, simulation, simparams):
        super().__init__(simulation, simparams)
        self.center_freq = simparams.scenario.center_freq
        self.PRB_bandwidth = self.simulation.sim_params.scenario.PRB_bandwidth * 10 ** 3  # Hz
        self.transmit_power = simparams.scenario.transmit_power
        self.num_PRBs = simulation.sim_params.scenario.num_PRBs

    def init(self):
        super().init()
        self.gnb_antenna_height = np.zeros((1, len(self.simulation.gNBs_per_scenario)), float)
        self.gnb_antenna_height[0, :] = self.simulation.sim_params.scenario.gnb_antenna_height
        self.gnb_xy = None
        self.user_xy = None

    def calc_los_probability(self, d_2dout):
        assert (self.gnb_antenna_height == 3).all(), self.gnb_antenna_height
        los_probability = np.exp((-d_2dout - 49) / 211.7) * 0.54
        mask1 = d_2dout <= 5
        mask2 = (5 < d_2dout) & (d_2dout <= 49)
        los_probability[mask1] = 1
        los_probability[mask2] = np.exp((-d_2dout[mask2] - 5) / 70.8)
        return los_probability

    def calc_pathloss(self, distance_btw_ue_and_gnb_3d, los_flag):
        """ pathloss [number of users, number of RBs, number of gNBs]"""
        # assume that input distance = to outside distance (fixme later)
        pathloss_los = self.calc_pathloss_with_los(distance_btw_ue_and_gnb_3d)
        pathloss_nlos = self.calc_pathloss_with_nlos(distance_btw_ue_and_gnb_3d, pathloss_los)
        final_pathloss = los_flag * pathloss_los + ~los_flag * pathloss_nlos
        return final_pathloss

    def calc_pathloss_with_los(self, distance_btw_ue_and_gnb_3d):
        # fixme: also check 1 <= distance_btw_ue_and_gnb
        assert np.all(distance_btw_ue_and_gnb_3d <= 150), \
            f"3D Distance must be in the range [1, 150] m, not {distance_btw_ue_and_gnb_3d}"  # m
        # distance_3d = self.calc_distance_users_gnbs_3d()
        return 32.4 + 17.3 * np.log10(distance_btw_ue_and_gnb_3d) + 20 * np.log10(self.center_freq)

    def calc_pathloss_with_nlos(self, distance_btw_ue_and_gnb_3d, pathloss_los):
        # distance_3d = self.calc_distance_users_gnbs_3d(distance_btw_ue_and_gnb)
        # PL_los = self.calc_pathloss_with_los(distance_btw_ue_and_gnb_3d)
        # todo: check that self.center_freq = 0.5 is okay
        return np.maximum(38.3 * np.log10(distance_btw_ue_and_gnb_3d) + 17.30 + 24.9 * np.log10(self.center_freq),
                          pathloss_los)


class ChannelUMiUMa(ChannelModel):
    # parameter values for UMi and UMa: https://www.ericsson.com/en/blog/2019/9/energy-consumption-5g-nr
    def __init__(self, simulation, simparams):
        super().__init__(simulation, simparams)
        self.effective_env_height = simparams.scenario.effective_env_height
        self.gnb_type_macro_or_not = None
        self.gnb_antenna_height = None

    def init(self):
        super().init()
        num_macro_gnbs = self.simulation.sim_params.scenario.num_macro_gnbs

        self.gnb_type_macro_or_not = np.zeros((1, len(self.simulation.gNBs_per_scenario)), float)
        self.gnb_type_macro_or_not[0, :num_macro_gnbs] = 1

        self.gnb_antenna_height = np.zeros((1, len(self.simulation.gNBs_per_scenario)), float)
        self.gnb_antenna_height[0, :num_macro_gnbs] = self.simulation.sim_params.scenario.macro_gnb_antenna_height
        self.gnb_antenna_height[0, num_macro_gnbs:] = self.simulation.sim_params.scenario.micro_gnb_antenna_height
        self.center_freq = np.zeros((len(self.simulation.devices_per_scenario), len(self.simulation.gNBs_per_scenario)),
                                    float)
        self.center_freq[:, :num_macro_gnbs] = self.simulation.sim_params.scenario.center_freq_macro
        self.center_freq[:, num_macro_gnbs:] = self.simulation.sim_params.scenario.center_freq_micro

        self.transmit_power = np.zeros((1, len(self.simulation.gNBs_per_scenario)), float)
        self.transmit_power[0, :num_macro_gnbs] = self.simulation.sim_params.scenario.transmit_power_macro
        self.transmit_power[0, num_macro_gnbs:] = self.simulation.sim_params.scenario.transmit_power_micro

        self.num_PRBs = np.zeros((1, len(self.simulation.gNBs_per_scenario)), float)
        self.num_PRBs[0, :num_macro_gnbs] = self.simulation.sim_params.scenario.num_PRBs_macro
        self.num_PRBs[0, num_macro_gnbs:] = self.simulation.sim_params.scenario.num_PRBs_micro

        self.gnb_xy = None
        self.user_xy = None

    def get_break_point_distance(self):
        break_point_dist = 4 * (self.gnb_antenna_height - self.effective_env_height) * \
                           (self.ue_antenna_height - self.effective_env_height) * self.center_freq \
                           * self.center_freq_multiplier / Constants.speed_of_light
        # self.log_channel(f"Breakpoint distance is {break_point_dist}")
        return break_point_dist

    def calc_pathloss(self, distance_btw_ue_and_gnb_3d, los_flag):
        """ pathloss [number of users, number of RBs, number of gNBs]"""
        # assume that input distance = to outside distance (fixme later)
        pathloss_los, pathloss_los_umi, pathloss_los_uma = self.calc_pathloss_with_los(distance_btw_ue_and_gnb_3d)
        pathloss_nlos = self.calc_pathloss_with_nlos(distance_btw_ue_and_gnb_3d, [pathloss_los_umi, pathloss_los_uma])
        final_pathloss = los_flag * pathloss_los + ~los_flag * pathloss_nlos
        return final_pathloss

    def calc_pathloss_with_los(self, distance_btw_ue_and_gnb_3d):
        assert 1.5 <= self.ue_antenna_height <= 22.5, f" UE's antenna height must be in [1.5;22.5], but is set to {self.ue_antenna_height}"
        break_point_dist = self.get_break_point_distance()
        if np.all(10 <= distance_btw_ue_and_gnb_3d) and np.all(distance_btw_ue_and_gnb_3d <= break_point_dist):
            pl_umi = 32.4 + 21 * np.log10(distance_btw_ue_and_gnb_3d) + 20 * np.log10(self.center_freq)
            pl_uma = 28 + 22 * np.log10(distance_btw_ue_and_gnb_3d) + 20 * np.log10(self.center_freq)

        # elif np.all(break_point_dist <= distance_btw_ue_and_gnb_3d) and np.all(distance_btw_ue_and_gnb_3d <= 5000):
        else:
            pl_umi = 32.4 + 40 * np.log10(distance_btw_ue_and_gnb_3d) + 20 * np.log10(self.center_freq) - \
                   9.5 * np.log10(break_point_dist ** 2 + (self.gnb_antenna_height - self.ue_antenna_height) ** 2)
            pl_uma = 28 + 40 * np.log10(distance_btw_ue_and_gnb_3d) + 20 * np.log10(self.center_freq) - \
                   9 * np.log10(break_point_dist ** 2 + (self.gnb_antenna_height - self.ue_antenna_height) ** 2)
        # else:
        #     raise ValueError(f"Distance {distance_btw_ue_and_gnb_3d} is out of 3GPP range")
        pl_final = (pl_uma - pl_umi) * self.gnb_type_macro_or_not
        pl_final += pl_umi
        # self.check_pathloss_calc_for_umi_uma(pl_umi, pl_uma, pl_final)
        return pl_final, pl_umi, pl_uma

    def calc_pathloss_with_nlos(self, distance_btw_ue_and_gnb_3d, pathloss):
        pathloss_with_los_umi, pathloss_with_los_uma = pathloss
        assert 1.5 <= self.ue_antenna_height <= 22.5, f" UE's antenna height must be in [1.5;22.5], but is set to {self.ue_antenna_height}"
        # if (9 <= distance_btw_ue_and_gnb_3d).all() and (distance_btw_ue_and_gnb_3d<= 5000).all():
        pathloss_with_nlos_umi = 35.3 * np.log10(distance_btw_ue_and_gnb_3d) + 22.4 + 21.3 * np.log10(self.center_freq) - \
                             0.3 * (self.ue_antenna_height - 1.5)
        pathloss_umi = np.maximum(pathloss_with_los_umi, pathloss_with_nlos_umi)

        pathloss_with_nlos_uma = 13.54 + 39.08 * np.log10(distance_btw_ue_and_gnb_3d) + \
                                 20 * np.log10(self.center_freq) - 0.6 * (self.ue_antenna_height - 1.5)
        pathloss_uma = np.maximum(pathloss_with_los_uma, pathloss_with_nlos_uma)
        pathloss_final = (pathloss_uma - pathloss_umi) * self.gnb_type_macro_or_not
        pathloss_final += pathloss_umi
        # self.check_pathloss_calc_for_umi_uma(pathloss_umi, pathloss_uma, pathloss_final)
        return pathloss_final

        # else:
        #     raise ValueError(f"Distance is out of 3GPP range: min and max in my case: {np.min(distance_btw_ue_and_gnb_3d)}, "
        #                      f" {np.max(distance_btw_ue_and_gnb_3d)}")  # fixme

    def check_pathloss_calc_for_umi_uma(self, pathloss_umi, pathloss_uma, pathloss_final):
        num_macro_gnbs = self.simulation.sim_params.scenario.num_macro_gnbs
        assert (pathloss_final[0, :num_macro_gnbs] == pathloss_uma[0, :num_macro_gnbs]).all()
        assert (pathloss_final[0, num_macro_gnbs:] == pathloss_umi[0, num_macro_gnbs:]).all()

    def calc_los_probability(self, d_2dout):
        assert self.ue_antenna_height <= 13, "For larger heights see p.28 TP 38.901 Study on channel model"
        los_probability_umi = 18 / d_2dout + np.exp(-d_2dout / 36) * (1 - 18 / d_2dout)
        los_probability_uma = 18 / d_2dout + np.exp(-d_2dout / 63) * (1 - 18 / d_2dout)
        los_probability = (los_probability_uma - los_probability_umi) * self.gnb_type_macro_or_not
        los_probability += los_probability_umi
        # self.check_los_prob_calc_for_umi_uma(los_probability_umi, los_probability_uma, los_probability)
        mask = d_2dout <= 18
        los_probability[mask] = 1
        return los_probability

    def check_los_prob_calc_for_umi_uma(self, los_probability_umi, los_probability_uma, los_probability):
        # los_probability_umi = np.round(los_probability_umi, 1)
        # los_probability_uma = np.round(los_probability_uma, 1)
        # los_probability = np.round(los_probability, 1)
        num_macro_gnbs = self.simulation.sim_params.scenario.num_macro_gnbs
        assert (los_probability_uma[0, :num_macro_gnbs] == los_probability[0, :num_macro_gnbs]).all(), \
            f"tti={self.simulation.TTI}, {num_macro_gnbs}, UMi: {los_probability_umi}, UMa: {los_probability_uma}, Final: {los_probability}"
        assert (los_probability_umi[0, num_macro_gnbs:] == los_probability[0, num_macro_gnbs:]).all(), \
            f"tti={self.simulation.TTI}, {num_macro_gnbs}, UMi: {los_probability_umi}, UMa: {los_probability_uma}, Final: {los_probability}"

    def calc_noise_power(self, PRB_bandwidth):
        num_macro_gnbs = self.simulation.sim_params.scenario.num_macro_gnbs
        noise_macro = super().calc_noise_power(self.simulation.sim_params.scenario.PRB_bandwidth_macro * 10 ** 3)
        noise_micro = super().calc_noise_power(self.simulation.sim_params.scenario.PRB_bandwidth_micro * 10 ** 3)
        noise = np.zeros((len(self.simulation.devices_per_scenario), len(self.simulation.gNBs_per_scenario)),
                         float)
        noise[:, :num_macro_gnbs] = noise_macro
        noise[:, num_macro_gnbs:] = noise_micro
        return noise


class ChannelUMa(ChannelModel):
    """This Channel is not used in the ran_simulation, to speed up the ran_simulation using np arrays.
    It is only used for plotting PLs.  """
    def __init__(self, simulation, simparams):
        super().__init__(simulation, simparams)
        self.effective_env_height = simparams.scenario.effective_env_height

    def get_break_point_distance(self):
        # fixme: call this function from ChannelUMi
        break_point_dist = 4 * (self.gnb_antenna_height - self.effective_env_height) * \
                           (self.ue_antenna_height - self.effective_env_height) * self.center_freq \
                           * self.center_freq_multiplier / Constants.speed_of_light
        # self.log_channel(f"Breakpoint distance is {break_point_dist}")
        return break_point_dist

    def calc_pathloss(self, distance_btw_ue_and_gnb_3d, los_flag):
        """ pathloss [number of users, number of RBs, number of gNBs]"""
        # assume that input distance = to outside distance (fixme later)
        pathloss_los = self.calc_pathloss_with_los(distance_btw_ue_and_gnb_3d)
        pathloss_nlos = self.calc_pathloss_with_nlos(distance_btw_ue_and_gnb_3d, pathloss_los)
        final_pathloss = los_flag * pathloss_los + ~los_flag * pathloss_nlos
        return final_pathloss

    def calc_pathloss_with_los(self, distance_btw_ue_and_gnb_3d):
        assert 1.5 <= self.ue_antenna_height <= 22.5, f" UE's antenna height must be in [1.5;22.5], but is set to {self.ue_antenna_height}"
        break_point_dist = self.get_break_point_distance()
        if np.all(10 <= distance_btw_ue_and_gnb_3d) and np.all(distance_btw_ue_and_gnb_3d <= break_point_dist):
            return 28.0 + 22 * np.log10(distance_btw_ue_and_gnb_3d) + 20 * np.log10(self.center_freq)
        elif np.all(break_point_dist <= distance_btw_ue_and_gnb_3d) and np.all(distance_btw_ue_and_gnb_3d <= 5000):
            return 28.0 + 40 * np.log10(distance_btw_ue_and_gnb_3d) + 20 * np.log10(self.center_freq) - \
                   9 * np.log10(break_point_dist ** 2 + (self.gnb_antenna_height - self.ue_antenna_height) ** 2)
        else:
            return 28.0 + 40 * np.log10(distance_btw_ue_and_gnb_3d) + 20 * np.log10(self.center_freq) - \
                   9 * np.log10(break_point_dist ** 2 + (self.gnb_antenna_height - self.ue_antenna_height) ** 2)
            # raise ValueError(f"Distance {distance_btw_ue_and_gnb} is out of 3GPP range")

    def calc_pathloss_with_nlos(self, distance_btw_ue_and_gnb_3d, pathloss_with_los):
        assert 1.5 <= self.ue_antenna_height <= 22.5, f" UE's antenna height must be in [1.5;22.5], but is set to {self.ue_antenna_height}"
        # if (9 <= distance_btw_ue_and_gnb_3d).all() and (distance_btw_ue_and_gnb_3d<= 5000).all():
        pathloss_with_nlos = 13.54 + 39.08 * np.log10(distance_btw_ue_and_gnb_3d) + 20 * np.log10(
            self.center_freq) - 0.6 * (self.ue_antenna_height - 1.5)
        return np.maximum(pathloss_with_los, pathloss_with_nlos)
        # else: # fixme
            # raise ValueError(f"Distance is out of 3GPP range: min and max in my case: "
        #                      f"{np.min(distance_btw_ue_and_gnb_3d)}, {np.max(distance_btw_ue_and_gnb_3d)}")

    def calc_los_probability(self, d_2dout):
        assert self.ue_antenna_height <= 13, "For larger heights see p.28 TP 38.901 Study on channel model"
        los_probability = 18 / d_2dout + np.exp(-d_2dout / 63) * (1 - 18 / d_2dout)
        mask = d_2dout <= 18
        los_probability[mask] = 1
        return los_probability

    def calc_noise_power(self, PRB_bandwidth):
        num_macro_gnbs = self.simulation.sim_params.scenario.num_macro_gnbs
        noise_macro = super().calc_noise_power(self.simulation.sim_params.scenario.PRB_bandwidth_macro * 10 ** 3)
        noise_micro = super().calc_noise_power(self.simulation.sim_params.scenario.PRB_bandwidth_micro * 10 ** 3)
        noise = np.zeros((len(self.simulation.devices_per_scenario), len(self.simulation.gNBs_per_scenario)),
                         float)
        noise[:, :num_macro_gnbs] = noise_macro
        noise[:, num_macro_gnbs:] = noise_micro
        return noise

    def init(self):
        super().init()
        num_macro_gnbs = self.simulation.sim_params.scenario.num_macro_gnbs

        self.gnb_type_macro_or_not = np.zeros((1, len(self.simulation.gNBs_per_scenario)), float)
        self.gnb_type_macro_or_not[0, :num_macro_gnbs] = 1

        self.gnb_antenna_height = np.zeros((1, len(self.simulation.gNBs_per_scenario)), float)
        self.gnb_antenna_height[0, :num_macro_gnbs] = self.simulation.sim_params.scenario.macro_gnb_antenna_height
        self.gnb_antenna_height[0, num_macro_gnbs:] = self.simulation.sim_params.scenario.micro_gnb_antenna_height
        self.center_freq = np.zeros((len(self.simulation.devices_per_scenario), len(self.simulation.gNBs_per_scenario)),
                                    float)
        self.center_freq[:, :num_macro_gnbs] = self.simulation.sim_params.scenario.center_freq_macro
        self.center_freq[:, num_macro_gnbs:] = self.simulation.sim_params.scenario.center_freq_micro

        self.transmit_power = np.zeros((1, len(self.simulation.gNBs_per_scenario)), float)
        self.transmit_power[0, :num_macro_gnbs] = self.simulation.sim_params.scenario.transmit_power_macro
        self.transmit_power[0, num_macro_gnbs:] = self.simulation.sim_params.scenario.transmit_power_micro

        self.num_PRBs = np.zeros((1, len(self.simulation.gNBs_per_scenario)), float)
        self.num_PRBs[0, :num_macro_gnbs] = self.simulation.sim_params.scenario.num_PRBs_macro
        self.num_PRBs[0, num_macro_gnbs:] = self.simulation.sim_params.scenario.num_PRBs_micro


