from systemd import journal

class JournaldLogger(object):
    def __init__(self, name, journald_message_id):
        self._name = name
        self._journald_message_id = journald_message_id

    def debug(self, message):
        journal.send(message, PRIORITY=journal.LOG_DEBUG, MESSAGE_ID=self._journald_message_id, LOGGER=self._name)

    def info(self, message):
        journal.send(message, PRIORITY=journal.LOG_INFO, MESSAGE_ID=self._journald_message_id, LOGGER=self._name)

    def error(self, message):
        journal.send(message, PRIORITY=journal.LOG_ERR, MESSAGE_ID=self._journald_message_id, LOGGER=self._name)

    def event(self, event):
        message = f"Event '{event.name}'" #just not required but lazy to deal with `sendv` api which doesn't need message
        journal.send(
            message,
            PRIORITY=journal.LOG_INFO,
            MESSAGE_ID=self._journald_message_id,
            LOGGER=self._name,
            **(JournaldLogger._format_metadata(event.__dict__)))

    @staticmethod
    def _format_metadata(metadata):
        """
            Convert keys in kwargs to uppercase. This is journald style guide
        """
        return {key.upper(): str(value) for key,value in metadata.items()}
