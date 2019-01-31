from abc import ABC
from abc import abstractmethod
from calendar import timegm
from datetime import datetime
from time import localtime
from threading import RLock

from tracker_events import WorkStartEvent,WorkEndEvent,LunchStartEvent,MiniBreakStartEvent

class Tracker(ABC):
    @abstractmethod
    def handled_events(self):
        raise NotImplementedError('abstract type')

    @abstractmethod
    def handle(self):
        raise NotImplementedError('abstract type')

    @abstractmethod
    def summarize(self, dt, aggregate):
        raise NotImplementedError('abstract type')

class WorkDayTracker(Tracker):
    _handled_events = (
            WorkStartEvent,
            WorkEndEvent,
            LunchStartEvent,
            MiniBreakStartEvent)

    def __init__(self):
        self._events = {}
        self._lock = RLock()

    def handled_events(self):
        return WorkDayTracker._handled_events

    def handle(self, event):
        assert(isinstance(event, WorkDayTracker._handled_events))

        with self._lock:
            events = self._get_events_for_date(event.client_time_utc)
            events.append(event)
            events.sort(key = lambda  x: x.client_time_utc)

    def summarize(self, dt, aggregate):
        events = self._get_events_for_date(dt)
        return aggregate(events)

    def _get_events_for_date(self, dt):
        key = WorkDayTracker._get_key(dt)
        if key not in self._events:
            self._events[key] = []
        return self._events[key]

    @staticmethod
    def _get_key(dt):
        local_time = WorkDayTracker._utc_to_local(dt)
        return f"{local_time.tm_year}{local_time.tm_mon}{local_time.tm_mday}"

    @staticmethod
    def _utc_to_local(utc):
        # Idea is to convert the utc to epoch and reconvert the epoch to localtime
        epoch = timegm(utc.timetuple())
        return localtime(epoch)