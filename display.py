from collections import namedtuple
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

from journald_logging import LogManager

class DisplayFont(graphics.Font):
    def __init__(self, font_file):
        super().__init__()
        super().LoadFont(font_file)

class Color:
    Red,Green,Blue = graphics.Color(255, 0, 0), graphics.Color(0, 255, 0), graphics.Color(0, 0, 255)

class LedDisplay(object):
    defaultFont = DisplayFont("fonts/tom-thumb.bdf") 
    defaultColor = Color.Green

    def __init__(self, options):
        self._logger = LogManager.get_logger(__name__)
        self._logger.debug("Initializing display with '{0}'".format(options))

        matrix_options = RGBMatrixOptions()

        matrix_options.hardware_mapping = options.led_gpio_mapping
        matrix_options.rows = options.led_rows
        matrix_options.cols = options.led_cols
        matrix_options.chain_length = options.led_chain
        matrix_options.parallel = options.led_parallel
        matrix_options.row_address_type = options.led_row_addr_type
        matrix_options.multiplexing = options.led_multiplexing
        matrix_options.pwm_bits = options.led_pwm_bits
        matrix_options.brightness = options.led_brightness
        matrix_options.pwm_lsb_nanoseconds = options.led_pwm_lsb_nanoseconds
        matrix_options.led_rgb_sequence = options.led_rgb_sequence
        matrix_options.show_refresh_rate = options.led_show_refresh
        matrix_options.gpio_slowdown = options.led_slowdown_gpio
        matrix_options.disable_hardware_pulsing = options.led_no_hardware_pulse

        self._matrix = RGBMatrix(options = matrix_options)
        self._offscreen_canvas = self._matrix.CreateFrameCanvas()

        self._alignment = LedDisplay.Alignment(self._matrix.width, self._matrix.height)

    @property 
    def alignment(self):
        return self._alignment
        
    def write(self, message, alignment, font=defaultFont, color=defaultColor):
        self._offscreen_canvas.Clear()

        alignment = alignment(font)
        x = alignment.x
        y = alignment.y
        for c in message:
            # support for '\n'
            if c == "\n":
                x = alignment.x
                y += (font.baseline + 1) # add an extra space so that the next line doensn't hug the baseline
                continue
            x += font.DrawGlyph(self._offscreen_canvas, x, y, color, ord(c))

        self._offscreen_canvas = self._matrix.SwapOnVSync(self._offscreen_canvas)

    def clear(self):
        self._offscreen_canvas.Clear()
        self._offscreen_canvas = self._matrix.SwapOnVSync(self._offscreen_canvas)

    class Alignment(object):
        def __init__(self, canvas_width, canvas_height):
            self._width = canvas_width
            self._height = canvas_height

            self._align = namedtuple('Alignment', ['x', 'y'])

        def top_left(self, font):
            return self._align(x=0, y=font.baseline)
