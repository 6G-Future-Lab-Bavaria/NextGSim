from edge.network.NetworkTopology import NetworkTopology
import numpy as np

LINK_COUNTER = 0
LINKS = {}

FIBER_BW = 10 ** 9  # bits per second
FIBER_LATENCY_PER_METER = 0.00333  # milliseconds per meter


class Link:

    def __init__(self, source=None, destination=None, bandwidth=100000, latency=0, link_id=None):
        self.bandwidth = bandwidth
        self.source = source
        self.destination = destination
        self.latency = latency

        if link_id is None:
            self.link_id = get_link_counter()
        else:
            self.link_id = link_id

        # LINKS[mec_simulation.link_id] = mec_simulation
        add_link_to_link_list(self)
        get_and_increment_link_counter()

    def get_bandwidth(self):
        return self.bandwidth

    def update_bandwidth(self, bw):
        self.bandwidth = bw

    def get_latency(self):
        return self.latency

    def update_latency(self, latency):
        self.latency = latency


def get_and_increment_link_counter():
    global LINK_COUNTER
    prev_user_counter = LINK_COUNTER
    LINK_COUNTER += 1
    return prev_user_counter


def get_link_counter():
    return LINK_COUNTER


def get_link_list():
    return LINKS


def add_link_to_link_list(link):
    global LINKS
    LINKS[link.link_id] = link


def delete_link(link):
    global LINKS
    del LINKS[link.link_id]


def add_link(source, destination, bandwidth=None, latency=None, link_id=None):
    if bandwidth is None:
        bandwidth = FIBER_BW
    if latency is None:
        latency = FIBER_LATENCY_PER_METER * np.sqrt((source.x - destination.x) ** 2 + (source.y - destination.y) ** 2)
    link = Link(source.entity_id, destination.entity_id, bandwidth, latency, link_id)
    NetworkTopology().G.add_edge(source.entity_id, destination.entity_id, bandwidth=bandwidth, latency=latency)
    return link


def add_bidirectional_link(source, destination, bandwidth=None, latency=None, link_id=None):
    if bandwidth is None:
        bandwidth = FIBER_BW
    if latency is None:
        latency = FIBER_LATENCY_PER_METER * np.sqrt((source.x - destination.x) ** 2 + (source.y - destination.y) ** 2)
    link = Link(source.entity_id, destination.entity_id, bandwidth, latency, link_id)
    NetworkTopology().G.add_edge(source.entity_id, destination.entity_id, bandwidth=bandwidth, latency=latency)
    reverse_link = Link(destination.entity_id, source.entity_id, bandwidth, latency, link_id)
    NetworkTopology().G.add_edge(destination.entity_id, source.entity_id, bandwidth=bandwidth, latency=latency)
    return link, reverse_link


def get_link_w_id(link_id):
    return LINKS[link_id]


def get_link(src, dst):
    for link in get_link_list().values():
        if link.source == src and link.destination == dst:
            return link
        else:
            pass

    return None


def link_does_exist(node_1, node_2):
    for link in get_link_list().values():
        if (link.source == node_1 and link.destination == node_2) or (
                link.destination == node_1 and link.source == node_2):
            return True
        else:
            pass
    return False
