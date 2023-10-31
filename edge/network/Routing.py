import logging
import networkx as nx


def get_path(topology, src_node, dst_node, method='dijkstra'):
    path = list(nx.shortest_path(topology.G, source=src_node, target=dst_node, method=method))
    best_path = path
    return best_path


class Routing(object):
    """
    A routing_policies algorithm that routes the messages from sender to receiver.

    .. note:: A class interface
    """

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def get_path(self, topology, src_node, dst_node):
        self.logger.debug("Routing")
        """ Define Routing """
        path = []
        ids = []
        """ End Routing """
        return path, ids


class ShortestPathRouting(Routing):
    def get_path(self, topology, src_node, dst_node, method='dijkstra'):
        """
        Computes the shortest path from the source service to the destination service.
        Return the shortest path. Uses the 'shortest_path' method of NetworkX library.
        Can use 'dijkstra' or 'bellman-ford' methods.
        """
        path = list(nx.shortest_path(topology.G, source=src_node, target=dst_node, method=method))
        best_path = path

        print("BEST PATH")
        print(best_path)

        return best_path
