import chomper_app as app
import chomper_wifi as wifi
import font_digital16 as small_font
from micropython import const
import ui
from ui import UIButton, UILabel
import lib_update as update

STATE_IDLE = const(0)
STATE_UPDATING = const(1)
STATE_COMPLETE = const(2)

CLASSNAME = "UpdateApp"
FILE = "/upgrayedd"

class UpdateApp():
    APP_NAME = "Update"
    WEIGHT = 35

    def __init__(self, _watch):
        self.watch = _watch
        self.updated = "Last Upgrayedd: NEVER"

        try:
            f = open(FILE, "r")
            str = f.readline()
            if len(str) < 8:
                self.updated = "Last Upgrayedd: " + str
        except:
            print("APP_UPDATE: upgrayedd file missing, assuming no updates have occurred")

        self._btn_update = UIButton(self.watch, 40, app.APP_TOP + 140, text="UPGRAYEDD")
        self._lbl_state = UILabel(self.watch, small_font, 75, 40, self.updated)
        self._lbl_msg = UILabel(self.watch, small_font, 90, 58, 'Message')

    def _cb(self, msg, error):
        # Erase previous text
        self._lbl_msg.fill_bg()

        # Determine text color based on status
        c = ui.WHITE
        if error:
            c = ui.RED

        # Update label and redraw
        self._lbl_msg._color = c
        self._lbl_msg._text = msg
        self._lbl_msg.draw()
        ui.push(self.watch)

    def _redraw(self):
        ui.fill_rgb("/upgrayedd.rgb")
        if self._state == STATE_IDLE:
            self._lbl_state._text = self.updated
            self._btn_update.draw()
        elif self._state == STATE_UPDATING:
            self._lbl_state._text = "UPGRAYEDDING..."
        elif self._state == STATE_COMPLETE:
            self._lbl_state._text = "Upgrayedd Complete :)"
        self._lbl_state.draw()
        ui.push(self.watch)
        self._valid = True

    def init(self):
        self._state = STATE_IDLE
        self.invalidate()

    def invalidate(self):
        self._valid = False

    def foreground(self):
        if not self._valid:
            self._redraw()

    def touch(self, x, y):
        if self._state == STATE_IDLE:
            if self._btn_update.handle_touch(x, y):
                self._state = STATE_UPDATING
                self.invalidate()
                self._redraw()

                # Force time update since good wifi is probably nearby
                wifi.next_connect_time = 0
                wifi.do_work(self.watch)

                dt = self.watch.pcf_rtc.datetime()
                timestamp_str = "{}/{}".format(dt[1], dt[2])
                print("APP_UPGRADE: Recording upgrayedd timestamp as ", timestamp_str)

                try:
                    f = open(FILE, "w")
                    f.write(timestamp_str)
                    f.close()
                except Exception as e:
                    print("APP_UPGRADE: Unable to record upgrayedd timestamp:", e)

                update.do_update(self._cb)
                self._state = STATE_COMPLETE
                self.invalidate()
                self._redraw()
