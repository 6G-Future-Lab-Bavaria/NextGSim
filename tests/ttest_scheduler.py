from gnb.Scheduler import Scheduler
from device.Device import Device
from gnb.GnB import GnB
from plotting.ScenarioVisualization import ScenarioVisualization
import numpy as np
from runtime.Simulation import Simulation


def main():
    simulation = Simulation()
    # scenario = Indoor()
    # simparams = SimulationParameters()

    for i in range(10):
        user = Device(ID=i, x=30 + i*10, y=0, transmit_power=0, simulation=simulation)
        # device = Device(ID=i, x=30, y=0, transmit_power=0)
        simulation.devices_per_scenario.append(user)

    for i in range(2):
        x = 10 + i*20
        y = 10
        gnb = GnB(ID=i, x=x, y=y, simulation=simulation)
        simulation.gNBs_per_scenario.append(gnb)

    num_users = 5
    num_prbs = 7
    num_gnbs = 2

    scheduler = Scheduler(simulation)
    received_power_matrix = [[[0,1], [0,1], [0,1], [0,1], [1,0], [1,0], [1,0]],
                             [[0,1], [0,1], [0,1], [0,1], [1,0], [1,0], [1,0]],
                             [[0,1], [0,1], [0,1], [0,1], [1,0], [1,0], [1,0]],
                             [[0,1], [0,1], [0,1], [0,1], [1,0], [1,0], [1,0]],
                             [[0,1], [0,1], [0,1], [0,1], [1,0], [1,0], [1,0]]
                             ]
    received_power_matrix = np.array(received_power_matrix)

    for TTI in range(1):
        scheduler.schedule(received_power_matrix, 'Round Robin', TTI)


    visualization = ScenarioVisualization(simulation)
    visualization.plot_allocation(with_allocation_flag=True)


main()