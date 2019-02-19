import json
import sys

from datetime import datetime,timedelta

from efficient import EfficientException
from logmanager import LogManager
from tracker import WorkDayTracker
import tracker_events

class EfficientJsonMessageHandler(object):
    '''
    Wrapper around efficient that provides a raw Json message handler. 
    This can be used inside a host (network_host, self_host)
    '''
    def __init__(self, efficient_tracker):
        self._efficient = efficient_tracker

        self._logger = LogManager.get_logger(__name__)

    def handle(self, message):
        self._logger.debug("Handling message '{0}'".format(message))

        success,command,data = self._parse_command(message)
        if not success:
            self._logger.info("Message parsing failed with '{0}'".format(data))
            return data

        response = self._handle_command(command, data)
        return response

    def _handle_command(self, name, data):
        self._logger.debug("Handling command '{0}'".format(name))
        if name == "start":
            return self._handle_start(data['args'])
        elif name == "pause":
            return self._handle_pause()
        elif name == "resume":
            return self._handle_resume()
        elif name == "end":
            return self._handle_end()
        elif name == "event":
            return self._handle_event(data['args'])

        message = "Command '{0}' not supported".format(name) 
        self._logger.info(message)
        return message

    def _handle_start(self, args):
        '''
        Wrapper around the start() method of Efficient.
        Parses the arguments and calls the start() method
        '''

        if not args:
            message = "Command 'start' does not have any arguments"
            self._logger.debug(message)
            return message
        if 'duration' not in args:
            message = "Command 'start' does not have any 'duration' specified"
            self._logger.debug(message)
            return message

        duration = args['duration']
        hours = duration['hours']
        minutes = duration['minutes']
        seconds = duration['seconds']

        try:
            self._efficient.start(timedelta(hours=hours, minutes=minutes, seconds=seconds), lambda: self._efficient.stop())
        except EfficientException as e:
            return str(e)

        response = "Timer started for hours:{0} minutes:{1} seconds:{2}".format(hours, minutes, seconds)
        self._logger.info(response)
        return response 

    def _handle_pause(self):
        '''
        Wrapper around the pause() method of Efficient.
        Parses the arguments and calls the pause() method
        '''

        try:
            self._efficient.pause()
        except EfficientException as e:
            return str(e)

        response = "Timer paused"
        self._logger.info(response)
        return response 

    def _handle_resume(self):
        '''
        Wrapper around the resume() method of Efficient.
        Parses the arguments and calls the resume() method
        '''

        try:
            self._efficient.resume()
        except EfficientException as e:
            return str(e)

        response = "Timer resumed"
        self._logger.info(response)
        return response 

    def _handle_end(self):
        '''
        Wrapper around the stop() method of Efficient.
        Parses the arguments and calls the stop() method
        '''

        try:
            self._efficient.stop()
        except EfficientException as e:
            return str(e)

        response = "Timer ended"
        self._logger.info(response)
        return response 

    def _handle_event(self, args):
        if not args:
            message = "Command 'event' does not have any arguments"
            self._logger.debug(message)
            return message

        if 'name' not in args:
            message = "Event does not have any 'name' specified"
            self._logger.debug(message)
            return message

        name = args['name']
        metadata = args['metadata'] if ('metadata' in args) else {}
        try:
            event = self._parse_event(name, metadata)
            self._efficient.event(event)
        except Exception as e:
            return str(e)

        return "Event '{0}' logged".format(name)

    def _parse_command(self, message):
        try:
            str_message = message.decode('utf-8')
            data = json.loads(str_message)
        except json.JSONDecodeError as e:
            return (False, None, "Malformed Json passed. {0}".format(str(e)))

        if 'command' not in data:
            return (False, None, "Json not of the correct type. Missing 'command' type")

        return (True, data['command'], data)

    def _parse_event(self, name, metadata):
        tracker_events_module = sys.modules['tracker_events']
        event = getattr(tracker_events_module, name)
        return event(**metadata, server_time_utc=datetime.utcnow())