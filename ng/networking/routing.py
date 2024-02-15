from abc import abstractmethod

# routing does both l3 and l2 resolution
# so given a l3 address, we receive the local output interface' as well as the remote interface's address

class Routing:

    class RoutingTable:

        def __init__(self, routing: "Routing", node):
            self.node = node
            self.routing = routing

        def get_next_hop(self, n1):
            return self.routing.get_next_hop(self.node, n1)

    def __init__(self, sim):
        self.sim = sim

    def get_routing_table(self, node):
        return Routing.RoutingTable(self, node)

    # returns [if0, if1]
    @abstractmethod
    def get_next_hop(self, n0, n1):
        pass


class ShortestPathRouting(Routing):

    def get_next_hop(self, n0, n1):
        path = self.sim.network.shortest_path(n0, n1)
        if path is None:
            return None
        next_node = path[1]  # next in path
        return self.sim.network.get_interfaces(n0, next_node)
