from matplotlib.patches import RegularPolygon
import matplotlib.pyplot as plt
from runtime.utilities import generate_color_list
from runtime.utilities import enable_print, block_print
from runtime.data_classes import States, HandoverAlgorithms
from runtime.utilities import show_shape
from matplotlib.pyplot import cm
import numpy as np
import math


class scenario_visualization:
    def __init__(self, simulation):
        self.sim = simulation
        self.fig, self.ax = plt.subplots(1)
        self.set_labelf = True

    def visualize(self, predefined: bool = False):
        self.visualize_gNBs(predefined)
        # TODO: Solve the connection problem
        # self.visualize_UEs(RRC_states, connection)
        plt.xlabel('Scenario length (m)')
        plt.ylabel('Scenario width (m)')
        plt.legend()
        # plt.show()

    def visualize_gNBs(self, predefined: bool = False):
        radius = self.sim.sim_params.scenario.cell_radius
        micro_colour = 'black'
        macro_color = 'red'
        micro_label = 'Micro gNB'
        macro_label = 'Macro gNB'
        micro_size = 70
        macro_size = 150
        micro_counter = 0
        micro_gNB_p = True
        x=[]
        y=[]
        color_map = cm.get_cmap("twilight_shifted")
        color = color_map(np.linspace(0, 1, len(self.sim.gNBs_per_scenario)))
        for gNB, c in zip(self.sim.gNBs_per_scenario, color):
            if predefined:
                circle = plt.Circle((gNB.x, gNB.y), 10,  color=c,  alpha=0.4,  linestyle='-', linewidth=1)
                circle1 = plt.Circle((gNB.x, gNB.y), 15,  color=c,  alpha=0.1,  linestyle='-', linewidth=1)
                plt.gca().add_patch(circle)
                plt.gca().add_patch(circle1)
                plt.scatter(gNB.x, gNB.y, label=micro_label if micro_counter == 0 else "", color=micro_colour, s=micro_size, marker='*')
                micro_counter = 1
            else:
                circle = plt.Circle((gNB.x, gNB.y), radius=radius, alpha=0.1, color=c)
                self.ax.add_patch(circle)
                self.macro_gNB(radius=radius, x_macro=gNB.x, y_macro=gNB.y, n=1, ax=self.ax, col=c, micro=micro_gNB_p)
                self.macro_gNB(radius=radius, x_macro=gNB.x, y_macro=gNB.y, n=3, ax=self.ax, col=c,  micro=micro_gNB_p)
                self.macro_gNB(radius=radius, x_macro=gNB.x, y_macro=gNB.y, n=5, ax=self.ax, col=c,  micro=micro_gNB_p)
                x.append(gNB.x)
                y.append(gNB.y)
        self.set_labelf = True
        self.ax.scatter(x, y, color=macro_color, marker='*', s=macro_size, label=macro_label if self.set_labelf == True else '')
        plt.gca().set_xlim(left=0)
        plt.gca().set_ylim(bottom=0)

    def micro_gNB(self,radius, x_sector, y_sector, n, ax):
        x_micro = x_sector + math.sin(n*math.pi/3)*radius/4
        y_micro = y_sector + math.cos(n*math.pi/3)*radius/4
        ax.scatter(x_micro, y_micro, color='black', marker='*', label='Micro gNB' if self.set_labelf == True else '')
        self.set_labelf = False
        circle = plt.Circle((x_micro,y_micro), radius=radius/5, edgecolor='black', alpha=0.1, linestyle='--')
        ax.add_patch(circle)

    def macro_gNB(self,radius, x_macro, y_macro, n, ax, col, micro=True):
        x_sector = x_macro + math.sin(n*math.pi / 3) * radius/2
        y_sector = y_macro + math.cos(n*math.pi / 3) * radius/2
        hex = RegularPolygon((x_sector, y_sector), numVertices=6, radius=radius/2, alpha=0.4, color=col, edgecolor='black')
        ax.add_patch(hex)
        if micro==True:
            self.micro_gNB(radius=radius, x_sector=x_sector, y_sector=y_sector, n=1, ax=ax)
            self.micro_gNB(radius=radius, x_sector=x_sector, y_sector=y_sector, n=3, ax=ax)
            self.micro_gNB(radius=radius, x_sector=x_sector, y_sector=y_sector, n=5, ax=ax)

    def visualize_UEs(self, RRC_states: bool = False, connection: bool = True):
        colour = 'blue'
        colour_idle = 'red'
        colour_inactive = 'blue'
        colour_connected = 'green'
        label_g ='UE'
        label_idle = 'RRC Idle'
        label_inactive = 'RRC Inactive'
        label_connected = 'RRC Connected'
        counter = 0
        counter_idle = 0
        counter_inactive = 0
        counter_connected = 0
        X = []
        Y = []
        X_gNB =[]
        Y_gNB =[]
        conn = None
        for UE in self.sim.devices_per_scenario:
            # plot identity
            msg = f"id {UE.ID}"
            # plt.text(UE.x + 0.1, UE.y + 0.1, msg)
            if RRC_states:
                if UE.state == States.rrc_idle:
                    self.ax.scatter([UE.x], [UE.y], color=colour_idle, label=label_idle if counter_idle == 0 else "")
                    counter_idle = 1
                    if connection:
                        plt.plot([UE.x, UE.my_gnb.x], [UE.y, UE.my_gnb.y], color=colour_idle, linewidth=0.3)
                elif UE.state == States.rrc_inactive:
                    plt.scatter([UE.x], [UE.y], color=colour_inactive, label=label_inactive if counter_inactive == 0 else "")
                    counter_inactive = 1
                    if connection:
                        plt.plot([UE.x, UE.my_gnb.x], [UE.y, UE.my_gnb.y], color=colour_inactive, linewidth=0.3)
                elif UE.state == States.rrc_connected:
                    plt.scatter([UE.x], [UE.y], color=colour_connected, label=label_connected if counter_connected == 0 else "")
                    counter_connected = 1
                    if connection:
                        plt.plot([UE.x, UE.my_gnb.x], [UE.y, UE.my_gnb.y], color=colour_connected, linewidth=0.3)
                else:
                    ValueError("Wrongly specified user state")
            else:
                X.append(UE.x)
                Y.append(UE.y)
                X_gNB.append(UE.my_gnb.x)
                Y_gNB.append(UE.my_gnb.y)
        pos = self.ax.scatter(X, Y, color=colour, s=5, label=label_g if counter == 0 else "")
        counter = 1
        if connection:
            conn = self.ax.plot([X,X_gNB], [Y, Y_gNB], color=colour, linewidth=0.3)
        plt.pause(0.6)
        while self.ax.lines:
            self.ax.lines[0].remove()
        pos.remove()

