import chomper_config as config
import font_digital as dfont
import font_digital32 as bfont

import sys
import ui
import math

from ui import *

CLASSNAME = "WatchApp"

class WatchApp():
    APP_NAME = "Watch Face"
    WEIGHT = 10

    def __init__(self, _watch):
        self.watch = _watch
        self._face_type = 0 # 0 = Digital Face, 1 = Binary, 2 thru 5 = Analog

        #Anchor the Binary Watch Labels
        bx = 153
        by = 137
              
        self._lbl_bin_min_0 = UILabel(self.watch, bfont, bx, by-30, '*')
        self._lbl_bin_min_1 = UILabel(self.watch, bfont, bx-15, by-30, '*')
        self._lbl_bin_min_2 = UILabel(self.watch, bfont, bx-30, by-30, '*')
        self._lbl_bin_min_3 = UILabel(self.watch, bfont, bx-45, by-30, '*')
        self._lbl_bin_min_4 = UILabel(self.watch, bfont, bx-60, by-30, '*')
        self._lbl_bin_min_5 = UILabel(self.watch, bfont, bx-75, by-30, '*')

        self._lbl_bin_hrs_0 = UILabel(self.watch, bfont, bx-5, by-60, '*')
        self._lbl_bin_hrs_1 = UILabel(self.watch, bfont, bx-20, by-60, '*')
        self._lbl_bin_hrs_2 = UILabel(self.watch, bfont, bx-35, by-60, '*')
        self._lbl_bin_hrs_3 = UILabel(self.watch, bfont, bx-50, by-60, '*')
        self._lbl_bin_hrs_4 = UILabel(self.watch, bfont, bx-65, by-60, '*')

        self._bin_sec_0 = 0
        self._bin_sec_1 = 0
        self._bin_sec_2 = 0
        self._bin_sec_3 = 0
        self._bin_sec_4 = 0
        self._bin_sec_5 = 0
        self._bin_min_0 = 0
        self._bin_min_1 = 0
        self._bin_min_2 = 0
        self._bin_min_3 = 0
        self._bin_min_4 = 0
        self._bin_min_5 = 0
        self._bin_hrs_0 = 0
        self._bin_hrs_1 = 0
        self._bin_hrs_2 = 0
        self._bin_hrs_3 = 0
        self._bin_hrs_4 = 0
        self.invalidate()
 
    def _redraw(self):
        # Set Background - Your watch face backgrounds need to be exactly 240x208 before converting to RGB
        if self._face_type == 0:
            ui.fill_rgb("/wf_d_defcon.rgb")  #Digital Clock Background
        elif self._face_type == 1:
            ui.fill_rgb("/wf_b_chip.rgb")    #Binary Clock Background
        elif self._face_type == 2:
            ui.fill_rgb("/wf_a_andnxor.rgb") #Analog Clock Background
        elif self._face_type == 3:
            ui.fill_rgb("/wf_a_defcon.rgb")  #Analog Clock Background
        elif self._face_type == 4:
            ui.fill_rgb("/wf_a_urbane.rgb")  #Analog Clock Background
        else:
            ui.fill_rgb("/wf_a_w00w00.rgb")  #Analog Clock Background

        # Stage Time Array
        dt = self.watch.pcf_rtc.datetime()
        h = dt[4]
        m = dt[5]
        s = dt[6]

        # Adjust for timezone
        offs = int(config.config[config.KEY_OFFSET])
        if offs >= -12 and offs <= 12:
            h += offs
            if h < 0:
                h += 24
            h %= 24

        #Hack Time
        dt_str = "{:02d}:{:02d}".format(h,m)

        # Draw Digital Clock
        if self._face_type == 0: 
            ui.draw_text_center(self.watch, dfont, dt_str, 94, ui.PEACH)
            ui.push(self.watch)

        # Draw Binary Clock
        elif self._face_type == 1: 
            #Convert RTC time units in to bits
            self._bin_min_0 = self._bitAtGivenPosSetOrUnset( m, 0)
            self._bin_min_1 = self._bitAtGivenPosSetOrUnset( m, 1)
            self._bin_min_2 = self._bitAtGivenPosSetOrUnset( m, 2)
            self._bin_min_3 = self._bitAtGivenPosSetOrUnset( m, 3)
            self._bin_min_4 = self._bitAtGivenPosSetOrUnset( m, 4)
            self._bin_min_5 = self._bitAtGivenPosSetOrUnset( m, 5)
            self._bin_hrs_0 = self._bitAtGivenPosSetOrUnset( h, 0)
            self._bin_hrs_1 = self._bitAtGivenPosSetOrUnset( h, 1)
            self._bin_hrs_2 = self._bitAtGivenPosSetOrUnset( h, 2)
            self._bin_hrs_3 = self._bitAtGivenPosSetOrUnset( h, 3)
            self._bin_hrs_4 = self._bitAtGivenPosSetOrUnset( h, 4)

            #Set Bit Colors for On or Off
            self._lbl_bin_min_0._color = self._binaryBitColor(self._bin_min_0)
            self._lbl_bin_min_1._color = self._binaryBitColor(self._bin_min_1)
            self._lbl_bin_min_2._color = self._binaryBitColor(self._bin_min_2)
            self._lbl_bin_min_3._color = self._binaryBitColor(self._bin_min_3)
            self._lbl_bin_min_4._color = self._binaryBitColor(self._bin_min_4)
            self._lbl_bin_min_5._color = self._binaryBitColor(self._bin_min_5)

            self._lbl_bin_hrs_0._color = self._binaryBitColor(self._bin_hrs_0)
            self._lbl_bin_hrs_1._color = self._binaryBitColor(self._bin_hrs_1)
            self._lbl_bin_hrs_2._color = self._binaryBitColor(self._bin_hrs_2)
            self._lbl_bin_hrs_3._color = self._binaryBitColor(self._bin_hrs_3)
            self._lbl_bin_hrs_4._color = self._binaryBitColor(self._bin_hrs_4)

            #Draw Them Bits
            self._lbl_bin_min_0.draw()
            self._lbl_bin_min_1.draw()
            self._lbl_bin_min_2.draw()
            self._lbl_bin_min_3.draw()
            self._lbl_bin_min_4.draw()
            self._lbl_bin_min_5.draw()
            self._lbl_bin_hrs_0.draw()
            self._lbl_bin_hrs_1.draw()
            self._lbl_bin_hrs_2.draw()
            self._lbl_bin_hrs_3.draw()
            self._lbl_bin_hrs_4.draw()

            ui.push(self.watch)

            self.quick_bits_draw_sec(s)


        #Draw Analog Clock
        else: 
            #Thank You WaspOS for letting Hyr0n learn from your polar code
            print("Analog Clock!")
            origin_x = 120
            origin_y = 120
            
            # Draw the hour dividers on the clock - if the watch face doesnt have them
            # for theta in range(12):
            #    self.polar(origin_x, origin_y, theta * 360 // 12, 80, 90, ui.RED)   
            
            # Draw the hour & minute hands
            hh = -((30 * (h % 12)) + (m / 2)) + 90
            mm = -(6 * m) + 90
            self.polar(origin_x, origin_y, mm, 0, 100, ui.PURPLE)
            self.polar(origin_x, origin_y, hh, 0, 60, ui.PURPLE)
            
            #Nub in the center of clock hands
            self._lbl_analog = UILabel(self.watch, bfont, origin_x-5, origin_y-12, '*')
            self._lbl_analog._color = PURPLE
            self._lbl_analog.draw()
            ui.push(self.watch)

        self.last_min = dt[5]
        self.last_sec = dt[6]

    def quick_bits_draw_sec(self, s):
        bx = 153
        by = 137
        for i in range(6):
            self.watch.display.write(bfont, "*", bx, by, self._binaryBitColor(s & (1 << i)))
            bx -= 15

    def polar(self, x, y, theta, r0, r1, color):
        # Our plot is 0,0 starting in top left (screen matrix) vice cartesian (bottom left)
        # So you flip the use of SIN vs COS for X and Y respectively
        # Yeah, that fucked my brain up too, then I got over it
        # Spreadsheets help to prototype code
        to_radians = math.pi / 180
        xdelta = math.cos(theta * to_radians)
        ydelta = math.sin(theta * to_radians)

        #Start the line here
        x0 = x + int(xdelta * r0)
        y0 = y - int(ydelta * r0)

        #End the line here
        x1 = x + int(xdelta * r1)
        y1 = y - int(ydelta * r1)

        #Draw That Fancy Line(s), multiple so its thikk
        ui.line(x0, y0, x1, y1, color)
        ui.line(x0+1, y0+1, x1+1, y1+1, color)
        ui.line(x0-1, y0-1, x1-1, y1-1, color)
        ui.line(x0+2, y0+2, x1+2, y1+2, ui.DARK_GRAY)
        ui.line(x0-2, y0-2, x1-2, y1-2, ui.DARK_GRAY)

    def init(self):
        self.invalidate()

    def invalidate(self):
        self.last_min = -1
        self.last_sec = -1
    
    def foreground(self):
        dt = self.watch.pcf_rtc.datetime()

        # only redraw when seconds change
        if dt[5] != self.last_min:
            self._redraw()
        
        if self._face_type == 1:
            if dt[6] != self.last_sec:
                self.quick_bits_draw_sec(dt[6])

    def touch(self, x, y):
        """
        Hey look we can handle touch events! You can do something with the X/Y but if you want your button(s)
        to work, pass the x,y to each button and it will tell if it was pressed. 
        """

    def swipe_up(self):
        # This is used to cycle watch face states between digital, binary, and analog
        if self._face_type < 5:
            self._face_type += 1
        else:
            self._face_type = 0
        ui.blinds_up_unbuffered(self.watch)
        self.invalidate()

    def swipe_down(self):
        # This is used to cycle watch face states between digital, binary, and analog
        if self._face_type > 0:
            self._face_type -= 1
        else:
            self._face_type = 5
        ui.blinds_down_unbuffered(self.watch)
        self.invalidate()
    
    def _binaryBitColor(self, b):
        #This returns a color based on bit value
        if b == 0:
            return ui.DARK_GRAY
        else:
            return ui.PEACH

    def _bitAtGivenPosSetOrUnset(self, n, k):
        #Reference Open Source Code: https://www.geeksforgeeks.org/check-whether-bit-given-position-set-unset/
        new_num = n >> (k)
        #if it results to '1' then bit is set,
        #else it results to '0' bit is unset
        return (new_num & 1)