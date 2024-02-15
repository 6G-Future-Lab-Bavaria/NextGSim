
class Message:

    # sender, destination are services. the mapping to a physical node will be determined through orchestration

    def __init__(self, sender, destination, size, data):
        self.sender = sender
        self.destination = destination
        self.data = data
        self.size = size
