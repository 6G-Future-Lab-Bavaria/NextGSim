import json
import os

from networkx import MultiDiGraph


class NetworkLogger:

    def __init__(self, sim):
        self.sim = sim
        self.states = []
        self.timestamps = []

    def log_state(self, network: MultiDiGraph):
        t = self.sim.env.now
        self.states.append(network.copy())
        self.timestamps.append(t)

    def get_states(self, from_ts=None, to_ts=None):
        i = 0
        n = len(self.timestamps)
        j = n
        if from_ts is not None:
            while i < n and self.timestamps[i] < from_ts:
                i += 1
        if to_ts is not None:
            while j > i and self.timestamps[j-1] > to_ts:
                j -= 1
        return self.timestamps[i:j], self.states[i:j]

    @staticmethod
    def write_states_to_disk(states, path):
        # could also split in multiple files
        with open(os.path.join(path, "topologies"), "w") as f:
            json.dump(states, f)

    @staticmethod
    def load_states_from_disk(path):
        with open(os.path.join(path, "topologies")) as f:
            return json.load(f)
