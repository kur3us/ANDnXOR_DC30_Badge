import chomper_app as app
import framebuf
import micropython
from micropython import const
import time
import font_digital32 as dfont

WIDTH = const(240)
HEIGHT = const(240)
MARGIN = const(4)

# Made using RGB565 color picker: http://www.barth-dev.de/online/rgb565-color-picker/
BLACK = const(0x0000)
BLUE = const(0x001F)
BROWN = const(0x8200)
DARK_BLUE = const(0x0014)
DARK_GRAY = const(0x8410)
DARK_GREEN = const(0x0400)
DARK_RED = const(0x8000)
RED = const(0xF800)
LIGHT_GRAY = const(0xC618)
GREEN = const(0x07E0)
CYAN = const(0x07FF)
MAGENTA = const(0xF81F)
ORANGE = const(0xFC00)
PINK = const(0xF81F)
PURPLE = const(0x801F)
YELLOW = const(0xFFE0)
WHITE = const(0xFFFF)
INDIGO = const(0x61D3)
HOTPINK = const(0xF88C)
PEACH = const(0XFCAA)

# Buffer for smooth graphix
__BUFFER = bytearray(WIDTH*HEIGHT*2)
__fbuf = framebuf.FrameBuffer(__BUFFER, WIDTH, HEIGHT, framebuf.RGB565)

# Look up table to convert colors from 8-bit to 16-bit RGB
__COLOR_CONVERSION_LUT = [0, 10, 21, 31, 288, 298, 309, 319, 576, 586, 597, 607, 864, 874, 885, 895, 1152, 1162, 1173, 1183, 1440, 1450, 1461, 1471, 1728, 1738, 1749, 1759, 2016, 2026, 2037, 2047, 8192, 8202, 8213, 8223, 8480, 8490, 8501, 8511, 8768, 8778, 8789, 8799, 9056, 9066, 9077, 9087, 9344, 9354, 9365, 9375, 9632, 9642, 9653, 9663, 9920, 9930, 9941, 9951, 10208, 10218, 10229, 10239, 18432, 18442, 18453, 18463, 18720, 18730, 18741, 18751, 19008, 19018, 19029, 19039, 19296, 19306, 19317, 19327, 19584, 19594, 19605, 19615, 19872, 19882, 19893, 19903, 20160, 20170, 20181, 20191, 20448, 20458, 20469, 20479, 26624, 26634, 26645, 26655, 26912, 26922, 26933, 26943, 27200, 27210, 27221, 27231, 27488, 27498, 27509, 27519, 27776, 27786, 27797, 27807, 28064, 28074, 28085, 28095, 28352, 28362, 28373, 28383, 28640, 28650, 28661, 28671, 36864, 36874, 36885, 36895,
                          37152, 37162, 37173, 37183, 37440, 37450, 37461, 37471, 37728, 37738, 37749, 37759, 38016, 38026, 38037, 38047, 38304, 38314, 38325, 38335, 38592, 38602, 38613, 38623, 38880, 38890, 38901, 38911, 45056, 45066, 45077, 45087, 45344, 45354, 45365, 45375, 45632, 45642, 45653, 45663, 45920, 45930, 45941, 45951, 46208, 46218, 46229, 46239, 46496, 46506, 46517, 46527, 46784, 46794, 46805, 46815, 47072, 47082, 47093, 47103, 55296, 55306, 55317, 55327, 55584, 55594, 55605, 55615, 55872, 55882, 55893, 55903, 56160, 56170, 56181, 56191, 56448, 56458, 56469, 56479, 56736, 56746, 56757, 56767, 57024, 57034, 57045, 57055, 57312, 57322, 57333, 57343, 63488, 63498, 63509, 63519, 63776, 63786, 63797, 63807, 64064, 64074, 64085, 64095, 64352, 64362, 64373, 64383, 64640, 64650, 64661, 64671, 64928, 64938, 64949, 64959, 65216, 65226, 65237, 65247, 65504, 65514, 65525, 65535]

# Helper function to get the color of a pixel from compressed font bitmap


def pixel(x, y, color):
    c = (color & 0xFF) << 8 | (color & 0xFF00) >> 8
    __fbuf.pixel(x, y, c)


def fill_rect(x, y, w, h, color):
    c = (color & 0xFF) << 8 | (color & 0xFF00) >> 8
    __fbuf.fill_rect(x, y, w, h, c)


def line(x0, y0, x1, y1, color):
    c = (color & 0xFF) << 8 | (color & 0xFF00) >> 8
    __fbuf.line(x0, y0, x1, y1, c)


def rect(x, y, w, h, color):
    c = (color & 0xFF) << 8 | (color & 0xFF00) >> 8
    __fbuf.rect(x, y, w, h, c)


def rect_unbuffered(watch, x, y, w, h, color):
    watch.display.line(x, y, x+w, y, color)
    watch.display.line(x, y+h, x+w, y+h, color)
    watch.display.line(x, y, x, y+h, color)
    watch.display.line(x+w, y, x+w, y+h, color)


def blinds_right_unbuffered(watch):
    # Indicate to user of swipe direction
    for x in range(0, WIDTH, 2):
        watch.display.vline(x, 0, HEIGHT, INDIGO)
    for x in range(1, WIDTH, 2):
        watch.display.vline(x, 0, HEIGHT, INDIGO)


def blinds_left_unbuffered(watch):
    # Indicate to user of swipe direction
    for x in range(WIDTH, 0-1, -2):
        watch.display.vline(x, 0, HEIGHT, INDIGO)
    for x in range(WIDTH-1, 0-1, -2):
        watch.display.vline(x, 0, HEIGHT, INDIGO)


def blinds_up_unbuffered(watch):
    # Indicate to user of swipe direction
    for y in range(HEIGHT, 0-1, -2):
        watch.display.hline(0, y, WIDTH, PEACH)
    for y in range(HEIGHT-1, 0-1, -2):
        watch.display.hline(0, y, WIDTH, INDIGO)


def blinds_down_unbuffered(watch):
    # Indicate to user of swipe direction
    for y in range(0, HEIGHT, 2):
        watch.display.hline(0, y, WIDTH, PEACH)
    for y in range(1, HEIGHT, 2):
        watch.display.hline(0, y, WIDTH, INDIGO)


def text(font, text, x, y, fg=WHITE, transparent=True, bg=BLACK):
    print_width = 0

    for chr in text:
        char_index = 0
        try:
            char_index = font.MAP.index(chr)
        except ValueError:
            break

        char_width = font._WIDTHS[char_index]
        char_height = font.HEIGHT
        offset_width = font.OFFSET_WIDTH

        bs_bit = 0

        if offset_width == 1:
            bs_bit = font._OFFSETS[char_index * offset_width]
        elif offset_width == 2:
            bs_bit = (font._OFFSETS[char_index * offset_width] <<
                      8) + (font._OFFSETS[char_index * offset_width + 1])
        elif offset_width == 3:
            bs_bit = (font._OFFSETS[char_index * offset_width] << 16) + (
                font._OFFSETS[char_index * offset_width + 1] << 8) + (font._OFFSETS[char_index * offset_width + 2])

        for yy in range(0, char_height):
            for xx in range(0, char_width):
                xxx = x + xx
                yyy = y + yy
                if xxx >= WIDTH:
                    break
                if yyy >= HEIGHT:
                    break

                color = 0
                for i in range(0, font.BPP):
                    color <<= 1
                    color |= (font._BITMAPS[int(bs_bit / 8)]
                              & 1 << (7 - (bs_bit % 8))) > 0
                    bs_bit += 1
                if color:
                    pixel(xxx, yyy, fg)
                elif not transparent:
                    fill_rect(xxx, yyy, 1, 1, bg)

        print_width += char_width
        x += char_width  # advance x axis

    return print_width

# Get the width in pixels of a string of text


def text_width(font, text):
    print_width = 0
    map = font.MAP

    for chr in text:
        idx = map.index(chr)
        print_width += font._WIDTHS[idx]
    return print_width


def push(watch):
    start_time = time.ticks_ms()
    watch.display.blit_buffer(__BUFFER, 0, 0, WIDTH, HEIGHT)
    end_time = time.ticks_ms()
    draw_time = end_time - start_time


class UIButton():
    def __init__(self, watch, x, y, text='button', cb=None):
        self._watch = watch
        self._text = text
        self._cb = cb
        self._width = text_width(dfont, text) + (MARGIN * 2)
        self._height = dfont.HEIGHT + (MARGIN * 2)
        self._x = x
        self._y = y
        self._fg = WHITE
        self._bg = HOTPINK

    def draw(self):
        x0 = self._x
        x1 = self._x + self._width
        y0 = self._y
        y1 = self._y + self._height
        fill_rect(x0, y0, self._width, self._height, self._bg)
        line(x0, y0, x1, y0, self._fg)
        line(x1, y0, x1, y1, self._fg)
        line(x0, y0, x0, y1, self._fg)
        line(x0, y1, x1, y1, self._fg)
        text(dfont, self._text, self._x + MARGIN,
             self._y + MARGIN, self._fg, self._bg)
        rect(self._x, self._y, self._width, self._height, INDIGO)

    def handle_touch(self, x, y):
        if (self._x - 2 <= x <= self._x + self._width + 2) \
                and (self._y - 2 <= y <= self._y + self._height + 2):
            rect_unbuffered(self._watch, self._x - 1, self._y - 1,
                            self._width + 2, self._height + 2, YELLOW)
            rect_unbuffered(self._watch, self._x, self._y,
                            self._width, self._height, YELLOW)
            return True
        return False


class UILabel():
    def __init__(self, watch, font, x, y, text='Label', color=WHITE):
        self._watch = watch
        self._font = font
        self._x = x
        self._y = y
        self._text = text
        self._color = color

    def draw(self):
        text(self._font, self._text, self._x, self._y, self._color)

    def fill_bg(self, color=BLACK):
        fill_rect(self._x, self._y, self.width(), self.height(), color)

    def height(self):
        return self._font.HEIGHT

    def width(self):
        return text_width(self._font, self._text)


class UITextbox():
    def __init__(self, watch, font, x, y, w, h, text='Textbox', color=WHITE, bg_color=BLACK):
        self._watch = watch
        self._font = font
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._text = text
        self._color = color
        self._bg_color = bg_color

    def draw(self):
        max_lines = int(self._h / self._font.HEIGHT)
        # Get last n lines that are displayable
        lines = self._text.split('\n')[-max_lines:]
        y = self._y
        for line in lines:
            text(self._font, line, self._x, y, self._color, self._bg_color)
            y += self._font.HEIGHT

    def fill_bg(self, color=BLACK):
        fill_rect(
            self._x, self._y, self.width(), self.height(), color)

    def height(self):
        return self._font.HEIGHT

    def width(self):
        return text_width(self._font, self._text)

    def text(self, text):
        self._text = text

    def append(self, text):
        self._text = self._text + "\n" + text


def draw_text_center(watch, font, s, row, color=WHITE):
    screen = WIDTH                    # get screen width
    # get the width of the string
    width = text_width(font, s)
    if width and width < screen:             # if the string < display
        col = WIDTH // 2 - width // 2  # find the column to center
    else:                                    # otherwise
        col = 0                              # left justify

    text(font, s, col, row, color)      # and write the string

def fill(color=BLACK):
    fill_rect(app.APP_LEFT, app.APP_TOP, app.APP_WIDTH, app.APP_HEIGHT, color)


def fill_rgb(file):
    draw_rgb(file, app.APP_LEFT, app.APP_TOP, app.APP_WIDTH, app.APP_HEIGHT)


def color565(r, g, b):
    """
    Convert discrete red/green/blue values to RGB565 (16-bit) color suitable for our watch
    """
    rgb = 0x0000
    rgb |= (r & 0xF8) << 8
    rgb |= (g & 0xFC) << 3
    rgb |= (b & 0xF8) >> 3
    return rgb


def draw_rgb(file, x, y, w, h):
    # Ensure coords are within range
    while y < 0:
        y += 240
    while y >= 240:
        y -= 240
    while x < 0:
        x += 240
    while x >= 240:
        x -= 240

    try:
        f = open(file, "rb")

        if x == 0 and w == WIDTH:
            o = ((y * WIDTH) + x) * 2
            view = memoryview(__BUFFER)
            f.readinto(view[o:o+(w*h*2)])
        else:
            for yy in range(y,y+h):
                o = ((yy * WIDTH) + x) * 2
                __BUFFER[o:(o+w*2)] = f.read(w*2)
        f.close()       
    except Exception as e:
        print("UI: Unable to draw", file, e)
        fill_rect(x, y, w, h, RED)


def draw_rgb_mv(b, x, y, w, h):
    """
    Draw an RGB file to the framebuffer from a given memoryview
    """

    # Ensure coords are within range
    while y < 0:
        y += 240
    while y >= 240:
        y -= 240
    if x < 0:
        x += 240
    if x >= 240:
        x -= 240

    if x == 0 and w == WIDTH:
        offset = (y * WIDTH) * 2
        __BUFFER[offset:offset+(h*w)*2] = b[:(h*w)*2]
    else:
        i = 0
        for yy in range(y, y+h):
            offset = ((yy * WIDTH) + x) * 2
            __BUFFER[offset:(offset+w)*2] = b[i:(i+w)*2]
            i += (w*2)
            offset += (w*2)


def draw_rgb8(file, x, y, w, h):
    # Ensure coords are within range
    while y < 0:
        y += 240
    while y >= 240:
        y -= 240
    while x < 0:
        x += 240
    while x >= 240:
        x -= 240

    try:
        f = open(file, "rb")
        ba = bytearray(w*h)
        f.readinto(ba)

        # Similar as above but only 8 bits per pixel
        i = 0
        for yy in range(y, y+h):
            o = ((yy * WIDTH) + x) * 2
            for xx in range(x, x+w):
                rgb = __COLOR_CONVERSION_LUT[ba[i]]
                __BUFFER[o] = (rgb & 0xFF00) >> 8
                __BUFFER[o+1] = rgb & 0xFF

                i += 1
                o += 2

        f.close()
    except Exception as e:
        print("UI: Unable to draw RGB8", file, e)
        fill_rect(x, y, w, h, YELLOW)