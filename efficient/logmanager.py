from journald_logging import JournaldLogger
from journald_event_listener import JournaldEventListener

class LogManager(object):
    JournaldMessageId = "6bfacfdf569b4ea9936e109f1e21bb97"

    @staticmethod
    def get_logger(name):
        return JournaldLogger(name, LogManager.JournaldMessageId)
    
    @staticmethod
    def get_eventlistener(tracker):
        return JournaldEventListener(tracker, LogManager.JournaldMessageId)
