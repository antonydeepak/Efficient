from datetime import timedelta
from threading import RLock

from countdown_timer import CountdownTimer
from runloop import Runloop

class Efficient(object):
    def __init__(self, display):
        self._display = display
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
            self._runloop.start(action=self._update, action_args=(self._display, self._timer))

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

        hours,minutes,seconds = Efficient._parse(timer.remaining)
        alignment = display.alignment.top_left
        display.write('{:02}:{:02}:{:02}'.format(hours, minutes, seconds), alignment)

    @staticmethod
    def _parse(timedelta):
        hours, remainder = divmod(timedelta.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)

        return (int(hours), int(minutes), int(seconds))

class EfficientException(Exception):
    def __init__(self, message):
        self._message = message
