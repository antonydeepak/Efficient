import signal
import sys
from datetime import timedelta
from threading import RLock

import argparse

from countdown_timer import CountdownTimer
from display import LedDisplay
from runloop import Runloop

class Efficient(object):
    def __init__(self, display_args):
        self._display = LedDisplay(display_args)
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

def terminate(signum, frame):
    if runloop:
        runloop.stop()
    sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--led-rows", action="store", help="Display rows. 16 for 16x32, 32 for 32x32. Default: 32", default=32, type=int)
    parser.add_argument("--led-cols", action="store", help="Panel columns. Typically 32 or 64. (Default: 32)", default=32, type=int)
    parser.add_argument("-c", "--led-chain", action="store", help="Daisy-chained boards. Default: 1.", default=1, type=int)
    parser.add_argument("-P", "--led-parallel", action="store", help="For Plus-models or RPi2: parallel chains. 1..3. Default: 1", default=1, type=int)
    parser.add_argument("-p", "--led-pwm-bits", action="store", help="Bits used for PWM. Something between 1..11. Default: 11", default=11, type=int)
    parser.add_argument("-b", "--led-brightness", action="store", help="Sets brightness level. Default: 100. Range: 1..100", default=100, type=int)
    parser.add_argument("-m", "--led-gpio-mapping", help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm", default='adafruit-hat-pwm', choices=['regular', 'adafruit-hat', 'adafruit-hat-pwm'], type=str)
    parser.add_argument("--led-scan-mode", action="store", help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)", default=1, choices=range(2), type=int)
    parser.add_argument("--led-pwm-lsb-nanoseconds", action="store", help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130", default=130, type=int)
    parser.add_argument("--led-show-refresh", action="store_true", help="Shows the current refresh rate of the LED panel", default=0)
    parser.add_argument("--led-slowdown-gpio", action="store", help="Slow down writing to GPIO. Range: 1..100. Default: 1", default=1, choices=range(3), type=int)
    parser.add_argument("--led-no-hardware-pulse", action="store", help="Don't use hardware pin-pulse generation. Default: True", default=False, type=bool)
    parser.add_argument("--led-rgb-sequence", action="store", help="Switch if your matrix has led colors swapped. Default: RGB", default="RGB", type=str)
    parser.add_argument("--led-row-addr-type", action="store", help="0 = default; 1=AB-addressed panels", default=0, type=int, choices=[0,1])
    parser.add_argument("--led-multiplexing", action="store", help="Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral (Default: 0)", default=0, type=int, choices=[0,1,2,3])

    signal.signal(signal.SIGINT, terminate)

    args = parser.parse_args()
    e = Efficient(args)
    runloop = e.start(timedelta(hours=8, minutes=0, seconds=0), lambda: e.end())
    runloop.wait_until_stopped()
    print('runloop ended')
