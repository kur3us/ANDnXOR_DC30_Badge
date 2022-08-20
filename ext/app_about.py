import chomper_app as app
import chomper_c
import chomper_config as config
import font_digital16 as font
import font_digital32 as font_large
import os
import ui

CLASSNAME = "AboutApp"

class AboutApp():
    APP_NAME = "About"
    WEIGHT = 40

    def __init__(self, watch):
        self.watch = watch

    def init(self):
        self.invalidate()

    def invalidate(self):
        self._valid = False

    def _redraw(self):
        ui.fill_rgb("/bg_about.rgb")
        y = app.APP_TOP + 15
        x = 16
        ui.text(font_large, "About", x, y, ui.ORANGE)
        y = y + font_large.HEIGHT + 2
        ui.text(font, "whoami: " + config.config[config.KEY_NAME], x, y, ui.WHITE)
        y = y + font.HEIGHT + 2
        ui.text(font, "Firmware: "+chomper_c.version(), x, y, ui.WHITE)
        
        # Sponsors should not overlap with sun
        y = y + font.HEIGHT + 50
        ui.text(font, "Sponsor: Urbane Security", x, y, ui.WHITE)
        y = y + font.HEIGHT + 2
        ui.text(font, "Sponsor: w00w00", x, y, ui.WHITE)
        y = y + font.HEIGHT + 2
        ui.text(font, "Sponsor: Philahtropists", x, y, ui.WHITE)
        ui.push(self.watch)
        self._valid = True
    
    def foreground(self):
        if not self._valid:
            self._redraw()

    def touch(self, x, y):
        pass