
# L2 quant

class Frame:

    def __init__(self, if0, if1, size, seq_nr, is_last, data):
        self.if0 = if0
        self.if1 = if1
        self.size = size
        self.seq_nr = seq_nr
        self.is_last = is_last
        self.data = data