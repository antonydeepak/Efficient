from datetime import datetime
from datetime import timedelta
from threading import Timer

class CountdownTimer(object):
    ZeroDelta = timedelta(0)
    def __init__(self, duration, on_elapsed):
        self._duration = duration
        self._on_elapsed = on_elapsed

        self._remaining = self._duration
        self._start_time = None
        self._end_timer = None

    @property
    def remaining(self):
        if not self._is_running():
            return self._remaining

        elapsed = datetime.utcnow() - self._start_time
        return (self._remaining - elapsed) if (self._remaining > elapsed) else CountdownTimer.ZeroDelta

    def start(self):
        if self._is_running():
            raise CountdownTimerException("Already running")
        if self._remaining == CountdownTimer.ZeroDelta:
            raise CountdownTimerException("Timer has elapsed")

        self._start_time = datetime.utcnow()
        self._end_timer = Timer(self._remaining.total_seconds(), self._elapsed)
        self._end_timer.daemon = True
        self._end_timer.start()

    def stop(self):
        if (not self._is_running()) or (self._remaining == CountdownTimer.ZeroDelta):
            return

        elapsed = datetime.utcnow() - self._start_time
        self._remaining = (self._remaining - elapsed) if (self._remaining > elapsed) else CountdownTimer.ZeroDelta

        self._reset_time()

    def reset(self):
        self._remaining = self._duration
        self._reset_time()

    def _is_running(self):
        return self._start_time != None

    def _elapsed(self):
        self._remaining = CountdownTimer.ZeroDelta
        self._reset_time()

        if self._on_elapsed:
            self._on_elapsed()

    def _reset_time(self):
        self._start_time = None
        if self._end_timer:
            self._end_timer.cancel()
        self._end_timer = None

class CountdownTimerException(Exception):
    def __init__(self, message):
        self._message = message
