from systemd import journal

class LogManager(object):
    @staticmethod
    def get_logger(name):
        return Logger(name)

class Logger(object):
    def __init__(self, name):
        self._name = name

    def debug(self, message):
        journal.send(message, PRIORITY=journal.LOG_DEBUG, LOGGER=self._name)

    def info(self, message):
        journal.send(message, PRIORITY=journal.LOG_INFO, LOGGER=self._name)

    def error(self, message):
        journal.send(message, PRIORITY=journal.LOG_ERR, LOGGER=self._name)

    def event(self, name, metadata):
        message = "Recording event '{0}'".format(name) #just not required but lazy to deal with `sendv` api
        journal.send(message, PRIORITY=journal.LOG_INFO, LOGGER=self._name, EVENT_NAME=name, **(Logger._format_metadata(metadata)))

    @staticmethod
    def _format_metadata(metadata):
        """
            Convert keys in kwargs to uppercase. This is journald style guide
        """
        return {key.upper(): str(value) for key,value in metadata.items()}
