import chomper_c
import chomper_config as config
import machine
import micropython
from micropython import const
import network
from ntptime import settime
import sys
import time
import urequests as requests
import utime

# 24 hour delay
CONNECT_DELAY_MS = const(1000 * 60 * 60 * 12)

hostname = "CHOMPER"
# Initial sync in 15 minutes
next_connect_time = 0
station = network.WLAN(network.STA_IF)

# Finite state machine
STATE_IDLE = const(0)
STATE_CONNECTING = const(1)
STATE_RUNNING = const(2)
state = STATE_IDLE

def _connect():
    global station, hostname, next_connect_time
    ssid = config.config[config.KEY_WIFI_SSID]
    pwd = config.config[config.KEY_WIFI_PWD]
    print("WIFI Connecting", ssid)
    station.active(True)
    # station.config(dhcp_hostname=hostname)

    try:
        scan = station.scan()

        known_network_nearby = False
        for result in scan:
            if result[0].decode("ASCII") == ssid:
                known_network_nearby = True

        if known_network_nearby == False:
            print("WIFI: No known networks nearby")
            # Try again in 6 hours
            next_connect_time = time.ticks_ms() + (1000 * 60 * 60 * 6)
            return

        station.connect(ssid, pwd)
    except Exception as e:
        print("WIFI: Unable to scan and connect to wifi")
        sys.print_exception(e)
    

def _disconnect():
    global station
    station.disconnect()
    station.active(False)
    print("WIFI Disconnected")

def set_hostname(_hostname):
    global hostname
    hostname = _hostname


def do_work(_watch):
    global state, station, watch, next_connect_time
    watch = _watch

    if state == STATE_IDLE:
        if time.ticks_ms() < next_connect_time:
            return
        state = STATE_CONNECTING
        _connect()
    elif state == STATE_CONNECTING:
        if station.isconnected():
            print("WIFI Connected", station.ifconfig())
            state = STATE_RUNNING
            print("WIFI NTP")
            task_ntp()
            _disconnect()  
    elif state == STATE_RUNNING:
        next_connect_time = time.ticks_ms() + CONNECT_DELAY_MS

def isconnected():
    global station
    return station.isconnected()

def task_ntp():
    global watch
    try:
        # Get time from NTP
        dt = settime()
        year = dt[0] % 100
        month = dt[1]
        date = dt[2]
        hour = dt[4]
        minute = dt[5]
        second = dt[6]

        machine.RTC().datetime(dt)
        watch.pcf_rtc.write_all(
            seconds=second, minutes=minute, hours=hour, day=date, month=month, year=year)

        print("NTP complete")
        print("NTP", dt)
        print("machine RTC",  machine.RTC().datetime())
        print("UPY RTC", utime.localtime())
        print("PCF RTC", watch.pcf_rtc.datetime())
    except Exception as e:
        print("WIFI: Unable to get current NTP TIME", e)