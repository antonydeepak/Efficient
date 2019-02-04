from datetime import datetime,timedelta
from itertools import islice
from threading import RLock

from countdown_timer import CountdownTimer
from runloop import Runloop
from tracker_events import *

class Efficient(object):
    def __init__(self, display, tracker):
        self._display = display
        self._tracker = tracker

        self._lock = RLock()
        self._timer = None
        self._runloop = None

    def start(self, duration, elapsed):
        if self._timer:
            raise EfficientException("Timer already running. Stop this timer before starting a new one")

        with self._lock:
            self._timer = CountdownTimer(duration, elapsed)
            self._timer.start()

            self._runloop = Runloop(delay=timedelta(hours=0, minutes=0, seconds=1))
            self._runloop.start(action=self._update, action_args=(self._display, self._timer, self._tracker))

            return self._runloop

    def pause(self):
        if not self._timer:
            raise EfficientException("Timer not started")

        with self._lock:
            self._timer.stop()

    def resume(self):
        if not self._timer:
            raise EfficientException("Timer not started")

        with self._lock:
            self._timer.start()

    def end(self):
        with self._lock:
            self._runloop.stop()
            self._timer.reset()
            self._display.clear()

            self._runloop = None
            self._timer = None
        
    def _update(self, args):
        display = args[0]
        timer = args[1]
        tracker = args[2]

        hours,minutes,seconds = Efficient._parse(timer.remaining)
        message = '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)

        event_durations = tracker.summarize(datetime.now(), aggregate=Efficient._aggregate)
        event_durations = Efficient._pretty_format(event_durations)
        top_2_event_durations = islice(sorted(event_durations, key=lambda x: x[1], reverse=True), 2)
        for event_duration in top_2_event_durations:
            ev,du = event_duration
            message += '\n{0} {1:02}'.format(ev, du)

        display.write(message)

    @staticmethod
    def _aggregate(events):
        range_events = (event for event in events if isinstance(event, RangeEvent))
        start_events = {}
        event_durations = {}

        for event in range_events:
            if isinstance(event, event.start_event_type):
                start_events[event.start_event_type] = event
            if start_events.get(event.start_event_type) and isinstance(event, event.end_event_type):
                range_event = Efficient._base_range_event(event.end_event_type)
                end_event = event
                duration = event_durations.get(range_event) if event_durations.get(range_event) else timedelta()
                duration += end_event.client_time_utc - start_events[event.start_event_type].client_time_utc
                event_durations[range_event] = duration
                del(start_events[event.start_event_type])
        # If start event does not have an end event compute duration with datetime.utcnow() as it might an ongoin event
        for start_event in start_events:
            range_event = Efficient._base_range_event(start_event)
            duration = event_durations.get(range_event) if event_durations.get(range_event) else timedelta()
            duration += datetime.utcnow() - start_events[start_event].client_time_utc
            event_durations[range_event] = duration

        return event_durations

    @staticmethod
    def _base_range_event(event):
        return event.__bases__[0]

    @staticmethod
    def _pretty_format(event_durations):
        # send it back as a iterable of kv pairs.
        for event in event_durations:
            d,h,m,s = Efficient._days_hours_minutes_seconds(event_durations[event])
            duration = d or h or m or s
            yield (event.__name__[:2], duration)

    @staticmethod
    def _days_hours_minutes_seconds(td):
        return td.days, td.seconds//3600, (td.seconds//60)%60, (td.seconds)%60

    @staticmethod
    def _parse(timedelta):
        hours, remainder = divmod(timedelta.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        return (int(hours), int(minutes), int(seconds))

class EfficientException(Exception):
    def __init__(self, message):
        self._message = message
