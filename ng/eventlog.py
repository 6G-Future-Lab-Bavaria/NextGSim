from simpy import Environment
from typing import List, Optional


# every component should have their own event types that inherit from this class and handle serialization
class Event:

    def __init__(self, time, component_meta, type, data: Optional[str]):
        self.time = time
        self.component_meta = component_meta
        self.type = type
        self.data = data

    def serialize(self):
        return {
            "time": self.time,
            "component": self.component_meta,
            "type": self.type,
            "data": self.data
        }

    @staticmethod
    def deserialize(obj):
        return Event(
            obj["time"],
            obj["component"],
            obj["type"],
            obj["data"]
        )

class EventLog:

    def __init__(self, env: Environment):
        self.env = env
        self.events: List[Event] = []

    def register_event(self, component, typ, data: Optional[str] = None):
        component_meta = {
            "_type": type(component).__qualname__,
            "name": type(component).__name__,
            "ref": component.__repr__(),
        }
        self.events.append(Event(self.env.now, component_meta, typ, data))
