import signal
from datetime import datetime, timedelta
from sys import exit

from efficient import Efficient
from console_display import ConsoleDisplay
from tracker import WorkDayTracker
from tracker_events import *

def terminate(signum, frame):
    efficient.stop()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, terminate)

    display = ConsoleDisplay()

    # Sample test data
    ws = WorkStartEvent(datetime.utcnow()-timedelta(hours=5), datetime.utcnow()-timedelta(hours=5))
    ls = LunchStartEvent(datetime.utcnow()-timedelta(hours=2), datetime.utcnow()-timedelta(hours=2))
    bs = MiniBreakStartEvent(datetime.utcnow()-timedelta(hours=1), datetime.utcnow()-timedelta(hours=1))
    tracker = WorkDayTracker()
    tracker.handle(ws)
    tracker.handle(ls)
    tracker.handle(bs)

    efficient = Efficient(display, tracker)
    efficient.start(timedelta(hours=8, minutes=0, seconds=0), lambda: efficient.stop())
    print('Runloop started')
    efficient.wait_until_stopped()
