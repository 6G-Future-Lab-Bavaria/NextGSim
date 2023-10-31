# @Author: Alba Jano, Anna Prado
# @Date: 2020-11-15
# @Email: alba.jano@tum.de, anna.prado@tum.de
# @Last modified by: Alba Jano

import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
import numpy as np
from runtime.utilities import generate_color_list, show_shape


# class CreateHardcodedScenario:
#     def __init__(self, sim_params, num_rows, num_cols):
#         self.sim_params = sim_params
#         self.start_position = [0, 0]
#         self.radius = sim_params.scenario.cell_radius  # from the center of a hexagon to a vertex
#         self.num_rows = num_rows
#         self.num_cols = num_cols
#         self.hexagons = []
#         self.final_gnbs_pos_and_col = []
#         self.fig = plt.figure(698)
#         self.ax = self.fig.gca()
#
#     def create_hexagons(self):
#         hexagons = []
#         x_pos = [0, 2*self.radius]
#         y_pos = [0, 0]
#         for x, y in zip(x_pos, y_pos):
#             hexagon = RegularPolygon((x, y), numVertices=6, radius=self.radius, alpha=0.2, edgecolor='k',
#                                      orientation=np.pi / 2)
#             hexagon.set_color('red')
#             self.ax.add_patch(hexagon)
#             plt.plot(hexagon.xy)
#
#         plt.show()


class CreateHexagons:
    def __init__(self, sim_params, num_rows, num_cols):
        self.sim_params = sim_params
        self.start_position =[0, 0]
        self.radius = sim_params.scenario.cell_radius  # from the center of a hexagon to a vertex
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.hexagons = []
        self.limits = self.get_limits()
        self.limits[0][0] -= (self.radius)
        self.limits[0][1] += (self.radius)
        self.limits[1][0] -= (self.radius)
        self.limits[1][1] += (self.radius)
        self.col_i = 0
        self.fig = plt.figure(555)
        self.ax = self.fig.gca()
        self.final_gnbs_pos_and_col = []
        self.served_hexagons = []
        self.served_hexagons_colors = []
        self.colors = ['red', 'green', 'black', 'blue', 'orange', 'pink', 'brown', 'yellow']
        self.colors.extend(generate_color_list(self.num_rows * self.num_cols))
        self.flag_text_gnb_positions = True

    def create_hexagons(self):
        self.hexagons = self.get_hexagons()
        gnbs = self.get_first()
        gnbs_2 = self.get_second(gnbs)
        gnbs_3 = self.get_third(gnbs)
        gnbs_4 = self.get_second(gnbs_3)

        self.final_gnbs_pos_and_col.extend(gnbs)
        self.final_gnbs_pos_and_col.extend(gnbs_2)
        self.final_gnbs_pos_and_col.extend(gnbs_3)
        self.final_gnbs_pos_and_col.extend(gnbs_4)
        # hardcode one more gNB
        if self.sim_params.num_cells == 20 and self.sim_params.scenario.inter_site_dist_macro == 500:
            self.final_gnbs_pos_and_col.append([-150, 875, self.colors[self.col_i]])
        if self.sim_params.num_cells == 10 and self.sim_params.max_cells_in_one_row == 3 \
                and self.sim_params.scenario.inter_site_dist_macro == 500:
            x = 433 - 288 * 2
            y = 875
            self.final_gnbs_pos_and_col.append([x, y, self.colors[self.col_i]])
        self.color_hexagons()

    def get_hexagons(self):
        hexagons = []
        positions_temp = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                hexagon = self.generate_hexagon(i, j)
                hexagons.append(hexagon)
                positions_temp.append(hexagon.xy)
        self.check_isd_macro(positions_temp)
        return hexagons

    def generate_hexagon(self, i, j):
        x = self.start_position[0] + j * self.radius * 1.5
        y = self.start_position[0] + i * self.radius * 2 * np.cos(30 * np.pi / 180) + 0.5 * self.radius * np.cos(
            30 * np.pi / 180) * (-1) ** j
        hexagon = RegularPolygon((x, y), numVertices=6, radius=self.radius, alpha=0.2, edgecolor='k',
                                 orientation=np.pi / 2)
        return hexagon

    def get_limits(self):
        limits = []
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                hexagon = self.generate_hexagon(i, j)
                x = hexagon.xy[0]
                y = hexagon.xy[1]
                # print(x, y)
                if not limits:
                    limits = [[x, x], [y, y]]
                    # print(f"First {limits}")
                elif np.sqrt(x**2 + y**2) > np.sqrt(limits[0][1]**2 + limits[1][1]**2):
                            limits[0][1] = x
                            limits[1][1] = y
                            # print(f"Further {limits}")
        return limits

    def get_first(self):
        gnbs = []
        first = None
        for hexagon in self.hexagons:
            if not first:
                first = [hexagon.xy[0] + self.radius, hexagon.xy[1]]
            else:
                first[0] += 3 * self.radius
            if self.limits[0][0] <= first[0] <= self.limits[0][1] and self.limits[1][0] <= first[1] <= self.limits[1][1]:
                gnbs.append([first[0], first[1], self.colors[self.col_i]])
                # plt.text(first[0], first[1], "1")
                self.col_i += 1
        return gnbs

    def get_second(self, gnbs):
        gnbs_2 = []
        for gnb in gnbs:
            x = gnb[0]
            y = gnb[1]
            # print(f"Hexagon 2nd {x}, {y}")
            while self.limits[1][0] <= y <= self.limits[1][1]:
                y += 6 * self.radius * np.cos(30 * np.pi / 180)
                if self.limits[0][0] <= x <= self.limits[0][1] and self.limits[1][0] <= y <= self.limits[1][1]:
                    gnbs_2.append([x, y, self.colors[self.col_i]])
                    # plt.text(x, y, "2")
                    self.col_i += 1
        return gnbs_2

    def get_third(self, gnbs):
        gnbs_3 = []
        second = []
        for gnb in gnbs:
            new_x = gnb[0] + 1.5 * self.radius
            new_y = gnb[1] - 3 * self.radius * np.cos(30 * np.pi / 180)
            second.append([new_x, new_y])
        for gnb in second:
            x = gnb[0]
            y = gnb[1]
            # print(f"Hexagon 3rd {x}, {y}")
            y += 6 * self.radius * np.cos(30 * np.pi / 180)
            if self.limits[0][0] <= x <= self.limits[0][1] and self.limits[1][0] <= y <= self.limits[1][1]:
                gnbs_3.append([x, y, self.colors[self.col_i]])
                self.col_i += 1
        return gnbs_3

    def plot_hexagons(self, color):
        for hexagon in self.hexagons:
            hexagon.set_color(color)
            self.ax.add_patch(hexagon)

    def plot_gnbs(self, gnbs, color):
        for gnb in gnbs:
            if not color:
                color = gnb[2]
            plt.scatter(gnb[0], gnb[1], color=color)
            if self.flag_text_gnb_positions:
                plt.text(gnb[0], gnb[1]+10, f"{int(gnb[0])}, {int(gnb[1])}")

    def color_hexagons(self):
        for hexagon in self.hexagons:
            for gnb in self.final_gnbs_pos_and_col:
                center = hexagon.xy
                x = gnb[0]
                y = gnb[1]
                if center[0]-hexagon.radius <= x <= center[0]+hexagon.radius and center[1]-hexagon.radius <= y <= center[1]+hexagon.radius:
                    # print(center, gnb)
                    color = gnb[2]
                    hexagon.set_color(color)
                    self.served_hexagons.append(hexagon)
                    self.served_hexagons_colors.append(color)

    def plot_colored_hexagons(self):
        for hexagon in self.hexagons:
            hexagon.set_color('grey')
            hexagon.set_fill(0)
            self.ax.add_patch(hexagon)

        for hexagon, color in zip(self.served_hexagons, self.served_hexagons_colors):
            hexagon.set_color(color)
            hexagon.set_fill(1)
            self.ax.add_patch(hexagon)

    def add_micro_gnbs(self,):
        # h = self.sim_params.scenario.inter_site_dist_macro / 2
        h = self.sim_params.scenario.inter_site_dist_micro
        small_gnbs_center = []
        for gnb in self.served_hexagons:
            # small cell top left
            x, y = gnb.xy[0], gnb.xy[1]
            x -= np.sqrt(3) * h / 6
            y += h / 2
            small_gnbs_center.append([x, y])
            # small cell bottom left
            x, y = gnb.xy[0], gnb.xy[1]
            x -= np.sqrt(3) * h / 6
            y -= h / 2
            small_gnbs_center.append([x, y])
            # small cell middle right
            x, y = gnb.xy[0], gnb.xy[1]
            x += h / np.cos(30 * np.pi / 180) / 2
            small_gnbs_center.append([x, y])
        return small_gnbs_center

    def plot_micro_cells(self, small_gnbs_center):
        # h = self.sim_params.scenario.inter_site_dist_macro / 2
        h = self.sim_params.scenario.inter_site_dist_micro
        for cell in small_gnbs_center:
            x, y = cell
            plt.scatter(x, y, color='black')
            if self.flag_text_gnb_positions:
                plt.text(x, y+ 10, f"{int(x)}, {int(y)}")
            circle = plt.Circle((x, y,), radius=h/2, fill=False, color='grey', linestyle='--')
            show_shape(circle)
            print(f"Small cell's ISD is {h} m")

    def check_isd_micro(self, small_gnbs_center):
        for i in range(0, 12+1, 3):
            for one in small_gnbs_center[i:i+3]:
                for two in small_gnbs_center[i:i+3]:
                    x1, y1 = one
                    x2, y2 = two
                    res = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                    if res == 0 or 198 < res < 201:
                        pass
                    else:
                        assert 0, f"Micro ISD must be 200 m, but ISD = {res} m"

    def check_isd_macro(self, cells):
        for one in cells:
            for two in cells:
                x1, y1 = one[0], one[1]
                x2, y2 = two[0], two[1]
                res = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                # if res > 0:
                #     print(f"ISD macro is {res} m ")


def plot_area():
    # 1000 x 1000 m area with 4 macro BSs; shift the positions of BSs such that this area is from 0 to 1000 m
    length = width = 1000
    x_min = -120
    x_max = x_min + length
    y_min = -120
    y_max = y_min + width
    plt.plot([x_min, x_max], [y_min, y_min], color='black')
    plt.plot([x_min, x_max], [y_max, y_max], color='black')
    plt.plot([x_min, x_min], [y_min, y_max], color='black')
    plt.plot([x_max, x_max], [y_min, y_max], color='black')


def main():
    from runtime.SimulationParameters import SimulationParameters
    sim_params = SimulationParameters()
    hexagon_maker = CreateHexagons(sim_params, num_rows=2, num_cols=3)
    hexagon_maker.create_hexagons()
    hexagon_maker.plot_colored_hexagons()
    hexagon_maker.plot_gnbs(hexagon_maker.final_gnbs_pos_and_col, None)
    small_gnbs_center = hexagon_maker.add_micro_gnbs()
    hexagon_maker.check_isd_micro(small_gnbs_center)
    hexagon_maker.plot_micro_cells(small_gnbs_center)
    plt.autoscale()
    plot_area()
    plt.savefig("../hexagons.png")

    for x, y, col in hexagon_maker.final_gnbs_pos_and_col:
        print(f"{col} macro gNB with {x}, {y}")

    # hardcoded_hexagons = CreateHardcodedScenario(sim_params, num_rows=2, num_cols=2)
    # hardcoded_hexagons.create_hexagons()


if __name__ == "__main__":
    main()




