import matplotlib.pyplot as plt
from abc import ABC

"""
    1. 3GPP: Channel model release 14
    2. Study of Realistic Antenna Patterns in 5G mmWave Cellular Scenarios.
    3. ITU-R Report ITU-R M.2412 “Guidelines for Evaluation of Radio Interface Technologies for IMT-2020,” ITU-R WP 5D,
     Oct. 2017.
    Antenna pattern is needed to quantify antenna gain obtained due to the radiation pattern. A precise antenna pattern
    can be obtained combining together the array factor expression, which provides information on the directivity
    equation of an antenna array, with the single element radiation pattern
    """


class AntennaPatterns(ABC):

    def __init__(self):
        self.elevation_antenna_orientation = None  # degree
        self.elevation_beamwidth = None  # degree
        self.azimuth_beamwidth = None  # degree
        self.backward_attenuation = None  # dB
        self.maximum_antenna_element_gain = None  # dBi

    def antenna_element_horizonal_radiation_pattern(self, BS_user_azimuth_angle):
        """
       :return: A_E_H (dB)
       """
        A_E_H = -min(12 * (BS_user_azimuth_angle / self.azimuth_beamwidth) ** 2, self.backward_attenuation)
        return A_E_H

    def plot_antenna_element_horizonal_radiation_pattern(self):
        """
        Comparioson with results in: 3GPP TR 37.840 v12.1.0, “Technical Specification Group Radio Access Network; Study
        of Radio Frequency (RF) and Electromagnetic Compatibility (EMC) requirements for Active Antenna Array System (
        AAS) base station,” Tech. Rep., 2013. azimuth_beamwidth = 65 (degree) backward_attenuation = 30 (dB)
        """
        BS_user_azimuth_angle_list = range(-180, 180, 5)
        gain_list = []
        for BS_user_azimuth_angle in BS_user_azimuth_angle_list:
            gain_list.append(
                self.antenna_element_horizonal_radiation_pattern(BS_user_azimuth_angle))
        plt.plot(BS_user_azimuth_angle_list, gain_list, label=r'$A_{E,\phi}$')
        plt.xlabel(r'$\phi$ (deg)')
        plt.ylabel('Gain (dB)')
        plt.title('Horizontal radiation antenna pattern')
        plt.grid()
        plt.legend(loc='best')
        plt.show()

    def antenna_element_vertical_radiation_pattern(self, BS_user_elevation_angle):
        """
        :return:  A_E_V (dB)
        """
        A_E_V = -min(
            12 * ((BS_user_elevation_angle - self.elevation_antenna_orientation) / self.elevation_beamwidth) ** 2,
            self.backward_attenuation)
        return A_E_V

    def plot_antenna_element_vertical_radiation_pattern(self):
        """
         elevation_antenna_orientation = 90 (degree)
        elevation_beamwidth = 65 (degree)
        backward_attenuation = 30 (dB)
        """
        BS_user_elevation_angle_list = range(-10, 190, 5)
        gain_list = []
        for BS_user_elevation_angle in BS_user_elevation_angle_list:
            gain_list.append(
                self.antenna_element_vertical_radiation_pattern(BS_user_elevation_angle))
        plt.plot(BS_user_elevation_angle_list, gain_list, label=r'$A_{E,\theta}$')
        plt.xlabel(r'$\theta$ (deg)')
        plt.ylabel('Gain (dB)')
        plt.title('Vertical radiation antenna pattern')
        plt.grid()
        plt.legend(loc='best')
        plt.show()

    def antenna_element_radiation_pattern(self, BS_user_elevation_angle, BS_user_azimuth_angle):
        """
        BS antennas have multiple antenna panels. An antenna panel has MxN antenna elements (N-number of columns,
        M-number of antenna elements in the same polarization in each column. Element radiation pattern describes
        how the power of a single anntena element is radiated in all directions,defined by any pair of vertical and
        horizontal angles.
        :param BS_user_elevation_angle: 0<theta<180
        :param BS_user_azimuth_angle: -180<phi<180
        :param elevation_antenna_orientation: tilt angle
        :param elevation_beamwidth: vertical 3dB beamwidth
        :param azimuth_beamwidth: horizontal 3dB beamwidth
        :param backward_attenuation: maximum side lobe level attenuation
        :return: relative antenna gain (dB) of an antenna element in directions(theta, phi)
        """
        A_E_V = self.antenna_element_vertical_radiation_pattern(BS_user_elevation_angle)
        A_E_H = self.antenna_element_horizonal_radiation_pattern(BS_user_azimuth_angle)
        A_E = self.maximum_antenna_element_gain - min(-(A_E_V + A_E_H), self.backward_attenuation)
        return A_E

    def antenna_radiation_pattern(self, A_E, AF):
        """
        TODO: Implement the matrix multiplication for getting the array factor
        Defines the relation between the array radiation pattern and the single element radiation pattern.
        :return:
        """
        pass

    def antenna_field_pattern(self):
        pass


class Antenna_Pattern_gNB(AntennaPatterns):
    def __init__(self, gNB_antenna_type):
        super().__init__()
        self.gNB_antenna_type = gNB_antenna_type
        if self.gNB_antenna_type == "3TRxP":
            self.elevation_antenna_orientation = 90  # degree
            self.elevation_beamwidth = 65  # degree
            self.azimuth_beamwidth = 65  # degree
            self.backward_attenuation = 30  # dB
            self.maximum_antenna_element_gain = 8  # dBi
        elif self.gNB_antenna_type == "Indoor":
            self.elevation_antenna_orientation = 90  # degree
            self.elevation_beamwidth = 90  # degree
            self.azimuth_beamwidth = 90  # degree
            self.backward_attenuation = 25  # dB
            self.maximum_antenna_element_gain = 5  # dBi
        else:
            raise NameError("Wrong gNB antenna pattern selected")

    def calc_gNB_antenna_element_radiation_pattern(self, BS_user_elevation_angle, BS_user_azimuth_angle):
        A_E = self.antenna_element_radiation_pattern(BS_user_elevation_angle, BS_user_azimuth_angle)
        return A_E


class Antenna_Pattern_UE(AntennaPatterns):
    def __init__(self, device_antenna_type):
        super().__init__()
        self.UE_antenna_type = device_antenna_type
        if self.UE_antenna_type == "Omnidirectional":
            pass
        elif self.UE_antenna_type == "Directional":
            self.elevation_antenna_orientation = 90  # degree
            self.elevation_beamwidth = 90  # degree
            self.azimuth_beamwidth = 90  # degree
            self.backward_attenuation = 25  # dB
            self.maximum_antenna_element_gain = 5  # dBi
        else:
            raise NameError("Wrong UE antenna pattern selected")

    def calc_gNB_antenna_element_radiation_pattern(self, BS_user_elevation_angle, BS_user_azimuth_angle):
        A_E = self.antenna_element_radiation_pattern(BS_user_elevation_angle, BS_user_azimuth_angle)
        return A_E


def perform_exhaustive_search_to_find_best_phi_theta(antenna_gnb):
    best_pattern = None
    best_theta = None
    best_phi = None
    for theta in range(0, 180, 5):
        for phi in range(-180, 180, 5):
            A_E = antenna_gnb.calc_gNB_antenna_element_radiation_pattern(theta, phi)
            # if A_E > 0:
            #     print(f"For theta = {theta}, phi = {phi}: {A_E} dB")
            if not best_pattern or best_pattern < A_E:
                best_pattern = A_E
                best_phi = phi
                best_theta = theta
    print(f"Best parameters: phi = {best_phi}, theta={best_theta}: {best_pattern} dB")


def main():
    antenna_gnb = Antenna_Pattern_gNB("3TRxP")
    antenna_gnb.plot_antenna_element_vertical_radiation_pattern()
    antenna_gnb.plot_antenna_element_horizonal_radiation_pattern()

    perform_exhaustive_search_to_find_best_phi_theta(antenna_gnb)


if __name__ == "__main__":
    main()
