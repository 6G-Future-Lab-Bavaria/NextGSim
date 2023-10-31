# -*- coding: utf-8 -*-
import logging
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt

DISABLED_TYPES_IN_TOPOLOGY = ["Vm", "Sensor", "Actuator"]


def filter_topology_plot(link):
    if link.source.__class__.__name__ in DISABLED_TYPES_IN_TOPOLOGY or \
            link.destination.__class__.__name__ in DISABLED_TYPES_IN_TOPOLOGY:
        return False
    else:
        return True


class NetworkTopology:
    """
    This class unifies the functions to deal with **Complex Networks** as a network topology within the simulator.
    In addition, it facilitates its creation, and assignment of attributes.
    """

    INSTANCE = None

    def __init__(self, logger=None):
        """ Virtually private constructor. """
        if NetworkTopology.INSTANCE is not None:
            pass
        else:
            self.entities = []
            self.G = nx.DiGraph()
            self.G_pos = {}
            self.plainG = nx.DiGraph()
            self.plainG_pos = {}
            self.nodes = {}
            self.logger = logger or logging.getLogger(__name__)
            NetworkTopology.INSTANCE = self

    def __new__(cls, *args, **kwargs):
        if NetworkTopology.INSTANCE:
            return NetworkTopology.INSTANCE
        else:
            inst = object.__new__(cls)
            return inst

    def add_node(self, node):
        self.entities.append(node)
        self.G.add_node(node)
        self.G_pos[node.entity_id] = [node.x, node.y]


    def get_edges(self):
        """
        Returns:
            list: a list of graph edges, i.e.: ((1,0),(0,2),...)
        """
        return self.G.edges

    def get_edge(self, key):
        """
        Args:
            key: an edge identifier, i.e. (1,9)

        Returns:
            a list of edge attributes
        """
        if key in self.G.edges:
            return self.G.edges[key]
        else:
            return {}

    def get_nodes(self):
        """
        Returns:
            list: a list of all nodes features
        """
        return self.G.nodes

    def get_node(self, node_id):
        """
        Args:
            node_id (int): ID of the service

        Returns:
            service (): Returns the service object
        """
        return self.G.node[node_id]


    def create_topology_from_graph(self, G):
        """
        It generates a topology from a NetworkX graph

        Args:
             G (*networkx.classes.graph.Graph*)
        """

        if isinstance(G, nx.classes.digraph.DiGraph):
            self.G = G
        else:
            raise TypeError

    # def load(self, topology):
    def load(self, entities, links):
        self.G = nx.DiGraph()
        self.plainG = nx.DiGraph()

        for edge in links.values():
            self.G.add_edge(edge.source.entity_id, edge.destination.entity_id, bandwidth=edge.bandwidth,
                            latency=edge.latency)
            if filter_topology_plot(edge):
                self.plainG.add_edge(edge.source.entity_id, edge.destination.entity_id, bandwidth=edge.bandwidth,
                                     latency=edge.latency)

        for node in entities.values():
            self.nodes[node.entity_id] = node
            self.G_pos[node.entity_id] = node.location
            if node.__class__.__name__ not in DISABLED_TYPES_IN_TOPOLOGY:
                self.plainG_pos[node.entity_id] = node.location

        cpu_speed_values = {}
        for node in entities.values():
            if hasattr(node, 'cpu_clock_speed'):
                cpu_speed_values[node.entity_id] = node.cpu_clock_speed

        nx.set_node_attributes(self.G, values=cpu_speed_values, name="cpu_clock_speed")


    def get_nodes_att(self):
        """
        Returns:
            A dictionary with the features of the nodes
        """
        return self.nodes

    def find_device_by_model(self, model):
        matched_devices = []

        for node in self.nodes.values():
            if node.model == model:
                matched_devices.append(node)

        return matched_devices

    def find_mobile_devices(self):
        matched_devices = []

        for node in self.nodes.values():
            if node.is_mobile_device:
                matched_devices.append(node)

        return matched_devices

    def find_mobile_device_by_model(self, model):
        matched_devices = []

        for node in self.nodes.values():
            if node.model == model:
                matched_devices.append(node)

        return matched_devices

    def show_topology(self):
        for entity in self.entities:
            entity.update_coordinates()

        node_colours = ['blue' if node.__class__.__name__ == 'GnB' else
                        'red' if node.__class__.__name__ == 'EdgeServer' else
                        'magenta' if node.__class__.__name__ == 'Device' else
                        'green' for node in self.entities]

        node_labels = {}
        for i in range(len(self.entities)):
            node_labels[i] = self.entities[i].entity_id

        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(22, 13)
        nx.draw_networkx_nodes(self.G, self.G_pos, cmap=plt.get_cmap('jet'), node_size=1000, node_color=node_colours,
                               alpha=0.5)
        nx.draw_networkx_edges(self.G, self.G_pos, edge_color='r', arrows=True)
        plt.show()


def get_topology():
    return NetworkTopology().G

