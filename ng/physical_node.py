from ng.networking.node import Node

# a node with a physical locations
# this should be an interface or something?
# maybe not even anything, i.e. anyting with a location defines that directly

class PhysicalNode(Node):

    def __init__(self, sim, id, coords):
        super().__init__(sim, id)
        self.coords = coords
