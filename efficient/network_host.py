import argparse
import codecs
import signal
import sys

from io import BytesIO
from socketserver import TCPServer
from socketserver import StreamRequestHandler

from efficient import Efficient
from efficient_message_handler import EfficientJsonMessageHandler
from led_display import LedDisplay
from logmanager import LogManager
from tracker import WorkDayTracker

class EfficientNetworkMessageHandler(StreamRequestHandler):
    def __init__(self, efficient_tracker, request, client_address, server, max_data_length = 2048):
        self._efficient_handler = EfficientJsonMessageHandler(efficient_tracker)
        self._max_data_length = max_data_length

        super().__init__(request, client_address, server)

    def handle(self):
        message = self.request.recv(self._max_data_length)
        response = self._efficient_handler.handle(message)
        self._send_response(response)

    def _send_response(self, message, ending='\n'):
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
    tracker = WorkDayTracker()
    efficient = Efficient(display,tracker)
    server = EfficientServer((args.host, args.port), EfficientNetworkMessageHandler, efficient)
    log.info("Efficient server started at port {0}".format(args.port))

    server.serve_forever()