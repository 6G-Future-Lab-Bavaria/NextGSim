import simpy
from ng.networking.network import NetworkTopology
from ng.eventlog import EventLog


class Simulation:

    def __init__(self, physical_env: "PhysicalEnvironment", routing_t, orchestrator_t, ms_per_ts=1):          # default: 1 time step = 1 millisecond
        self.env = simpy.Environment()
        self.physical = physical_env
        self.eventlog = EventLog(self.env)
        self.network = NetworkTopology(self.env)
        self.ms_per_ts = ms_per_ts
        self.routing = routing_t(self)
        self.orchestrator = orchestrator_t(self)

    def run(self, until):
        self.env.run(until)

    def wait_ms(self, ms):
        steps = ms / self.ms_per_ts
        return self.env.timeout(steps)

