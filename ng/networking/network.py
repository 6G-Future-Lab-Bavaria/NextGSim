from networkx import MultiDiGraph, shortest_path as sp
from networkx.exception import NetworkXNoPath

# network is multidigraph
# nodes are node ids
# edges are indexed by [if0,if1]

class NetworkTopology:

    def __init__(self, env):
        self.env = env
        self.graph = MultiDiGraph()
        self.nodes = []

    def register_node(self, node):
        self.nodes.append(node)
        self.graph.add_node(node.id)

    def get_links(self):
        for n0, n1, a in self.graph.edges(data=True):
            edges = self.graph[n0][n1].keys() # list of connected interfaces
            for [if0, if1] in edges:
                yield [n0, if0, n1, if1]

    # network.link: ifs get connected
    # if.onconnect => up(), link is active and data can be sent
    # because links can be buses and contain multiple peers, one link corresponds to multiple edges in network graph!!
    # => if linkend disconnects, remove edges [n0.if0, *]
    # => link object must keep edges per interface/linkend
    # for simplicity, dont implement up/down yet, but only connect/disconnect

    def link(self, if0, if1):
        return self.graph.add_edge(if0.node.id, if1.node.id, key=(if0.id, if1.id))

    def unlink(self, if0, if1):
        self.graph.remove_edge(if0.node.id, if1.node.id, key=(if0.id, if1.id))

    def get_interfaces(self, n0, n1): # get interfaces for link from n0 to n1
        edges = self.graph[n0][n1]
        return list(edges.keys())[0] # take first option (could be abstracted, todo)

    def remove_node(self, node_id):
        self.graph.remove_node(node_id)

    def shortest_path(self, n0, n1):
        try:
            return sp(self.graph, source=n0, target=n1)
        except NetworkXNoPath:
            return None

    def has_route(self, n0, n1):
        return self.shortest_path(n0, n1) is not None