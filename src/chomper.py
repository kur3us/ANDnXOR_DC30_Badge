import chomper_c
import chomper_config as config
import chomper_wifi as wifi
import axp202c
import gc
from lib_ble import BLE
import logo
import machine
from machine import Pin, I2C, PWM, RTC, SPI, lightsleep
from micropython import const
import ninja
import os
import pcf8563
import random
import sys
import time
import st7789
import ubinascii
import vga1_8x8 as font

FAIL_SAFE = False

# These dependencies may not come until after a wifi update
try:
    from accelerometer import Accelerometer
except Exception as e:
    print("******************************************")
    print("CHOMPER: Failure loading Accerlometer shim")
    sys.print_exception(e)
    print("CHOMPER will enter failsafe mode shortly!")
    print("******************************************")
    FAIL_SAFE = True # Go into a fail safe mode to prompt user to update over WIFI

try:
    import chomper_app
except Exception as e:
    print("******************************************")
    print("CHOMPER: Failure loading Chomper app lib")
    sys.print_exception(e)
    print("CHOMPER will enter failsafe mode shortly!")
    print("******************************************")
    FAIL_SAFE = True # Go into a fail safe mode to prompt user to update over WIFI

try:
    from ui_touch import UITouch
except Exception as e:
    print("******************************************")
    print("CHOMPER: Failure loading UI Touch lib")
    sys.print_exception(e)
    print("CHOMPER will enter failsafe mode shortly!")
    print("******************************************")
    FAIL_SAFE = True 

#
# GREAT REFERENCE https://gitlab.com/mooond/t-watch2020-esp32-with-micropython/-/blob/master/lily.py
#

AWAKE_TIME_MS = const(15*1000)
CHOMPER_STATE_AWAKE = const(0)
CHOMPER_STATE_SLEEP = const(1)
BACKLIGHT_PIN = const(15)
# PWM resolution is 10 bits, max value here is 1024
BACKLIGHT_DUTY_MAX = const(1024)
BACKLIGHT_FREQ = const(1024)


class Chomper:
    def __init__(self):
        '''
        Initialize watch
        '''
        print("AND!XOR DC30 Chomper")

        # Load config as early as possible
        config.load()

        self.axp = axp202c.PMU()
        # Let AXP init I2C0 then use it elseware. Ugly AF I don't like it.
        # TODO: maybe change this later
        self.i2c0 = self.axp.bus
        self.i2c1 = I2C(1, scl=Pin(32), sda=Pin(23))

        # Setup HW RTC
        self.pcf_rtc = pcf8563.PCF8563(self.i2c0)
        # Setup upy RTC is this more efficient than calling PCF all the time?
        self.rtc = RTC()

        # Setup touch shim
        try:
            self.touch = UITouch(self.i2c1)
        except Exception as e:
            print("CHOMPER: Unable to setup UI Touch shim", e)

        # Setup motor, simply IO on v3 watch
        self.motor = Pin(4, Pin.OUT)

        # Setup wifi
        wifi.set_hostname(self.unique_id)
        if wifi.isconnected():
            print("CHOMPER: WIFI already connected, disconnecting")
            wifi._disconnect()

        # Start awake, we will sleep later
        self.state = CHOMPER_STATE_AWAKE

        self.sleep_usage = -1
        self.backlight_percent = 80

        self._init_power()
        self._init_rtc()
        
        self._init_display()

        self.display.text(font, "init_dc30(0)", 0, 0, st7789.GREEN, st7789.BLACK)

        if FAIL_SAFE:
            self.failsafe()
        else:
            self.display.text(font, "print('Hello AND!XOR')", 0, 10, st7789.GREEN, st7789.BLACK)
            self.accel = Accelerometer(self.i2c0)
            self.ble = BLE()
            self.display.text(font, "import ui", 0, 20, st7789.GREEN, st7789.BLACK)
            self.display.text(font, "ui.begin()", 0, 20, st7789.GREEN, st7789.BLACK)
            self.boot()
            self.loop()

    def _axp_interrupt(self, pin):
        '''
        Handle interrupts coming from AXP HW to include battery conditions and hardware button 
        '''
        self.axp.readIRQ()
        if self.axp.isPEKShortPress():
            if self.state == CHOMPER_STATE_AWAKE:
                self._sleep()
            else:
                self._wake()
        elif self.axp.isPEKLongPress():
            pass
        elif self.axp.isVBUSPlugIn():
            pass
        self.axp.clearIRQ()

    def _init_power(self):
        # Change the button boot time to 4 seconds
        self.axp.setShutdownTime(axp202c.AXP202_SHUTDOWN_TIME_4S)
        # Turn off the charging instructions, there should be no
        self.axp.setChgLEDMode(axp202c.AXP20X_LED_OFF)
        # Turn off external enable
        self.axp.disablePower(axp202c.AXP202_EXTEN)
        # axp202 allows maximum charging current of 1800mA, minimum 300mA
        self.axp.setChargeControlCur(300)
        self.axp.enablePower(axp202c.AXP202_LDO2)

        # Required on v2 watch
        # axp.disablePower(axp202c.AXP202_LDO3)
        # axp.setLDO3Voltage(3300)
        # axp.enablePower(axp202c.AXP202_LDO3)

        # v3 watch
        ips = self.axp.read_byte(axp202c.AXP202_IPS_SET)
        ips = ips | 0x03
        self.axp.write_byte(axp202c.AXP202_IPS_SET, ips)  # limiting off
        
        # Audio power domain is AXP202 LDO4
        self.axp.disablePower(axp202c.AXP202_LDO4)
        # self.axp.setLDO4Voltage(3300)
        # self.axp.enablePower(axp202c.AXP202_LDO4)

        # LDO3 not used in v3
        self.axp.disablePower(axp202c.AXP202_LDO3)

        self.axp.enableADC(axp202c.AXP202_ADC1, axp202c.AXP202_BATT_VOL_ADC1)
        self.axp.enableADC(axp202c.AXP202_ADC1, axp202c.AXP202_BATT_CUR_ADC1)
        self.axp.enableADC(axp202c.AXP202_ADC1, axp202c.AXP202_VBUS_VOL_ADC1)
        # self.axp.enableADC(axp202c.AXP202_ADC1, axp202c.AXP202_VBUS_CUR_ADC1)

        self.axp.clearIRQ()

        # Setup AXP interrupts
        self.axp.enableIRQ(axp202c.AXP202_PEK_SHORTPRESS_IRQ)
        self.axp.enableIRQ(axp202c.AXP202_CHARGING_IRQ)
        self.axp.enableIRQ(axp202c.AXP202_CHIP_TEMP_HIGH_IRQ)
        self.axp.enableIRQ(axp202c.AXP202_BATT_OVER_TEMP_IRQ)
        self.axp.enableIRQ(axp202c.AXP202_CHARGING_FINISHED_IRQ)
        self.axp.enableIRQ(axp202c.AXP202_CHARGING_IRQ)
        self.axp.enableIRQ(axp202c.AXP202_BATT_EXIT_ACTIVATE_IRQ)
        self.axp.enableIRQ(axp202c.AXP202_BATT_ACTIVATE_IRQ)

        axpint = Pin(35, Pin.IN)
        axpint.irq(trigger=Pin.IRQ_FALLING, handler=self._axp_interrupt)

    def _init_display(self):
        # Enable display
        spi = SPI(1, baudrate=32000000,
                  sck=Pin(18), mosi=Pin(19))
        rot = 2 # default screen rotation is portrait inverted (relative to user this is non-inverted though)

        # Allow settings to override and invert display
        if config.config[config.KEY_INVERTED]:
            rot = 0

        self.display = st7789.ST7789(spi,
                                     240, 240,
                                     cs=Pin(5, Pin.OUT),
                                     dc=Pin(27, Pin.OUT),
                                     rotation=rot)
        self.display.init()
        backlight_pin = Pin(BACKLIGHT_PIN)
        self.backlight = PWM(backlight_pin)
        self.backlight.freq(BACKLIGHT_FREQ)
        self.set_backlight_level(self.backlight_percent)

    def _init_rtc(self):
        # update upy RTC API with current hardware RTC time
        pcf_dt = self.pcf_rtc.datetime()
        self.rtc.init(pcf_dt)

    def set_backlight_level(self, percent):
        if 0 <= percent <= 100:
            duty = int(percent * (BACKLIGHT_DUTY_MAX / 100))
            # print("Setting BL duty cycle to: ", duty)
            self.backlight.duty(duty)

    def _sleep(self):
        print("CHOMPER: Going to sleep")
        # Turn off backlight
        # self.display.off()
        for i in range(self.backlight_percent, 0, -1):
            self.set_backlight_level(i)
            time.sleep_ms(10)
        self.axp.disablePower(axp202c.AXP202_LDO2)
        self.state = CHOMPER_STATE_SLEEP

    def _wake(self):
        print("CHOMPER: Waking up")

        # trigger current app to redraw before we wake the screen 
        # chomper_app.invalidate()
        # chomper_app.foreground()

        # wake the backlight
        self.set_backlight_level(0)
        self.axp.enablePower(axp202c.AXP202_LDO2)
        for i in range(0, self.backlight_percent):
            self.set_backlight_level(i)
            time.sleep_ms(4)
        
        # Clear any previous touch events
        self.touch.reset()

        self.state = CHOMPER_STATE_AWAKE
        self.defer_sleep()

    def defer_sleep(self):
        '''
        Defer automatic sleep for set period of time, usually based on user input or some other valid reason
        '''
        self.next_sleep_time_ms = time.ticks_ms() + AWAKE_TIME_MS

    def failsafe(self):
        '''
        Special failsafe mode for when some python is not loaded on watch just yet
        '''
        print("\n\n!!!!FAILSAFE MODE!!!!\n")
        print("I am missing files and need an update")
        print("\tpip3 install adafruit-ampy")
        print("\twget https://mattdamon.app/data/update.mpy")
        print("\tampy run update.mpy")
        print("\nI like this WIFI:")
        print("\tSSID: " + config.config[config.KEY_WIFI_SSID])
        print("\tPWD: " + config.config[config.KEY_WIFI_PWD])
        print("\n!!!!FAILSAFE MODE!!!!\n\n")
        self.display.fill_rect(0, 0, 240, 240, st7789.RED)
        self.display.text(font, "UPDATE ME! =)", 0,60,st7789.WHITE, st7789.RED)
        self.display.text(font, "I am missing components", 0,70,st7789.WHITE, st7789.RED)
        self.display.text(font, "$ pip3 install adafruit-ampy", 0, 110, st7789.WHITE, st7789.RED)
        self.display.text(font, "$ ampy run update.mpy", 0,120,st7789.WHITE, st7789.RED)
        self.display.text(font, "Someday will be automatic :-)", 0,130,st7789.WHITE, st7789.RED)
        self.display.text(font, "I like this WIFI:", 0,150,st7789.WHITE, st7789.RED)
        self.display.text(font, "SSID: "+config.config[config.KEY_WIFI_SSID], 10,160,st7789.WHITE, st7789.RED)
        self.display.text(font, "PWD: "+config.config[config.KEY_WIFI_PWD], 10,170,st7789.WHITE, st7789.RED)
        while True:
            pass

    def boot(self):
        '''
        Perform watch bootup
        '''
        build = chomper_c.version()
        idf = chomper_c.idf_version()
        upy = os.uname()[2]
        print("=======================================================================")
        print("Booting Chomper", build,
              "[ESP-IDF="+idf, "Micropython="+upy+"]")
        print("Hostname: " + self.unique_id())
        print("=======================================================================")

        machine.freq(160000000)

        BLOCK = 20
        l = logo.data() # Get memoryview of logo from flash
        l_index = 0
        slice_size_bytes = 240 * 2 * BLOCK
        for y in range(0, 240, BLOCK):
            b = l[l_index:(l_index + slice_size_bytes)]
            l_index = l_index + slice_size_bytes
            self.display.blit_buffer(b, 0, y, 240, BLOCK)

        # Init apps
        chomper_app.register_apps(self)
        if len(chomper_app.apps) == 0:
            print("******************************************")
            print("CHOMPER: No apps registered")
            print("CHOMPER will enter failsafe mode shortly!")
            print("******************************************")            
            self.failsafe()

        r=40
        s=2
        c=int(240/s)
        pixels = [0] * c
        vel = [0] * c
        for x in range(0,c):
            pixels[x] = -random.randint(0, r)
            vel[x] = random.randint(1, 10) / 4

        for i in range(0,240+r):
            drawing = False
            for x in range(0,c):
                if pixels[x] >= 0 and pixels[x] < 240:
                    drawing = True
                    self.display.fill_rect(x*s, int(pixels[x]), s, s, random.randint(0,0xFFFF))
                # Erase behind pixel
                if pixels[x] >= s:
                    self.display.fill_rect(x*s, 0, 2, min(int(pixels[x])-s, 240), 0x0000)
                pixels[x] += vel[x]
                vel[x] *= 1.2
            if not drawing:
                break

        #Clear screen
        self.display.fill_rect(0, 0, 240, 240, st7789.BLACK)

        first_run = False
        try:
            os.stat("FIRSTRUN")
            first_run = True
        except:
            first_run = False

        if first_run:
            # Color increment per pct battery below target SOC
            tgt = 60
            hw = tgt / 2
            inc = 255 / hw

            wifi.do_work(self)

            while(self.axp.isVBUSPlug()):
                pct = self.axp.getBattPercentage()
                c = st7789.color565(0, 255, 0)
                if pct < hw:
                    g = int(pct * inc)
                    c = st7789.color565(255,g,0)
                elif pct < tgt:
                    r = 255 - int(((pct - hw) * inc))
                    c = st7789.color565(r,255,0)
                self.display.fill_rect(0,0,240,240,c)
                self.display.text(font, "SoC:{}".format(pct), 0, 20, st7789.BLACK, c)
                time.sleep(1)
            os.remove("FIRSTRUN")
            # time.sleep(2)
            # self.axp.shutdown()

    def loop(self):
        '''
        Primary UI loop, handle deep sleep and wakeup in a rational manner
        '''
        gc.collect()
        machine.freq(80000000)
        self.defer_sleep() #Keep screen awake for minimum time
        offset = config.config[config.KEY_OFFSET]

        while True:

            # Reset step counter at 2 am
            dt = self.pcf_rtc.datetime()
            hr = dt[4]
            min = dt[5]
            if hr == (2 - offset) and min == 0:
                self._sleep()
                steps = self.accel.step_count()
                self.accel.reset_steps()
                ninja = chomper_app.get_app_by_name("Ninja")
                if ninja:
                    ninja.give_steps(steps)
                lightsleep(60*1000)

            # Light sleep since we need appearance of bluetooth in the background
            # ESP32 Tech manual section 31.3.9 indicates light sleep around 800uA but **no radio**
            # wake time is around 1ms
            # Deep sleep is 6.5uA but loses CPU context, save deep sleep for more advanced power
            # saving (accelermeter inactive???)
            if self.state == CHOMPER_STATE_SLEEP:
                # machine.freq(80000000)
                # Low power sleep briefly if not plugged in
                if not self.axp.isVBUSPlug():
                    lightsleep(600)

                wifi.do_work(self)
                # Keeping this enabled crashes firmware :/
                if self.accel.tilted():
                    print("CHOMPER: Wake on tilt")
                    self._wake()

                # Need to be awake for BLE scanners to see us (briefly)
                time.sleep(0.01)

                # machine.freq(160000000)
            elif self.state == CHOMPER_STATE_AWAKE:
                chomper_app.foreground()
                # Automatic sleep
                if time.ticks_ms() > self.next_sleep_time_ms:
                    self._sleep()

    def unique_id(self):
        '''
        Get a unique identifier string for this badge
        '''
        return "chomper-" + ubinascii.hexlify(machine.unique_id()).decode('utf-8')


    def vibrate(self, delay=0.02):
        self.motor.value(1)
        time.sleep(delay)
        self.motor.value(0)