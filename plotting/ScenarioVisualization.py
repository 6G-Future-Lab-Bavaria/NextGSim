# @Author: Alba Jano
# @Date: 2020-11-15
# @Email: alba.jano@tum.de
# @Last modified by: Alba Jano

from matplotlib.patches import RegularPolygon
import matplotlib.pyplot as plt
from runtime.utilities import generate_color_list
from runtime.utilities import enable_print, block_print
from runtime.data_classes import States, HandoverAlgorithms
from runtime.utilities import show_shape
import plotting.plot_channel_results
from matplotlib.pyplot import cm
import numpy as np
import math





class ScenarioVisualization:
    def __init__(self, simulation, save_allocation_plots):
        self.sim = simulation
        self.save_allocation_plots = save_allocation_plots
        self.hexagon_maker = None
        self.user_speed_metrics = None
        self.radius_mean = None
        self.mean_snr_at_radius = None
        self.std_snr_at_radius = None
        self.plot_snr_vs_distance_flag = False

    def plot_allocation(self, tti, users_who_made_ho):
        if tti == 0 and self.sim.sim_params.with_mobility and self.sim.sim_params.scenario.scenario == 'UMi':
            self.get_radius_coverage_outdoor()
            self._plot_gNBs()
            self.hexagon_maker.plot_colored_hexagons()
            # plot_mobility(self.mec_simulation.X_mobility, self.mec_simulation.Y_mobility,
            #               len(self.mec_simulation.devices_per_scenario), self.user_speed_metrics, self.mec_simulation.results_name)
            plt.cla()
            # fig = plt.figure(1)
            # self.camera = Camera(fig)        if self.save_allocation_plots or users_who_made_ho or tti == 0:
        # self._plot_users_and_connections(users_who_made_ho)
        self._plot_gNBs()
        if self.sim.sim_params.hardcoded_initial_setup:
            plt.xlim(self.sim.setup.room_limits[0])
            plt.ylim(self.sim.setup.room_limits[1])
        elif self.sim.sim_params.scenario.scenario == 'Indoor':
            plt.xlim([-10, self.sim.sim_params.scenario.x_max + 10])
            plt.ylim([0, self.sim.sim_params.scenario.y_max + 10])
        else:
            plt.xlim([self.sim.setup.room_limits[0][0] , self.sim.setup.room_limits[0][1] ])
            plt.ylim([self.sim.setup.room_limits[1][0] , self.sim.setup.room_limits[1][1] ])
        # plt.legend()
        # plt.title(f"Allocation for {len(self.simulation.devices_per_scenario)} users and {len(self.simulation.gNBs_per_scenario)} gNBs, "
        #           f"TTI = {tti}")

        if self.hexagon_maker:
            # Note: For hexagon visualization disable other plots like scheduling.
            self.hexagon_maker.plot_colored_hexagons()
            # self.hexagon_maker.plot_gnbs(self.hexagon_maker.final_gnbs_pos_and_col, None) # to highlight macro gNBs
        # folder = 'allocation' + self.simulation.results_name
        # check_if_directory_with_results_exists(folder)
        # plt.savefig(f"results/{folder}/allocation_{str(tti).zfill(3)}.png", dpi=500)
        # plt.cla()
        plt.show()

    def _plot_users_and_connections(self, users_who_made_ho):
        counter = counter_ho = 0
        counter_connected = counter_idle = counter_inactive = counter_handover_process = counter_handover_prep = 0
        rlf_counter = 0
        for user in self.sim.devices_per_scenario:
            if user.ID in users_who_made_ho:
                color = 'red'
                plt.scatter(user.x, user.y, label='User made HO' if counter_ho == 0 else "", color=color, s=15, marker='o')
                counter_ho += 1
            elif user in self.sim.monitor_rlf.not_connected_users_due_to_rlf_till:
                color = 'orange'
                plt.scatter(user.x, user.y, label='RLF-RACH' if rlf_counter == 0 else "", color=color, s=15, marker='o')
                rlf_counter += 1
            else:
                color = 'blue'
                plt.scatter(user.x, user.y, label='User' if counter == 0 else "", color=color, s=15, marker='o')
                counter += 1
            plt.legend()
            # sinr = self.simulation.channel.measured_SINR[user.ID, user.my_gnb.ID]
            # msg = f"id {user.ID} {round(sinr, 1)}"
            msg = f"id {user.ID}"
            plt.text(user.x + 0.1, user.y + 0.1, msg)
            self.text_cho_prep_cells(user)
            if self.save_allocation_plots:
                if user.hit_finish and user.hit_finish > 0:
                    color = 'pink'
                    label = 'HIT'
                    counter_handover_process += 1
                    plt.plot([user.x, user.my_gnb.x], [user.y, user.my_gnb.y], color=color,
                             label=label if counter_handover_process == 1 else "")
                elif user in self.sim.monitor_rlf.not_connected_users_due_to_rlf_till:
                    # RLF, user is idle
                    pass

                elif user.handover_prep_time_finish and user.handover_prep_time_finish > 0:
                    color = 'grey'
                    label = 'Handover preparation'
                    counter_handover_prep += 1
                    plt.plot([user.x, user.my_gnb.x], [user.y, user.my_gnb.y], color=color,
                             label=label if counter_handover_prep == 1 else "")
                elif user.state == States.rrc_connected:
                    color = 'green'
                    label = 'Connected'
                    counter_connected += 1
                    plt.plot([user.x, user.my_gnb.x], [user.y, user.my_gnb.y], color=color,
                             label=label if counter_connected == 1 else "")
                elif user.state == States.rrc_idle:
                    color = 'red'
                    label = 'Idle'
                    counter_idle += 1
                    plt.plot([user.x, user.my_gnb.x], [user.y, user.my_gnb.y], color=color,
                             label=label if counter_idle == 1 else "")
                elif user.state == States.rrc_inactive:
                    color = 'blue'
                    label = 'Inactive'
                    counter_inactive += 1
                    plt.plot([user.x, user.my_gnb.x], [user.y, user.my_gnb.y], color=color,
                             label=label if counter_inactive == 1 else "")
                else:
                    raise ValueError("No such user state")

                # if self.simualtion.sim_params.hardcoded_initial_setup:
                #     plt.text(user.x-10, user.y+5, user.msg_scheduler_1)
                #     plt.text(user.x - 10, user.y + 10, user.msg_scheduler_2)
            # self.camera.snap()

    def _plot_gNBs(self, with_coverage=True):
        counter_macro = counter_micro = 0
        color_map = cm.get_cmap("twilight_shifted")
        color = color_map(np.linspace(0, 1, len(self.sim.gNBs_per_scenario)))
        # x_coordinates = np.array(range(self.mec_simulation.setup.room_limits[0][0], self.mec_simulation.setup.room_limits[0][1]))
        # y_coordinates = np.array(range(self.mec_simulation.setup.room_limits[1][0], self.mec_simulation.setup.room_limits[1][1]))
        # x, y = np.meshgrid(x_coordinates, y_coordinates)
        #
        # num_users = len(np.array(np.meshgrid(x_coordinates, y_coordinates)).T.reshape(-1, 2))
        # self.mec_simulation.set_channel()
        # self.mec_simulation.channel.generate_test_users(x_coordinates, y_coordinates, num_users)
        # SINR = np.max(np.mean(self.mec_simulation.channel.calc_SNR(),2),0).reshape(x.shape)


        # # plt.hexbin(self.mec_simulation.channel.user_coordinates[:,0],self.mec_simulation.channel.user_coordinates[:,1],SINR, cmap="RdYlBu_r")
        # im = plt.imshow(SINR[:30], interpolation='bilinear', extent=[self.mec_simulation.setup.room_limits[0][0],self.mec_simulation.setup.room_limits[0][1],self.mec_simulation.setup.room_limits[1][0],self.mec_simulation.setup.room_limits[1][1]])
        # plt.colorbar()
        # plt.show()
        for gNB, c in zip(self.sim.gNBs_per_scenario, color):
            if self.sim.sim_params.scenario.scenario == 'UMi' and with_coverage:
                self.plot_gnb_coverage(gNB)
            if gNB.type == 'macro':
                color = 'red'
                label = 'Macro BS'
                size = 150
                plt.scatter(gNB.x, gNB.y, label=label if counter_macro == 0 else "", color=color, s=size, marker='*')
                counter_macro += 1
                plt.text(gNB.x + 0.1, gNB.y + 0.3, str(gNB.ID))
            else:
                color = 'black'
                label = 'Micro gNB'
                size = 70
                circle = plt.Circle((gNB.x, gNB.y), 10,  color=c,  alpha=0.4,  linestyle='-', linewidth=1)
                circle1 = plt.Circle((gNB.x, gNB.y), 15,  color=c,  alpha=0.1,  linestyle='-', linewidth=1)
                plt.gca().add_patch(circle)
                plt.gca().add_patch(circle1)
                plt.scatter(gNB.x, gNB.y, label=label if counter_micro == 0 else "", color=color, s=size, marker='*')
                counter_micro += 1
        plt.legend()

    def plot_gnb_coverage(self, gnb):
        if gnb.type == 'macro':
            radius = 500
            # radius = self.radius_mean[0]
        elif gnb.type == 'micro':
            radius = 125
            # radius = self.radius_mean[1]
        circle = plt.Circle((gnb.x, gnb.y,), radius=radius, fill=False, color='grey', linestyle='--')
        show_shape(circle)

    def get_radius_coverage_outdoor(self):
        plt_channel = plotting.plot_channel_results.PlotChannel()
        self.mean_snr_at_radius, self.std_snr_at_radius, self.radius_mean = \
            plt_channel.plot_snr_vs_distance(plot_flag=self.plot_snr_vs_distance_flag)
        enable_print()
        print(f"UMa: at mean radius {self.radius_mean[0]} m, SNR = {self.mean_snr_at_radius[0]} dB, "
              f"std SNR = {self.std_snr_at_radius[0]}")
        print(f"UMi: at mean radius {self.radius_mean[1]} m, SNR = {self.mean_snr_at_radius[1]} dB, "
              f"std SNR = {self.std_snr_at_radius[0]}")
        block_print(self.sim.sim_params.disable_print)

    def text_cho_prep_cells(self, user):
        if self.sim.sim_params.handover_algorithm == HandoverAlgorithms.conditional_5g \
                and self.sim.sim_params.scenario.scenario == 'Indoor':
            msg = "Preparing cells:"
            for cell in user.currently_being_prep_cells_finish_time.keys():
                msg += f" {cell.ID}"
            plt.text(-20, 2.5, msg)
            msg = "Prepared cells:"
            for cell in user.prepared_gnbs:
                msg += f" {cell.ID}"
            plt.text(-20, 1.5, msg)

    @staticmethod
    def drawArrow(A, B, color):
        plt.arrow(A[0], A[1], B[0] - A[0], B[1] - A[1],
                  head_width=0.5, length_includes_head=True, color=color)

    def plot_mobility(self, X, Y, num_users):
        # todo: add plot when the user exactly made a HO
        self._plot_gNBs()
        colors = generate_color_list(num_users + 1)
        for user_id in range(num_users):
            plt.plot(X[user_id], Y[user_id], color=colors[user_id])
            # plt.scatter(X[user_id][0], Y[user_id][0], color=colors[user_id], marker='*')
            plt.text(X[user_id][0], Y[user_id][0], f"UE {user_id}")
            for t in range(len(X[0])-1):
                self.drawArrow((X[user_id][t], Y[user_id][t]), (X[user_id][t + 1], Y[user_id][t + 1]),
                               color=colors[user_id])

        plt.savefig("plots/mobility.png")
        # plt.show()


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

