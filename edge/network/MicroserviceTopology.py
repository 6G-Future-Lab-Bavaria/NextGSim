# -*- coding: utf-8 -*-
import logging
import networkx as nx
import warnings
import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


class MicroserviceTopology:
    """
    This class unifies the functions to deal with **Complex Networks** as a network topology within the simulator.
    In addition, it facilitates its creation, and assignment of attributes.
    """

    INSTANCE = None

    def __init__(self, logger=None):
        """ Virtually private constructor. """
        if MicroserviceTopology.INSTANCE is not None:
            pass
        else:
            self.services = []
            self.G = nx.DiGraph()
            self.G_pos = {}
            self.plainG = nx.DiGraph()
            self.plainG_pos = {}
            self.nodes = {}
            self.logger = logger or logging.getLogger(__name__)
            MicroserviceTopology.INSTANCE = self

    def __new__(cls, *args, **kwargs):
        if MicroserviceTopology.INSTANCE:
            return MicroserviceTopology.INSTANCE
        else:
            inst = object.__new__(cls)
            return inst

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

    def add_node(self, service):
        self.services.append(service)
        self.G.add_node(service)
        self.G_pos[service.entity_id] = [service.x, service.y]

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

    def get_info(self):
        return self.nodes

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

    def load(self, topology):
        self.G = nx.DiGraph()
        self.plainG = nx.DiGraph()

        for edge in topology["links"].values():
            self.G.add_edge(edge.source.entity_id, edge.destination.entity_id, BW=edge.bandwidth,
                            LATENCY=edge.latency)
            if not (edge.source.model == "sensor" or edge.source.model == "actuator"
                    or edge.destination.model == "sensor" or edge.destination.model == "actuator"):
                self.plainG.add_edge(edge.source.entity_id, edge.destination.entity_id, BW=edge.bandwidth,
                                     LATENCY=edge.latency)

        for node in topology["entities"].values():
            self.nodes[node.entity_id] = node
            self.G_pos[node.entity_id] = node.location
            if not ((node.model == 'sensor') or (node.model == 'actuator')):
                self.plainG_pos[node.entity_id] = node.location

        cpu_speed_values = {}
        for node in topology["entities"].values():
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

