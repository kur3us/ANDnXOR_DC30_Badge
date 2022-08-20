import chomper_app as app
import font_digital32 as large_font
from micropython import const
import os
import ui
import ui_touch
  
from ui import *

CLASSNAME = "BlingApp"

STATE_STOPPED = const(0x00)
STATE_PLAYING = const(0x01)
STATE_PAUSED = const(0x02)

class BlingApp():
    APP_NAME = "Bling Player"
    WEIGHT = 45

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
        self._valid = False
        self._index = 0
        self._bling_files = []
        self._lbl_file = UILabel(self.watch, large_font, 32, app.APP_TOP + 6, ui.WHITE)
        self._lbl_file._color = HOTPINK

        file_list = os.listdir()
        for file_name in file_list:
            if file_name.endswith('.rgb') and file_name.startswith('bling_'):
                name = file_name[:-4] # Remove the .rgb
                print("BLING: Found Bling", file_name)
                self._bling_files.append(file_name)

    def _redraw(self):
        if len(self._bling_files) == 0:
            self._lbl_file._text = "=("
        else:
            self._lbl_file._text = self._bling_files[self._index][6:-4]
            ui.fill_rgb("/bg_bling.rgb")
        
        x_anchor = 60
        y_anchor = 65

        ui.draw_rgb8(self._bling_files[self._index], x_anchor, y_anchor, 120, 120)
        
        # Draw a border
        ui.rect(x_anchor-2, y_anchor-2, 122, 122, ui.HOTPINK)
        
        self._lbl_file.draw()

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
            self.watch.display.play_rgb(self._bling_files[self._index], 0, 0, 240, 240, self._cb)
            self.watch.defer_sleep() # make sure screen stays off a bit after player stops
        
    def touch(self, x, y):
        if len(self._bling_files) > 0:
            if x > 80 and x < 160 and y > 80 and y < 160:
                if self._state == STATE_STOPPED or self._state == STATE_PAUSED:
                    self._state = STATE_PLAYING

    def swipe_up(self):
        if len(self._bling_files) > 0:
            self._index = (self._index + 1) % len(self._bling_files)
            self._valid = False
            ui.blinds_up_unbuffered(self.watch)

    def swipe_down(self):
        if len(self._bling_files) > 0:
            self._index -= 1
            if self._index < 0:
                self._index = len(self._bling_files) - 1
            self._valid = False
            ui.blinds_down_unbuffered(self.watch)
