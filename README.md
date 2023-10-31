# NextGSim

NextGSim provides a simulation environment focusing on resource management aspects in mobile edge computing scenarios. It consists of mainly two parts: Radio Simulation and Edge Computing
simulation. These two simulations are loosely connected to enable both independent and joint use.

# Simulated Architecture

Simulated architecture resembles a joint management server, where edge and radio related information is simultaneously updated 
to edge orchestrator and SD-RAN controller. Therefore, novel resource allocation, offloading decision and orchestration algorithms can be tested through NextGSim. 

<p align="center">
  <img src="doc/Simulated_Architecture.png" width="55%">
  <p align="center">
    Figure 1: Relationship between EdgeCloudSim modules.
  </p>

# Radio Simulation
Flow-based 5G simulator based on 3GPP standartization and SOA papers. The project includes the following classes/modules:
1. RANSimulation.py - main file, which workflow is shown in documentation/simulator_workflow.png 
2. SimParams.py - data class with simulation parameters (simulation duration, scenario, bandwidth, frequency, etc)
3. Scenarios.py - data class with scenario parameters: Outdoor that includes macro and micro gNBs; Indoor only macro gNB
4. TrafficGenerator.py - aggregated traffic models are implemented for activation of the devices. Packets have a defined size with Poisson distributed inter-arrival time.
5. mobility folder - RWP and SLAW mobility models to mobility patterns of the users. 
6. Scheduler.py - Round Robin scheduling algorithm 
7. Device.py - stores device related information such as gNB to which it is connected, RRC state, energy consumption for state transitions, device position (x, y), handover related latencies, etc. 
8. ChannelModel.py - 3GPP channel model for indoor, outdoor scenarios
9. Handover.py, NormalHandover, CondtionalHandover.py - implementation of handover algorithms 
10. ThroughputCaclulation.py - thoughput is calculated based on SINR and number of PRBs using the formula from 3GPP. 
The throughput calculation is verified using this calculator: https://5g-tools.com/5g-nr-throughput-calculator/
11. Visualization.py - used to plot UE mobility and UE's allocation either only at the begining of the simulation, at every TTI or when a flag is set (e.g. after a handover). 
12. folder tests - contains some tests, which need to be updated. 
13. data_classes.py - contain some constants and parameter values such as channel measurement periodicity, traffic generation periodicity, traffic models, frequencies, UE position update periodicity, handover parameters, etc. 
14. InitialSetUp.py - creates gNB and UE's objects and generates the indoor and outdoor topologies. 
15. ProcessResults.py - saves the results after the simulation (results.json, sinr over time plots). 
16. plot_channel_results.py - to plot channel parameters (SINR, LoS probability, Pathloss vs. distance) 

NOTE: The words device, UE and user are used interchangebly in the readme and in the code. 

1. Outdoor topology with hexagons: 
-Set the scenario to Outdoor() and num_cells in SimParams. gNBs are generated within an area, parameter max_cells_in_one_row decides how many cells fit horizontally. The number of cells will be smaller than the number you set because some the cells on the edges do not have a gNB 
(cells without color filling that do not have a gnb).  Then 3 micro gNBs are added to every small cell. 
- To set the cell grid arbitrarily (e.g. 3x7), go to Outdoor Scenario) and set num_rows and num_cols manually, num_cells must be set to None in this case. 
-Colored cells belong to one gNB. Edge cells without filling will not be used. 

2. Link Budge calculator for 5G channel: https://5g-tools.com/5g-nr-link-budget-calculator/

Unit Tests:
1. To test channel models, run test_channel_3gpp_with_np.py. 

The code works with Python 3.8. With Python 3.7, there are some errors with plots in plot_channel_results.py because the input lists require some reshaping.

# Edge Computing Simulation
Edge Computing part consists of 3 main modules that are Application, Entities and
Network.

<ins>Application</ins>: An application is defined by its services which form a directed
acyclic graph(DAG). Microservices can generate, receive and process messages. In such a scenario, a task is completed
when the last microservice in a DAG, processes its message. Different users can share microservices at the edge or have
a dedicated microservice for themselves.

<ins>Entities</ins>: Entities implemented are Edge Server, Orchestrator, CPU and Router. Edge servers are the computing
nodes that serves users at the edge of the network. They are controlled by the orchestrator which decides where to deploy services,
which services users need to be assigned to, forward radio related information to services and if necessary migrate services
between edge servers. 

CPU module defines the processing behaviour of the services. Different processing behaviour can be implemented
module. As a proof-of-concept example a latency aware processing algorithm is implemented, where messages from users that suffer 
higher radio link latency is prioritized, in order to increase the chance of meeting the deadline of the task.

Router is a simple entity that routes messages between entities like edge servers and base stations. Currently, it only implements
shortest path algorithm for routing.

<ins>Network</ins>: This module implements the topology between entities and microservices. Physical entities 
are connected to each other with links that are defined by their bandwidth and latency.



