import argparse
import codecs
import json
import signal
import sys

from datetime import timedelta
from io import BytesIO
from socketserver import TCPServer
from socketserver import StreamRequestHandler

from efficient import Efficient,EfficientException
from journald_logging import LogManager
from led_display import LedDisplay
from tracker import WorkDayTracker

class EfficientHandler(StreamRequestHandler):
    def __init__(self, efficient_tracker, request, client_address, server, max_data_length = 2048):
        self._efficient = efficient_tracker
        self._max_data_length = max_data_length

        self._logger = LogManager.get_logger(__name__)

        super().__init__(request, client_address, server)

    def handle(self):
        message = self.request.recv(self._max_data_length)
        self._logger.debug("Handling message '{0}'".format(message))

        success,command,data = self._parse_command(message)
        if not success:
            self._logger.info("Message parsing failed with '{0}'".format(data))
            self._send_message(data)
            return

        response = self._handle_command(command, data)
        self._send_message(response)

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
        try:
            self._efficient.pause()
        except EfficientException as e:
            return str(e)

        response = "Timer paused"
        self._logger.info(response)
        return response 

    def _handle_resume(self):
        try:
            self._efficient.resume()
        except EfficientException as e:
            return str(e)

        response = "Timer resumed"
        self._logger.info(response)
        return response 

    def _handle_end(self):
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
        self._logger.event(name, metadata)

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

    def _send_message(self, message, ending='\n'):
        message_to_send = message + ending
        message_bytes = message_to_send.encode('utf-8')
        self.wfile.write(message_bytes)

class EfficientServer(TCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass, efficient_tracker):
        self._efficient_tracker = efficient_tracker

        super().__init__(server_address, RequestHandlerClass)

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(self._efficient_tracker, request, client_address, self)

def terminate(signum, frame):
    if server:
        server.server_close()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, terminate)

    log = LogManager.get_logger('global')

    parser = argparse.ArgumentParser()
    # Server args
    parser.add_argument("--host", action="store", help="Host interface", default='', type=str)
    parser.add_argument("--port", action="store", help="Host port", default=8080, type=int)
    # Display args
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
    args = parser.parse_args()

    display = LedDisplay(args)
    tracker = WorkDayTracker() # TODO: have to add the proper tracker
    efficient = Efficient(display,tracker)
    server = EfficientServer((args.host, args.port), EfficientHandler, efficient)
    log.info("Efficient server started at port {0}".format(args.port))

    server.serve_forever()