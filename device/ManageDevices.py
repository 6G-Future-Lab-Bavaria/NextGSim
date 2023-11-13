import numpy as np
from runtime.data_classes import States, MeasurementParams


class ManageDevices:
    def __init__(self, simulation):
        self.simulation = simulation
        self.sim_params = simulation.sim_params
        self.gNBs_per_scenario_ID = simulation.gNBs_per_scenario_ID
        self.devices_per_scenario = simulation.devices_per_scenario
        self.devices_per_scenario_ID = simulation.devices_per_scenario_ID
        self.end_TTI = 0

    def activate_devices_every_tti(self, expected_num_device_arrivals, num_active_devices_previous_TTI, all_active_devices_ID, TTI):
        if self.simulation.TTI % MeasurementParams.traffic_generation_periodicity == 0:
            self.generate_traffic_devices()
        if self.simulation.seed:
            np.random.seed(self.simulation.seed)
        num_active_devices_this_TTI = int(self.sim_params.scenario.max_num_devices_per_scenario *
                                          (expected_num_device_arrivals[TTI] - expected_num_device_arrivals[
                                              self.sim_params.initial_TTI])) * self.sim_params.num_cells
        num_active_devices = num_active_devices_this_TTI - num_active_devices_previous_TTI
        if len(self.devices_per_scenario_ID) > num_active_devices:
            active_devices_IDs = np.random.choice(self.devices_per_scenario_ID, num_active_devices, replace=False)  # random.sample()
            num_active_devices_previous_TTI = num_active_devices_this_TTI
        else:
            active_devices_IDs = self.devices_per_scenario_ID.copy()
            num_active_devices_previous_TTI = len(self.devices_per_scenario_ID)
            # initial connection of the device to the network IDLE->CONNECTED and traffic generation
        for device_ID in active_devices_IDs:
            device = self.devices_per_scenario[device_ID]
            self.simulation.gNBs_per_scenario[device.my_gnb.ID].add_connected_device(device)
            self.devices_per_scenario_ID.remove(device_ID)
            device.RRC_Setup()
            device.generate_device_traffic(TTI, self.end_TTI)
        all_active_devices_ID.extend(active_devices_IDs)
        return all_active_devices_ID, num_active_devices_previous_TTI

    def manage_devices_states(self, TTI_packet_event):
        devices_ID_with_packets = [event.device_ID for event in TTI_packet_event]
        for device_ID in devices_ID_with_packets:
            device = self.devices_per_scenario[device_ID]
            if not device.state == States.rrc_connected:
                device.RRC_Resume()
            self.simulation.gNBs_per_scenario[device.my_gnb.ID].add_connected_device(device)

        for gNB in self.simulation.gNBs_per_scenario:
            for connected_device in gNB.connected_devices:
                if connected_device.ID not in devices_ID_with_packets and not connected_device.get_buffer_stats():
                    connected_device.increase_inactivity_timer()
                    if connected_device.my_connected_device_inactivity_time == connected_device.RRC_connected_data_inactivity_timer:
                        connected_device.RRC_Suspend()
                        self.simulation.gNBs_per_scenario[connected_device.my_gnb.ID].add_inactive_device(
                            connected_device)
        for device in self.devices_per_scenario:
            print(device.ID, "-->", device.state, "my gNB = ", device.my_gnb.ID)

    # functions added from Alba - change them is needed
    def calc_distance_users_gnbs_2d(self):
        distance_users_gnbs_2d = np.zeros((len(self.devices_per_scenario_ID),
                                           len(self.simulation.gNBs_per_scenario)), float)
        for gNB in self.simulation.gNBs_per_scenario:
            for ue in self.devices_per_scenario:
                distance_users_gnbs_2d[ue.ID, gNB.ID] = float(np.sqrt((ue.x - gNB.x) ** 2 + (ue.y - gNB.y) ** 2))
        return distance_users_gnbs_2d

    #TODO: delete the connected device list
    def select_cell(self):
        distance_users_gnbs_2d = self.calc_distance_users_gnbs_2d()
        best_gnb = np.argmin(distance_users_gnbs_2d, axis=1)
        for user in self.devices_per_scenario:
            # assert user.state == States.rrc_idle, f'To perform initial allocation, user {user.ID} must be in RRC idle'
            user.my_gnb = self.simulation.gNBs_per_scenario[best_gnb[user.ID]]
            # add latency of transferring from idle to connected
            # print(f"Initial connection: UE {user.ID} --> {user.my_gnb.ID}")
            self.simulation.gNBs_per_scenario[best_gnb[user.ID]].idle_devices.append(user)
            if not self.sim_params.traffic_model:
                user.state = States.rrc_connected
                user.my_gnb.connected_devices.append(user)
        return distance_users_gnbs_2d

    def generate_traffic_devices(self):
        self.simulation.event_chain.delete()
        self.end_TTI = self.simulation.TTI + MeasurementParams.traffic_generation_periodicity
        for device_ID in self.simulation.all_active_devices_ID:
            device = self.devices_per_scenario[device_ID]
            device.generate_device_traffic(self.simulation.TTI, self.end_TTI)

    def init_buffers(self):
        for ue in self.simulation.devices_per_scenario:
            ue.init_buffer(self.simulation)
