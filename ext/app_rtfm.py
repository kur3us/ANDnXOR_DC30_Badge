from micropython import const
import ui
import ui_touch
  
from ui import *

CLASSNAME = "RTFMApp"

STATE_STOPPED = const(0x00)
STATE_PLAYING = const(0x01)
STATE_PAUSED = const(0x02)

class RTFMApp():
    APP_NAME = "RTFM"
    WEIGHT = 30

    def _cb(self):
        # Manually handle touch, interrupt bling if any event occurs
        touch = self.watch.touch.do_work()
        if touch[0] > ui_touch.GESTURE_NONE:
            self._state = STATE_STOPPED
            self._valid = False
            return 1
        return 0

    def __init__(self, _watch):
        self.watch = _watch
        self._btn = UIButton(self.watch, 53, 187, text="   R.T.F.M.   ")
        self._btn._bg = ui.INDIGO
        self._btn._fg = ui.PEACH
        self._valid = False

    def _redraw(self):
        ui.fill_rgb("/bg_rtfm.rgb")
        self._btn.draw()
        ui.push(self.watch) # Push chrome before we draw directly to the screen
        self._valid = True
    
    def init(self):
        self._valid = False
        self._stop = False
        self._state = STATE_STOPPED
    
    def foreground(self):
        if not self._valid:
            self._redraw()

        while self._state == STATE_PLAYING:
            self.watch.display.play_rgb("/qr_rtfm.rgb", 0, 0, 240, 240, self._cb)
            self.watch.defer_sleep() # make sure screen stays off a bit after player stops
        
    def touch(self, x, y):
        if self._btn.handle_touch(x,y):
            self._state = STATE_PLAYING
