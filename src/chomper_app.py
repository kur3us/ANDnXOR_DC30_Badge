import chomper_config as config
import chomper_wifi as wifi
from micropython import const
import os
import time
import ui_touch
import ui
import font_digital16 as font
import font_digital32 as large_font
import sys
import math

apps = []
app_index = -1
APP_LEFT = const(0)
APP_TOP = const(16)
APP_HEIGHT = const(208)
APP_BOTTOM = const(224)
APP_WIDTH = const(240)
TEXT_HEIGHT = const(8)
MARGIN = const(4)
TEXT_VSPACE = TEXT_HEIGHT + MARGIN

CHROME_DRAW_INTERVAL = const(2000)
next_chrome_draw_time = 0

def __register_app(name):
    global apps, watch
    try:
        module = __import__(name)
        class_ = getattr(module, module.CLASSNAME)
        instance = class_(watch)

        # This services two purposes:
        #   1. Prints helpful log information during boot which we all need
        #   2. It's a lazy way to check for standard properties in the target app, if property is not there, exception occurs
        print("REGISTERING: {0}::{1} [{2}]".format(instance.WEIGHT, instance.APP_NAME, module.CLASSNAME))

        # If we got this far, then all must be good (eyeroll emoji)
        apps.append(instance)
    except Exception as e:
        print("Unable to import app '{}".format(name))
        sys.print_exception(e)

def register_apps(_watch):
    '''
    Find apps in /apps directory and auto register them with app framework
    '''
    global watch
    watch = _watch

    global apps, app_index
    
    apps_found = []
    file_list = os.listdir()
    for file_name in file_list:
        if file_name.endswith('.py') and file_name.startswith('app_'):
            name = file_name[:-3] # Remove the .py
            if name not in apps_found:
                __register_app(name)
                apps_found.append(name)
        if file_name.endswith('.mpy') and file_name.startswith('app_'):
            name = file_name[:-4] # Remove the .mpy
            if name not in apps_found:
                __register_app(name)
                apps_found.append(name)         

    # Sort apps by their weight, low to high
    apps.sort(key=lambda x: x.WEIGHT)

    print("===================================")
    print("Apps Registered:")
    i = 1
    for app in apps:
        print("\t{0}: {1}".format(i, app.APP_NAME))
        i += 1
    print("===================================")

    # Start with the lightest app
    app_index = 0

    # Make sure we tell the first app to run to init itself
    if app_index < len(apps):
        apps[app_index].init()

def _draw_chrome():
    '''
    Draw standard top and bottom "chrome" around the app
    '''
    global watch
    ui.fill_rect(0,0,240,16,ui.BLACK)
    ui.fill_rect(0,224,240,16,ui.BLACK)

    dt = watch.pcf_rtc.datetime()
    h = dt[4]
    m = dt[5]

    # Adjust for timezone
    offs = int(config.config[config.KEY_OFFSET])
    if offs >= -12 and offs <= 12:
        h += offs
        if h < 0:
            h += 24
        h %= 24


    tstr = "{:02d}:{:02d}".format(h,m)
    ui.text(font, tstr, 105, 0, ui.INDIGO)

    if watch.ble.is_inuse():
        ui.draw_rgb("/icon_bt.rgb", 160, 0, 11, 16)

    if wifi.isconnected():
        ui.draw_rgb("/icon_wifi.rgb", 174, 0, 23, 16)

    if watch.axp.isVBUSPlug():
        ui.draw_rgb("/icon_charge.rgb", 200,0,10,16)

    pct = watch.axp.getBattPercentage()
    if pct > 70:
        ui.draw_rgb("/icon_batt_full.rgb", 212, 0, 27, 16)
    elif pct > 20:
        ui.draw_rgb("/icon_batt_half.rgb", 212, 0, 27, 16)
    else:
        ui.draw_rgb("/icon_batt_empty.rgb", 212, 0, 27, 16)

    if config.config[config.KEY_CURRENT]:
        ma = watch.axp.getBattDischargeCurrent()
        ui.text(font, str(ma) + " mA", 192, APP_BOTTOM+4, ui.PEACH, ui.BLACK)

    steps = watch.accel.step_count()
    step_length = len(str(steps)) #This will adjust centering at X=100 as steps increase and number of charachters to print increase
    ui.text(font, str(steps) + " steps", 97 - step_length, APP_BOTTOM+4, ui.PEACH)


def _app_next():
    global apps, app_index, watch
    if len(apps) < 2:
        return
    app_index = app_index + 1
    if app_index >= len(apps):
        app_index = 0
    
    ui.blinds_left_unbuffered(watch)

    text = ""
    try: 
        text = "[" + apps[app_index].APP_NAME + "]"
    except: 
        text = "[???]"

    #Pad pixels to center the string
    i = 0
    text_x = 0
    text_width = 14
    text_length = len(text)
    while i < ((240 - (text_width * text_length))//2):
        text_x += 1
        i += 1 

    watch.display.write(large_font, text, text_x, 112, ui.PEACH, ui.INDIGO)

    ui.fill_rect(0, APP_TOP, 240, APP_HEIGHT, ui.BLACK)
    apps[app_index].init()

def _app_prev():
    global apps, app_index
    if len(apps) < 2:
        return
    if app_index == 0:
        app_index = len(apps) - 1
    else:
        app_index = app_index - 1

    ui.blinds_right_unbuffered(watch)
    text = ""
    try: 
        text = "[" + apps[app_index].APP_NAME + "]"
    except: 
        text = "[???]"
    
    #Pad pixels to center the string
    i = 0
    text_x = 0
    text_width = 14
    text_length = len(text)
    while i < ((240 - (text_width * text_length))//2):
        text_x += 1
        i += 1 

    watch.display.write(large_font, text, text_x, 112, ui.PEACH, ui.INDIGO)

    ui.fill_rect(0, APP_TOP, 240, APP_HEIGHT, ui.BLACK)
    apps[app_index].init()

def get_app_by_name(name):
    '''
    Retrieve an app instance by it's name
    '''
    for app in apps:
        if app.APP_NAME == name:
            return app
    return None

def foreground():
    '''
    Execute an app once in the foreground, this is called at some periodicity
    '''
    global apps, app_index, watch, next_chrome_draw_time

    # If a touch event happened stay awake and handle in the UI somehow
    touch = watch.touch.do_work()
    if touch[0] > ui_touch.GESTURE_NONE:
        watch.defer_sleep()
        end_x = touch[2][0]
        end_y = touch[2][1]
        # Pass short touches to app
        if touch[0] == ui_touch.GESTURE_SHORT_PRESS:
            apps[app_index].touch(end_x, end_y)
        elif touch[0] == ui_touch.GESTURE_LONG_PRESS:
            pass #not implemented
        elif touch[0] == ui_touch.GESTURE_SWIPE_LEFT:
            _app_next()
            next_chrome_draw_time = 0
        elif touch[0] == ui_touch.GESTURE_SWIPE_RIGHT:
            _app_prev()
            next_chrome_draw_time = 0
        elif touch[0] == ui_touch.GESTURE_SWIPE_UP:
            try:
                apps[app_index].swipe_up()
            except:
                pass
        elif touch[0] == ui_touch.GESTURE_SWIPE_DOWN:
            try:
                apps[app_index].swipe_down()
            except:
                pass

    # don't do any updates while being touched, otherwise touches can be missed
    if not watch.touch.is_touched(): 
        if next_chrome_draw_time < time.ticks_ms():
            next_chrome_draw_time = time.ticks_ms() + CHROME_DRAW_INTERVAL
            _draw_chrome()

    # don't do any updates while being touched, otherwise touches can be missed
    # Split from previous if statement so touch can kinda sorta interrupt
    if not watch.touch.is_touched(): 
        if len(apps) > 0:
            apps[app_index].foreground()

# Invalidate the current app
def invalidate():
    try:
        apps[app_index].invalidate()
    except:
        pass
