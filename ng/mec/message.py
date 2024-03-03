ID = 0

class Message:

    # sender, destination are service names
    # the mapping to a physical node will be determined through orchestration / load-balancing

    def __init__(self, sender, destination, size, data):
        global ID
        self.id = ID
        ID += 1
        self.sender = sender
        self.destination = destination
        self.data = data
        self.size = size

    def __str__(self):
        return "M[#%s:%s->%s|size=%s]" % (self.id, self.sender, self.destination, self.size)