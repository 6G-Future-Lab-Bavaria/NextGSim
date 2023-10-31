import logging.config
import os

from core.core import SimThread, SimConfig
from pathlib import Path
from application_examples.ar_pipeline import ARPipeline
from edge.network.NetworkTopology import NetworkTopology
from attic.BaseStation import BaseStation
from attic.SimpleDevice1 import SimpleDevice1
from edge.entities.EdgeServer import EdgeServer
from edge.entities.orchestrator.EdgeOrchestrator import EdgeOrchestrator
from network.link import add_link

# region Configurations
results_directory = Path("../examples/results/")
results_directory.mkdir(parents=True, exist_ok=True)
results_directory = str(results_directory) + "/"
sim_config = SimConfig(running_time=100,
                       plot_latency=False,
                       plot_topology=False,
                       show_csv=True,
                       is_ran_scheduling_in_use=True,
                       is_ran_simulator_in_use=False,
                       location_update=True,
                       computing_period=0.2,
                       reporting_period=0.3,
                       location_update_period=1,
                       ran_granularity=1000,
                       ran_csv_dir='../sim_params/config_test_3.json',
                       mec_csv_dir='../attic/drafts/MEC.csv')
# endregion

if __name__ == '__main__':
    file_name = os.path.basename(__file__)
    t = NetworkTopology()
    sim = SimThread(sim_config=sim_config)
    n_ue = 2

    bs_1 = BaseStation()
    bs_2 = BaseStation()
    es_1 = EdgeServer()
    add_link(es_1, bs_1)
    add_link(bs_1, es_1)
    add_link(es_1, bs_2)
    add_link(bs_2, es_1)
    orchestrator = EdgeOrchestrator()
    es_1.bind_to_orchestrator(orchestrator)
    for _ in range(n_ue):
        tmp_ue = SimpleDevice1(num_of_cpus=5, velocity=10)
        tmp_ue.bind_to_orchestrator(orchestrator)
        tmp_ue.deploy_app(ARPipeline())

    vm_request = {"num_of_cpus": 5, "storage": 10000000, "bw": 10000}
    es_1.deploy_app_to_server(ARPipeline())
    orchestrator.update_service_map()
    log_file_path = Path(__file__).parent / 'logging.ini'
    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    sim.start()
