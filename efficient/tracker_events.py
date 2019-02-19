from abc import ABC
from abc import abstractmethod
from datetime import timedelta

class IEndEventCreator(ABC):
    @abstractmethod
    def create_end_event(self):
        raise NotImplementedError('abstract type')

class Event(object):
    def __init__(self, name, client_time_utc, server_time_utc):
        self.name = name
        self.client_time_utc = client_time_utc
        self.server_time_utc = server_time_utc

class RangeEvent(Event):
    def __init__(self, name, client_time_utc, server_time_utc, start_event_type, end_event_type):
        super().__init__(name, client_time_utc, server_time_utc)
        self.start_event_type = start_event_type
        self.end_event_type = end_event_type

class AutoExpiringRangeEvent(RangeEvent):
    def __init__(self, name, client_time_utc, server_time_utc, start_event_type, end_event_type, expiry):
        super().__init__(name, client_time_utc, server_time_utc, start_event_type, end_event_type)
        self.expiry = expiry

class WorkEvent(RangeEvent):
    def __init__(self, name, client_time_utc, server_time_utc):
        super().__init__(name, client_time_utc, server_time_utc, WorkStartEvent, WorkEndEvent)

class WorkStartEvent(WorkEvent):
    def __init__(self, client_time_utc, server_time_utc):
        super().__init__("start", client_time_utc, server_time_utc)

class WorkEndEvent(WorkEvent):
    def __init__(self, client_time_utc, server_time_utc):
        super().__init__("end", client_time_utc, server_time_utc)

class LunchEvent(AutoExpiringRangeEvent):
    def __init__(self, name, client_time_utc, server_time_utc):
        super().__init__(name, client_time_utc, server_time_utc, LunchStartEvent, LunchEndEvent, timedelta(minutes=45))

class LunchStartEvent(LunchEvent, IEndEventCreator):
    def __init__(self, client_time_utc, server_time_utc):
        super().__init__("start", client_time_utc, server_time_utc)

    def create_end_event(self):
        return LunchEndEvent(self.client_time_utc, self.server_time_utc)

class LunchEndEvent(LunchEvent):
    def __init__(self, client_time_utc, server_time_utc):
        super().__init__("end", client_time_utc, server_time_utc)

class MiniBreakEvent(AutoExpiringRangeEvent):
    def __init__(self, name, client_time_utc, server_time_utc):
        super().__init__(name, client_time_utc, server_time_utc, MiniBreakStartEvent, MiniBreakEndEvent, timedelta(minutes=15))

class MiniBreakStartEvent(MiniBreakEvent, IEndEventCreator):
    def __init__(self, client_time_utc, server_time_utc):
        super().__init__("start", client_time_utc, server_time_utc)

    def create_end_event(self):
        return MiniBreakEndEvent(self.client_time_utc, self.server_time_utc)

class MiniBreakEndEvent(MiniBreakEvent):
    def __init__(self, client_time_utc, server_time_utc):
        super().__init__("end", client_time_utc, server_time_utc)

