import numpy as np
import math
from abc import ABC
from shapely.geometry import Point
from device.Device import Device
from gnb.GnB import GnB


class InitialSetUp(ABC):
    def __init__(self, simulation):
        self.simulation = simulation
        self.sim_params = self.simulation.sim_params
        self.room_limits = [None, None]
        self.hexagon_maker = None

    def create_users(self):

        if not self.room_limits:
            raise ValueError(f"In Setup file, room limits are not set (first gNBs must be created, and only then users")
        self.enlarge_room_limits_to_the_walls()
        # print(f"Creating users within these limits {self.room_limits}")
        devices_per_scenario = []
        user_coordinates = []
        x_range = [self.room_limits[0][0], self.room_limits[0][1]]
        y_range = [self.room_limits[1][0], self.room_limits[1][1]]
        for user_id in range(self.sim_params.scenario.max_num_devices_per_scenario):
            radius = self.sim_params.scenario.cell_radius
            x = np.random.uniform(low=x_range[0]+radius/4, high=x_range[1]-radius/4, size=1)
            y = np.random.uniform(low=y_range[0]+radius/4, high=y_range[1]-radius/4, size=1)
            max_speed = np.random.uniform(0.1, 6)
            user = Device(user_id, x, y, self.room_limits[0][0], self.room_limits[0][1], self.room_limits[1][0],
                          self.room_limits[1][1], max_speed,  self.sim_params.scenario.device_transmit_power, self.simulation)
            user_coordinates.append([int(x), int(y)])
            devices_per_scenario.append(user)
        # self.log(f"Created {len(devices_per_scenario)} users located within X:[{x_range}], Y:[{y_range}]")
        return devices_per_scenario, np.array(user_coordinates)

    def generate_gnb_position(self, gnb_id):
        pass

    def enlarge_room_limits_to_the_walls(self):
        pass


class InitialSetUpIndoor(InitialSetUp):
    def create_gnbs(self):
        gNBs_per_scenario = []
        for gnb_id in range(self.sim_params.num_cells):
            x, y = self.generate_gnb_position(gnb_id)
            gNB = GnB(gnb_id, x, y, self.simulation)
            gNBs_per_scenario.append(gNB)
        return gNBs_per_scenario

    def generate_gnb_position(self, id):
        assert self.sim_params.scenario.scenario == 'Indoor'
        if id < self.sim_params.max_cells_in_one_row:
            x = id * 20  # + 10
            y = 20
        else:
            id = id % self.sim_params.max_cells_in_one_row
            x = 10 + id * 20
            y = 15 + 20
        if self.room_limits == [None, None]:  # and id == 0:
            self.room_limits = [[x, x], [y, y]]
        self.room_limits[0][0] = min(self.room_limits[0][0], x)
        self.room_limits[0][1] = max(self.room_limits[0][1], x)
        self.room_limits[1][0] = min(self.room_limits[1][0], y)
        self.room_limits[1][1] = max(self.room_limits[1][1], y)
        return x, y

    def enlarge_room_limits_to_the_walls(self):
        try:
            self.room_limits[0][0] -= 10
            self.room_limits[0][1] += 10
            self.room_limits[1][0] -= 15
            self.room_limits[1][1] += 15
        except TypeError:
            self.room_limits = [[0, self.sim_params.scenario.x_max], [0, self.sim_params.scenario.y_max]]


class InitialSetUpIndoorFactory(InitialSetUp):
    def create_gnbs(self, radius):
        gNBs_per_scenario = []
        gNB_coordinates = self.sim_params.scenario.gNB_coordinates
        for gnb_id in range(len(gNB_coordinates)):
            x = gNB_coordinates[gnb_id, 0]
            y = gNB_coordinates[gnb_id, 1]
            gNB = GnB(gnb_id, x, y, self.simulation)
            gNBs_per_scenario.append(gNB)
        self.room_limits = [[0, 120], [0, 60]]
        return gNBs_per_scenario


class InitialSetUpOutdoor(InitialSetUp):

    def get_user_within_hexagon(self, hexagon, user_id):
        center_x = hexagon.xy[0]
        center_y = hexagon.xy[1]
        x_range = [center_x - self.sim_params.scenario.cell_radius, center_x + self.sim_params.scenario.cell_radius]
        y_range = [center_y - self.sim_params.scenario.cell_radius, center_y + self.sim_params.scenario.cell_radius]
        while True:
            x = np.random.uniform(low=x_range[0], high=x_range[1], size=1)
            y = np.random.uniform(low=y_range[0], high=y_range[1], size=1)
            point = Point(x, y)
            contains_flag = hexagon.contains(point)
            if contains_flag[0]:
                user = Device(user_id, x, y, self.sim_params.scenario.transmit_power, self.simulation)
                return user

    def set_num_serving_cells_of_gnb(self, gnb, hexagons):
        num_seving_cells = 0
        x_gnb = gnb.x
        y_gnb = gnb.y
        for hexagon in hexagons:
            point = Point(x_gnb, y_gnb)
            contains_flag = hexagon.contains(point)[0]
            if contains_flag:
                num_seving_cells += 1
        gnb.num_serving_cells = num_seving_cells

    def create_gnbs(self, radius):
        gNBs_per_scenario = []
        diameter = 2*radius
        nr_cells = self.sim_params.num_cells
        nr_columns = round(np.sqrt(nr_cells))
        nr_rows = round(np.sqrt(nr_cells))
        add_column = nr_cells%(nr_columns*nr_rows)
        if add_column!=0:
            nr_columns+=1
        right_limit = (nr_columns/2)*diameter + (nr_columns/2)*(radius/2)
        upper_limit = nr_rows*diameter - radius
        self.room_limits = [[0, right_limit], [0, upper_limit]]
        x_coord = np.zeros((nr_columns,nr_rows))
        y_coord = np.zeros((nr_columns,nr_rows))
        id = np.array(range(0, nr_cells))
        id = np.pad(id.astype(float), (0, nr_columns * nr_rows - id.size),
               mode='constant', constant_values=np.nan).reshape((nr_columns, nr_rows))
        for gNB in range(0, nr_cells):
            i, j = np.where(id == gNB)
            if i[0] % 2 == 0:
                x_coord[i[0]][j[0]] = radius + i[0] * ((diameter - radius / 2) - math.sin(math.pi / 3) * radius / 4)
                y_coord[i[0]][j[0]] = radius + j[0] * (diameter - radius / 2)
            else:
                x_coord[i[0]][j[0]] = radius + i[0] * ((diameter - radius / 2) - math.sin(math.pi / 3) * radius / 4)
                y_coord[i[0]][j[0]] = radius + j[0] * (diameter - radius / 2) + math.cos(math.pi / 3) * (
                            radius + radius / 2)
            gNB_obj = GnB(gNB, x_coord[i[0]][j[0]], y_coord[i[0]][j[0]], self.simulation)
            gNB_obj.type = 'macro'
            gNBs_per_scenario.append(gNB_obj)
        return gNBs_per_scenario
