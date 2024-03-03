
class Computation:

    def __init__(self, cycles):
        self.cycles = cycles
        self.remaining_cycles = cycles

    def __str__(self):
        return "C[cycles=%d]" % self.cycles