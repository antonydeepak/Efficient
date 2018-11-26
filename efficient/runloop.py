import time
from threading import Thread

class Runloop(object):
    grace_timeout_seconds = 2

    def __init__(self, delay):
        self._delay = delay.total_seconds()
        self._loop = None
        self._terminate = False

    def start(self, action, action_args):
        if self._loop:
            return

        self._loop = Thread(name='runloop', target=self._run, args=(action, action_args))
        self._loop.daemon = True
        self._loop.start()

    def wait_until_stopped(self):
        self._loop.join()

    def stop(self):
        if not self._loop:
            return

        self._terminate = True
        self._loop.join(Runloop.grace_timeout_seconds)

        self._reset()

    def _run(self, action, action_args):
        while not self._terminate:
            action(action_args)
            time.sleep(self._delay)

    def _reset(self):
        self._loop = None
        self._terminate = False
