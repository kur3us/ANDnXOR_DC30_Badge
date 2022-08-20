""" AND!XOR DC30 Example App

Hello there fellow hacker! We are releasing our very own app framework for our DC30 watch for all you 
hackers to create apps of your very own in honor of the greatest actor of all time, Matt Damon (despite
that superb owl commercial recently :/). 

These apps are simple, we do some of the work for you, like drivers, touch, UI, etc. However there are
a few things you should know. 

1. Your app is "run" every 500 to 1000ms via the foreground() function when the watch is awake
2. Your app cannot run in the background while the watch is asleep - unless you do some threading YMMV
3. Try to avoid long running actions or loops, these prevent the watch from doing its thing
4. __init__ is called when the watch is instantiated
5. init() [confusing! we know!] is called whenever the app is brought swiped to by the user
6. Graphics are buffered by the UI library. When you're don't drawing, push buffer with ui.push()
7. GIF and 8-bit RGB playing is supported through low level C library (see app_bling.py) - although
   these violate #2 above
8. Apps only have access to a 240x208 canvas, see chomper_app.APP_* for specific coordinates

How do I run my app!? We recommend mpremote or ampy. 

    pip3 install adafruit_ampy
    ampy put app_mattdamon.py

mpremote is similar
    
    pip3 install mpremote
    mpremote cp app_mattdamon.py :
    
But this just uploads your app. You probably notice the watch screen is black :( You need to get main.py
to run again. Restarting the watch will run main.py. Another way to is run main.py from your local device.

First download a copy of our main.py from the watch (this only needs to be done once)

    ampy get main.py > main.py

To put and run the main.py

    ampy run main.py

Alternative, reset watch with mpremote

    mpremote exec 'import machine; machine.reset()'

Watch will startup and log some stuff. Ampy has issues with timeouts. But you should see if your app
had issues or at least swipe over to it.

For logging and REPL we like

    picocom -b 115200 /dev/ttyACM0

"""

import chomper_app as app
import chomper_config as config
import font_digital16 as small_font
import ui
from ui import UILabel, UIButton

"""
CLASSNAME is required, app discovery routine needs to know what class to instantiate. YOLO
It also must be outside of the class scope for obvious reasons
"""
CLASSNAME = "ExampleApp"

"""
Your app must be a class, we thought about inheritance and all that, but this kept it simple.
"""
class ExampleApp():

    """
    APP_NAME is required and should be short. It will be displayed on the screen as the user 
    swipes between apps. We're using a 32pt font so space is at a premium.
    """
    APP_NAME = "Example"

    """
    WEIGHT is also required and hints to the app framework how far back in the menu system the 
    app should be. The heaviest apps will be last when swiping from left to right. Lightest app
    will be the first shown to the user after a reboot.
    """
    WEIGHT = 25

    def __init__(self, watch):
        """
        __init__() is required for app instantiation. It is called exactly once during boot when the
        app is found by the app framework. This is where you should create any UI widgets like labels
        and buttons.

        Note in this case we did not set the text of the two labels, instead they are set in the touch() 
        function so that they appear when the button is activated.
        """

        self.watch = watch
        y = app.APP_TOP
        self._lbl_title = UILabel(self.watch, small_font, 77, app.APP_TOP + 140, "")
        y += app.TEXT_VSPACE
        self._lbl_name = UILabel(self.watch, small_font, 60, app.APP_TOP + 160, "")
        self._btn = UIButton(self.watch, 64, app.APP_TOP + 100, text="Example")

    def init(self):
        """
        init() is called by the app framework when the user swipes to the app. It is a best practice to 
        reset state in most use cases. 
        
        In all cases, you should invalidate() your graphics state in order to force a full redraw. 
        Remember the user is coming from a different app. The watch will clear the buffer with a black
        rectangle but your elements need to be drawn on top of that.
        """

        self.invalidate()

    def invalidate(self):
        """
        Invalidate the graphics buffer state so next opportunity the app can redraw it. Redrawing and pushing
        every app cycle makes the UI unresponsive and jittery. 

        Do not count on only your app controlling the graphics buffer. There are some limited cases where the 
        watch will invalidate the current app's buffer (such as on screen wake).
        """

        self._valid = False

    def _redraw(self):
        """
        _redraw() is not required. But after writing a few apps, we found it to be a best practice to have a 
        single function that draws all elements, especially when the app has a state machine. Do as you wish.

        Note the ui.push() function, without it we have only pushed pixels into a buffer. That buffer needs
        to go to the screen.

        ui.push() takes 87ms. Most hoomans won't perceive this unless you try to do animation with it.
        """

        ui.fill_rgb("/bg_example.rgb")
        self._lbl_title.draw()
        self._lbl_name.draw()
        self._btn.draw()
        ui.push(self.watch)
        self._valid = True
    
    def foreground(self):
        """
        foreground() as mentioned earlier is run every 500 to 1000ms depending on how the app framework is 
        feeling and the current sleep state. When the watch is on it uses a TON of energy. We have to keep 
        maximize sleeping and minimize CPU use.

        Note the check for graphics buffer validity.
        """

        if not self._valid:
            self._redraw()

    def touch(self, x, y):
        """
        Hey look we can handle touch events! You can do something with the X/Y but if you want your button(s)
        to work, pass the x,y to each button and it will tell if it was pressed. 
        """

        if self._btn.handle_touch(x,y):
            print("Button pressed")
            self._lbl_title._text = "Example App"
            self._lbl_name._text = "whoami: " + config.config[config.KEY_NAME]
            self._redraw()

    def swipe_up(self):
        """
        UI framework will also send us gestures. These are optional functions but useful for some things.
        """

        print("Swipe up!")

    def swipe_down(self):
        """
        Ditto
        """
        print("Swipe down!")