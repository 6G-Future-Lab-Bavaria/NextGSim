
# a data to be sent over the network is split into 1 or more packets. once the last packet is received,
# the network interface can forward the data upstream

# L3 quant

class Packet:

    def __init__(self, node0, node1, size, seq_nr, is_last, data):
        self.node0 = node0
        self.node1 = node1
        self.size = size
        self.seq_nr = seq_nr
        self.is_last = is_last
        self.data = data
