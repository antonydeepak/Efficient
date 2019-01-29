import signal
from datetime import timedelta
from sys import exit

from efficient import Efficient
from console_display import ConsoleDisplay

def terminate(signum, frame):
    if runloop:
        runloop.stop()
    exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, terminate)

    display = ConsoleDisplay()
    efficient = Efficient(display)
    runloop = efficient.start(timedelta(hours=8, minutes=0, seconds=0), lambda: efficient.end())
    print('Runloop started')
    runloop.wait_until_stopped()
    print('Runloop ended')
