'''
Shim between FT6336 hardware and UI layer
'''
import chomper_config as config
from focaltouch import FocalTouch
from machine import Pin
from micropython import const
import time

GESTURE_NONE = const(0)
GESTURE_SHORT_PRESS = const(1)
GESTURE_LONG_PRESS = const(2)
GESTURE_SWIPE_LEFT = const(3)
GESTURE_SWIPE_RIGHT = const(4)
GESTURE_SWIPE_UP = const(5)
GESTURE_SWIPE_DOWN = const(6)

LIFT_TIMEOUT_MS = const(100)

SWIPE_MIN_TIME_MS = const(50)
SWIPE_MAX_TIME_MS = const(800)
SWIPE_DISTANCE_PX = const(60)
LONG_PRESS_TIME_MS = const(500)


class UITouch:
    def __init__(self, i2c):
        self.focaltouch = FocalTouch(i2c, debug=False)
        irq_pin = Pin(38, Pin.IN)
        irq_pin.irq(trigger=Pin.IRQ_FALLING, handler=self._touch_irq)
        self.irq = 0
        self.inverted = config.config[config.KEY_INVERTED] == True
        print("UI_TOUCH: Shim Setup Complete, inverted={0}".format(
            self.inverted))
        self._wait_for_lift = False
        self._start_point = [0,0]
        self._end_point = [0,0]
        self._last_time = time.ticks_ms()
        self._touched = False

    def _touch_irq(self, pin):
        point = self._touch_to_tuple(self.focaltouch.touches[0])

        if point == [0,0]:
            return

        # Starting a new gesture
        if time.ticks_ms() > (self._last_time + LIFT_TIMEOUT_MS) or not self._touched:
            # print("{}:::TOUCH START".format(time.ticks_ms()))
            self._start_point = point
            self._touched = True

        # Update our the timestamp of the last touch and move the end point
        self._last_time = time.ticks_ms()
        self._end_point = point

    def _touch_to_tuple(self, touch):
        '''
        Converted a touch point object into a simple x/y coordinate normalized against current inverted state
        '''
        if self.inverted:
            return [240-touch['x'], 240-touch['y']]
        else:
            return [touch['x'], touch['y']]

    def do_work(self):
        
        if self._touched:
            self._touched = False
            dx = self._end_point[0] - self._start_point[0]
            dy = self._end_point[1] - self._start_point[1]

            gesture = GESTURE_SHORT_PRESS #default gesture

            #Pick x or y direction as bias then determine if gesture occurred
            if abs(dx) > abs(dy):
                if dx < -SWIPE_DISTANCE_PX:
                    gesture = GESTURE_SWIPE_LEFT
                elif dx > SWIPE_DISTANCE_PX:
                    gesture = GESTURE_SWIPE_RIGHT
            else:
                if dy < -SWIPE_DISTANCE_PX:
                    gesture = GESTURE_SWIPE_UP
                elif dy > SWIPE_DISTANCE_PX:
                    gesture = GESTURE_SWIPE_DOWN
        
            if self._start_point == [0,0] or self._end_point == [0,0]:
                # print("invalid touch coords")
                gesture = GESTURE_NONE

            # print("{}:::g:{} sp:{} ep:{} dx:{} dy:{}".format(time.ticks_ms(), gesture,  self._start_point, self._end_point, dx,dy))
            
            res = [gesture, self._start_point, self._end_point, 0]
            self._start_point = [0,0]
            self._end_point = [0,0]
            return res

        # Default action is to return no gesture unless there is a lift event above
        return [GESTURE_NONE, [0, 0], [0, 0]]

    def is_touched(self):
        return self._touched

    def reset(self):
        self._start_point = [0,0]
        self._end_point = [0,0]
        self._touched = False
        self._last_time = time.ticks_ms()