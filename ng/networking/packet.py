
# a data to be sent over the network is split into 1 or more packets. once the last packet is received,
# the network interface can forward the data upstream

# L3 quant

ID = 0

class Packet:

    def __init__(self, node0, node1, size, seq_nr, is_last, data):
        global ID
        self.id = ID
        ID += 1
        self.node0 = node0
        self.node1 = node1
        self.size = size
        self.seq_nr = seq_nr
        self.is_last = is_last
        self.data = data

    def __str__(self):
        return ("P[#%s:%s->%s|seq=%s|size=%s|isLast=%s]"
                % (self.id, self.node0, self.node1, self.seq_nr, self.size, str(self.is_last)))

