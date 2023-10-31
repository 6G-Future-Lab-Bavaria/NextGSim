# @Author: Alba Jano, Anna Prado
# @Date: 2020-11-15
# @Email: alba.jano@tum.de, anna.prado@tum.de
# @Last modified by: Alba Jano

from edge.entities.Entity import Entity


class GnB(Entity):
    def __init__(self, ID, x, y, simulation):
        self.sim_param = simulation.sim_params
        # self.sim_traffic = simulation.traffic_generator
        self.scenario = simulation.sim_params.scenario
        self.event_chain = simulation.event_chain
        self.type = None
        self.ID = ID
        self.x = x
        self.y = y
        self.transmit_power = None
        self.connected_devices = []  # fixme: set()
        self.inactive_devices = []
        self.idle_devices = []

        self.available_resources = self.init_available_resources()
        self.sinr_stats_of_connected_ues = {}
        self.hexagon = None  # to store hexagon object for the outdoor scenario
        self.num_serving_cells = 3  # for UMi might be 1 or 2;
        self.prepared_CHO_for_users = []  # fixme: set()
        self.remove_prep_cells_at = {}
        self.my_controller = None

        # Added by Mert
        super().__init__()

    def reset_statistics(self):
        self.connected_devices = []  # fixme: set()
        self.inactive_devices = []
        self.idle_devices = []

    def init_available_resources(self):
        if self.scenario.scenario == 'Indoor' or 'IndoorFactory':
            return self.sim_param.scenario.num_PRBs
        elif self.type == 'macro':
            return self.sim_param.scenario.num_PRBs_macro
        else:
            return self.sim_param.scenario.num_PRBs_micro

    def set_zero_available_resources(self):
        self.available_resources = 0

    def add_available_resources(self, nPRBs):
        self.available_resources += nPRBs

    def get_available_resources(self):
        return self.available_resources

    def add_connected_device(self, device):
        try:
            if device not in self.connected_devices:
                self.connected_devices.append(device)
                if device in self.inactive_devices:
                    self.inactive_devices.remove(device)
                elif device in self.idle_devices:
                    self.idle_devices.remove(device)
        except:
            raise ValueError('Wrong device format')

    def add_inactive_device(self, device):
        try:
            self.inactive_devices.append(device)
            if device in self.connected_devices:
                self.connected_devices.remove(device)
            elif device in self.idle_devices:
                self.idle_devices.remove(device)
        except:
            raise ValueError('Wrong device format')

    def add_idle_device(self, device):
        try:
            self.idle_devices.append(device)
        except:
            raise ValueError('Wrong device format')
        if device in self.connected_devices:
            self.connected_devices.remove(device)
        elif device in self.inactive_devices:
            self.inactive_devices.remove(device)

    def connect_to_controller(self, controller):
        self.my_controller.disconnect_gnb(self)
        self.my_controller = controller
        self.my_controller.connect_gnb(self)
