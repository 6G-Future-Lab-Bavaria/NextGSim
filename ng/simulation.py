import simpy

from metrics import MetricWriter
from ng.networking.network import NetworkTopology
from ng.eventlog import EventLog
from physical import PhysicalEnvironment, Coords2D


class Simulation:

    def __init__(self, routing_t, orchestrator_t, ms_per_ts=1):          # default: 1 time step = 1 millisecond
        self.env = simpy.Environment()
        # todo remove:
        self.physical = PhysicalEnvironment(Coords2D(0, 0), Coords2D(200, 100))
        self.eventlog = EventLog(self.env)
        self.network = NetworkTopology(self.env)
        self.ms_per_ts = ms_per_ts
        self.routing = routing_t(self)
        self.orchestrator = orchestrator_t(self)
        self.metric_writer = MetricWriter(self)

    def run(self, until):
        self.env.run(until)

    def now(self):
        return self.env.now

    def wait_ms(self, ms):
        steps = ms / self.ms_per_ts
        return self.env.timeout(steps)

    @staticmethod
    def from_config(config):
        default = {
            "ms_per_ts": 1
        }
        config = { **default, **config } # merge dicts

        return Simulation(
            config["routing"]["_type"],
            config["orchestrator"]["_type"],
            config["ms_per_ts"],
        )

