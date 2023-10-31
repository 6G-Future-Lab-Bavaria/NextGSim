# @Author: Polina Kutsevol
# @Date: 2021-04-12
# @Email: kutsevol.pn@phystech.edu
# @Last modified by: Polina Kutsevol

from runtime.utilities import block_print, enable_print
from controller.Allocation import Optimization
import time

class ControlHandover():
    def __init__(self, simulation):
        self.simulation = simulation
        self.control_handover_periodicity = 3000
        self.transmission_to_app_ongoing = False
        self.transmission_to_app_finish_time = None
        self.allocation_ongoing = False
        self.allocation_finish_time = None
        self.transmission_to_control_ongoing = False
        self.transmission_to_control_finish_time = None
        self.database_transmission_ongoing = False
        self.database_transmission_finish_time = None
        self.handover_ongoing = False
        self.transmission_to_app_latency = 100
        self.transmission_to_control_latency = 100
        self.database_transmission_latency = 100
        self.best_controllers_id = [gNB.my_controller.ID for gNB in self.simulation.gNBs_per_scenario]
        self.allocation = Optimization(len(simulation.gNBs_per_scenario), len(simulation.controllers_per_scenario))


    def control_handover_function(self):
        if self.simulation.TTI % self.control_handover_periodicity == 0 and not self.handover_ongoing:
            enable_print()
            print("start handover at tti", self.simulation.TTI)
            block_print()
            self.handover_ongoing = True
            self.transmission_to_app_ongoing = True
            self.transmission_to_app_finish_time = self.simulation.TTI + self.transmission_to_app_latency
        elif self.transmission_to_app_ongoing and self.simulation.TTI < self.transmission_to_app_finish_time:
            return
        elif self.transmission_to_app_ongoing and self.simulation.TTI >= self.transmission_to_app_finish_time:
            enable_print()
            print("transmitted to app_name at tti", self.simulation.TTI)
            block_print()
            self.transmission_to_app_ongoing = False
            self.allocation_ongoing = True
            self.perform_allocation()
        elif self.allocation_ongoing and self.simulation.TTI < self.allocation_finish_time:
            return
        elif self.allocation_ongoing and self.simulation.TTI >= self.allocation_finish_time:
            enable_print()
            print("start transmission to control at tti", self.simulation.TTI)
            block_print()
            self.allocation_ongoing = False
            self.transmission_to_control_ongoing = True
            self.transmission_to_control_finish_time = self.simulation.TTI + self.transmission_to_control_latency
        elif self.transmission_to_control_ongoing and self.simulation.TTI < self.transmission_to_control_finish_time:
            return
        elif self.transmission_to_control_ongoing and self.simulation.TTI >= self.transmission_to_control_finish_time:
            self.transmission_to_control_ongoing = False
            enable_print()
            print("transmit database at tti", self.simulation.TTI)
            block_print()
            self.database_transmission_ongoing = True
            self.database_transmission_finish_time = self.simulation.TTI + self.database_transmission_latency
        elif self.database_transmission_ongoing and self.simulation.TTI < self.database_transmission_finish_time:
            return
        elif self.database_transmission_ongoing and self.simulation.TTI >= self.database_transmission_finish_time:
            enable_print()
            print("transmitted database at tti", self.simulation.TTI)
            block_print()
            self.database_transmission_ongoing = False
            self.handover_ongoing = False
            for i in range(len(self.simulation.gNBs_per_scenario)):
                if self.simulation.gNBs_per_scenario[i].my_controller != self.simulation.controllers_per_scenario[self.best_controllers_id[i]]:
                    enable_print()
                    print("Control handover")
                    block_print()
                    self.simulation.gNBs_per_scenario[i].connect_to_controller(self.simulation.controllers_per_scenario[self.best_controllers_id[i]])


    def perform_allocation(self):
        enable_print()
        print("allocation at tti", self.simulation.TTI)
        block_print()
        start_time = time.time()
        ues_per_gnbs = []
        for gnb in self.simulation.gNBs_per_scenario:
            ues_per_gnbs.append(len(gnb.connected_devices))
        self.init_allocation()
        self.allocation.perform_alloc(ues_per_gnbs)
        self.best_controllers_id = self.allocation.best_controllers
        allocation_time = (time.time() - start_time)/(self.simulation.sim_params.TTI_duration/1000)
        self.allocation_finish_time = self.simulation.TTI + allocation_time

    def init_allocation(self):
        x_array = []
        y_array = []
        for gnb in self.simulation.gNBs_per_scenario:
            x_array.append(gnb.x)
            y_array.append(gnb.y)
        for controller in self.simulation.controllers_per_scenario:
            x_array.append(controller.x)
            y_array.append(controller.y)
        coordinates = [x_array, y_array]

        self.allocation.initiate_alloc(coordinates, self.best_controllers_id)
        self.allocation.set_seed(self.simulation.seed)
