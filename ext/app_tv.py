from esp32 import RMT
import font_digital16 as small_font
import font_digital32 as large_font
import machine
from machine import Pin
from micropython import const
import time
import ui
from ui import UIButton, UILabel

CLASSNAME = "TVApp"

# Great resource: https://github.com/probonopd/irdb
# Another onehttp://www.hifi-remote.com/wiki/index.php/Infrared_Protocol_Primer
class TVApp():
    APP_NAME = "TV-B-Gone"
    WEIGHT = 15

    def __init__(self, watch):
        self.watch = watch
        self._lbl_title = UILabel(self.watch, large_font, 30, 120, "TV-B-GONE")
        self._lbl_status_1 = UILabel(self.watch, small_font, 35, 155, "")
        self._lbl_status_2 = UILabel(self.watch, small_font, 35, 175, "")
        self._btn_run = UIButton(self.watch, 172, 158, 'Off')
        self.rmt = RMT(0, pin=Pin(13), clock_div=32, tx_carrier=(38000, 50, 1))
        self._res = 1000000000 / \
            (self.rmt.source_freq() / self.rmt.clock_div())


# # To apply a carrier frequency to the high output
# r = esp32.RMT(0, pin=Pin(18), clock_div=8, tx_carrier=(38000, 50, 1))
# r.loop(True)
# # The channel resolution is 100ns (1/(source_freq/clock_div)).
# r.write_pulses((1, 20, 2, 40), 0)  # Send 0 for 100ns, 1 for 2000ns, 0 for 200ns, 1 for 4000ns

    def init(self):
        self.invalidate()

    def _redraw(self):
        ui.fill_rgb("/bg_tv-b-gone.rgb")
        self._lbl_title.fill_bg()
        self._lbl_title.draw()
        self._lbl_status_1.draw()
        self._lbl_status_2.draw()
        self._btn_run.draw()
        ui.push(self.watch)
        self._valid = True

    def foreground(self):
        if not self._valid:
            self._redraw()

    def invalidate(self):
        self._valid = False

    def touch(self, x, y):
        if self._btn_run.handle_touch(x, y):
            pulses = [100, 100, 100, 100, 100, 100, 100, 100]
            self.rmt.write_pulses(pulses)
            self.rmt.loop(True)
            # for code in tv.NApowerCodes:
            #     self._sendcode(code)
            # self.rmt.loop(False)
            print("Importing TV codes")
            self._lbl_status_1._text = "Loading Codes"
            self._redraw()
            import lib_tv_codes as tv

            i = 1
            total = len(tv.NEC) + len(tv.NECEXT) + len(tv.RAW)

            # IR timing is based on 160mhz clock
            machine.freq(160000000)

            # Send all NEC codes
            for nec in tv.NEC:
                self._lbl_status_1.fill_bg(ui.BLACK)
                self._lbl_status_2.fill_bg(ui.BLACK)
                self._lbl_status_1._text = "Sending NEC"
                self._lbl_status_2._text = "{0} of {1}".format(str(i), str(total))
                self._lbl_status_1.draw()
                self._lbl_status_2.draw()
                ui.push(self.watch)
                self._send_nec(nec[0], -1, nec[1])
                i += 1
            for nec in tv.NECEXT:
                self._lbl_status_1.fill_bg(ui.BLACK)
                self._lbl_status_2.fill_bg(ui.BLACK)
                self._lbl_status_1._text = "Sending NECEXT"
                self._lbl_status_2._text = "{0} of {1}".format(str(i), str(total))
                self._lbl_status_1.draw()
                self._lbl_status_2.draw()
                ui.push(self.watch)
                self._send_nec(nec[0], nec[1], nec[2])
                i += 1
            for raw in tv.RAW:
                self._lbl_status_1.fill_bg(ui.BLACK)
                self._lbl_status_2.fill_bg(ui.BLACK)
                self._lbl_status_1._text = "Sending RAW"
                self._lbl_status_2._text = "{0} of {1}".format(str(i), str(total))
                self._lbl_status_1.draw()
                self._lbl_status_2.draw()
                ui.push(self.watch)
                self._send_raw(raw)
                i += 1

            self.rmt.loop(False)

            # Slow clock back to save power
            machine.freq(80000000)

            self._lbl_status_1._text = "Complete"
            self._lbl_status_2._text = ""
            self._redraw()

            # self._send_nec(0x04, -1, 0x25) #vizio test code
            # self._send_nec(0x04, 0x08)
            # self._send_nec(0x44, 0x44, 0x30)

    def _push_nec_value(self, codes, value):
        # compute pulse size
        pulse = int(562500 / self._res)
        for i in range(8):
            b = value & 0x1 # pop LSB
            value >>= 1 # shift
            codes.append(pulse) # push a single on pulse, length of off pulse depends on 1 or 0
            if b:
                codes.append(pulse * 3)
            else:
                codes.append(pulse)

    # Send an NEC Extended IR command
    # Ref: https://www.sbprojects.net/knowledge/ir/nec.php
    def _send_nec(self, address, subdevice, command):
        # compute pulse size
        pulse = int(562500 / self._res)

        # Setup address and command values
        address &= 0xFF
        command &= 0xFF

        is_extended = True

        # Handle NEC1 addresses by performing logical compliment
        if subdevice < 0:
            subdevice = address ^ 0xFF
            subdevice &= 0xFF
            is_extended = False
        
        # Push headers
        if is_extended:
            codes = [int(9000000 / self._res), int(2256000 / self._res)]
        else:
            codes = [int(9000000 / self._res), int(4500000 / self._res)]

        # Push address onto code list LSB
        self._push_nec_value(codes, address)
        # Push address onto code list LSB inverted
        self._push_nec_value(codes, subdevice)
        # Push command onto code list LSB
        self._push_nec_value(codes, command)
        # Push command onto code list LSB inverted
        self._push_nec_value(codes, command ^ 0xFF)
        # End command
        codes.append(pulse)
        codes.append(32565) #maximum off time

        self.rmt.write_pulses(codes, 1)
        time.sleep(0.1)

        durations = []
        for c in codes:
            durations.append(c * self._res)
        
    def _send_raw(self, durations):
        codes = []
        if len(durations) > 125:
            return
            
        for d in durations:
            codes.append(int(d / self._res))
        self.rmt.write_pulses(codes,1)
        time.sleep(0.1)