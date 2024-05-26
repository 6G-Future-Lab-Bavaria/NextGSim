import json
import os

from networkx import MultiDiGraph
from typing import List, Tuple


class NetworkLog:

    def __init__(self, sim):
        self.sim = sim
        self.states = []
        self.timestamps = []

    def log_state(self, network: MultiDiGraph):
        t = self.sim.env.now
        self.states.append(network.copy())
        self.timestamps.append(t)

    def get_states(self, from_ts=None, to_ts=None) -> List[Tuple[float, any]]:
        i = 0
        n = len(self.timestamps)
        j = n
        if from_ts is not None:
            while i < n and self.timestamps[i] < from_ts:
                i += 1
        if to_ts is not None:
            while j > i and self.timestamps[j-1] > to_ts:
                j -= 1
        return list(zip(self.timestamps[i:j], self.states[i:j]))

    @staticmethod
    def write_states_to_disk(states: List[Tuple[float, any]], path):
        # could also split in multiple files
        def serialize(graph: MultiDiGraph):
            return {
                "nodes": list(graph.nodes.keys()),
                # links is list of 3-tuples (start,end,key)
                "links": list(graph.edges(keys=True))
            }

        serialized = [[t, serialize(graph)] for t,graph in states]
        with open(os.path.join(path, "topologies"), "w") as f:
            json.dump(serialized, f)

    @staticmethod
    def load_states_from_disk(path):
        def deserialize(data: any):
            graph = MultiDiGraph()
            graph.add_nodes_from(data["nodes"])
            graph.add_edges_from([(s,e,tuple(k)) for s,e,k in data["links"]])
            return graph

        with open(os.path.join(path, "topologies")) as f:
            serialized = json.load(f)

        return [[t, deserialize(data)] for t,data in serialized]
