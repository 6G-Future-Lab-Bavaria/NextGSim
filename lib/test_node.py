from networking.node import Node
from simulation import Simulation


class TestNode(Node):

    def __init__(self, sim: Simulation, id, ifs):
        super().__init__(sim, id, ifs)

        def link_after_delay():
            yield sim.wait_ms(200)
            sim.network.link(self.intf("eth0"), sim.network.nodes[2].intf("eth1"))
            yield sim.env.process(unlink_after_delay())

        def unlink_after_delay():
            yield sim.wait_ms(300)
            sim.network.unlink(self.intf("eth0"), sim.network.nodes[2].intf("eth1"))

        sim.env.process(link_after_delay())
