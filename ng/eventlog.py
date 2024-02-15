from simpy import Environment
from typing import List

# every component should have their own event types that inherit from this class and handle serialization
class Event:

    def __init__(self, time, component, type, data):
        self.time = time
        self.component = component
        self.type = type
        self.data = data

    def serialize(self):
        return {
            "time": self.time,
            "component": {
                "name": type(self.component).__name__,
                "ref": self.component.__repr__(),
            },
            "type": self.type,
            "data": str(self.data)
        }

class EventLog:

    def __init__(self, env: Environment):
        self.env = env
        self.events: List[Event] = []

    def register_event(self, component, type, data):
        self.events.append(Event(self.env.now, component, type, data))