# @Author: Alba Jano
# @Date: 2020-11-15
# @Email: alba.jano@tum.de
# @Last modified by: Alba Jano

import heapq


class EventChain(object):

    def __init__(self):
        self.event_list = []

    def insert(self, e):
        heapq.heappush(self.event_list, e)

    def remove_TTI_events(self, time):
        return self.event_list[time:]
        # return heapq.heappop(self.event_list)

    def delete(self):
        self.event_list = []


class SimEvent(object):

    def __init__(self, timestamp, device_ID, packet_size):
        self.packet_timestamp = timestamp
        self.packet_size = packet_size
        self.device_ID = device_ID
        self.priority = None
        self.waiting = True

    def __lt__(self, other):
        """
        Comparison is made by comparing timestamps. If time stamps are equal, priorities are compared.
        """
        if self.packet_timestamp != other.packet_timestamp:
            return self.packet_timestamp < other.packet_timestamp
        else:
            return self.packet_timestamp
        # TODO: solve the problem:     return self.priority < other.priority - Alba
        # TypeError: '<' not supported between instances of 'NoneType' and 'NoneType'
        # elif self.priority != other.priority:
        #     return self.priority < other.priority
        # else:
        #     return self.priority < other.priority
