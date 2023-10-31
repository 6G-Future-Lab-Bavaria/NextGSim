import logging


class ServicePlacement(object):
    """
    A placement (or allocation) algorithm controls where to locate the service all_services and their replicas in the different nodes of the topology, according to load criteria, or other objectives.

    .. note:: A class interface

    Args:
        name (str): associated name

        activation_distribution (): a generation_distribution function to active the *run* function in execution period

    Kwargs:
        param (dict): the parameters of the *activation_dist*

    """

    def __init__(self, name, activation_distribution=None, logger=None):
        self.name = name
        self.activation_distribution = activation_distribution
        self.number_of_services = []
        self.logger = logger or logging.getLogger(__name__)

    def set_number_of_services(self, num_of_services):
        self.number_of_services = num_of_services

    def initial_allocation(self, sim, app_name):
        """
        Given an ecosystem, it starts the allocation of all_services in the topology.

        Args:
            sim (:mod:cm_edge.core.MECSimulation)
            app_name (String)

        . attention:: override required
        """

    def run(self, sim):
        """
        This method will be invoked during the ran_simulation to change the assignment of the all_services to the topology

        Args:
            sim (:mod: cm_edge.core.MECSimulation)
        """
        self.logger.debug("JUST TO TEST at Time: %f", sim.env.now)
