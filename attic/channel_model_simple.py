import numpy as np


class ChannelModelBasic:
    distance_vs_CQI_dict = {1200: 7, 1000: 8, 800: 10, 500: 12, 200: 15}
    # todo: Shall CQI drop to zero when UE is too far?

    def __init__(self, total_number_of_PRBs):
        self.total_number_of_PRBs = total_number_of_PRBs

    def _get_max_achievable_CQI(self, distance):
        """ Calculate maximum achievable CQI value for the UEs based on their distance from the gNB """
        """From matlab:Mapping between distance from gNB (key in meters) and maximum achievable UL CQI value (value).  
        For example, if a UE is 700 meters away from the gNB, it can achieve a maximum CQI value of 10 
        as the distance falls within the [501, 800] meters range, as per the mapping."""
        CQI_max = 0
        for dist, CQI in ChannelModelBasic.distance_vs_CQI_dict.items():
            if distance <= dist:
                CQI_max = CQI
        return CQI_max

    def _get_distance_btw_UE_and_gNB(self, UE_position, gNB_position):
        UE_x, UE_y = UE_position
        gNB_x, gNB_y = gNB_position
        return np.sqrt((UE_x-gNB_x)**2 + (UE_y-gNB_y)**2)

    def get_CQIs(self, device_parameters, gNB_position):
        """ The value of CQI for each PRB, for each UE, is calculated randomly
                and is limited by the maximum achievable CQI value """
        CQI_per_UE_per_PRB_dict = {}
        for i in range(len(device_parameters)):
            distance = self._get_distance_btw_UE_and_gNB(device_parameters[i]['device_positions'], gNB_position)
            CQI_max = self._get_max_achievable_CQI(distance)
            CQI_per_UE_per_PRB_dict[i] = list(np.random.uniform(1, CQI_max, self.total_number_of_PRBs))
        return CQI_per_UE_per_PRB_dict
