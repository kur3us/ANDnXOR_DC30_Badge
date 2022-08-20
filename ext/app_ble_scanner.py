import chomper_app as app
import font_digital16 as small_font
import lib_ble
from micropython import const
import ubinascii
import ui
from ui import *

STATE_IDLE = const(0)
STATE_SCANNING = const(1)
STATE_CONNECTING = const(2)
STATE_RESULT = const(3)

CLASSNAME = "BLEScannerApp"

class BLEScannerApp():
    APP_NAME = "BLE App"
    WEIGHT = 50
    MAX_RESULTS = 9

    def __init__(self, _watch):
        self._state = STATE_IDLE
        self.watch = _watch
        self._output = UITextbox(self.watch, small_font, app.APP_LEFT+10, app.APP_TOP+10, app.APP_WIDTH, app.APP_HEIGHT, "Testing\n1\n2\n3", ui.PEACH)
      
        # Register for bluetooth callbacks
        self.watch.ble.register_callback(self._ble_callback)
        self.bt = self.watch.ble.bt

        self._state = STATE_IDLE
        self._output.text("Touch screen to scan")
        self._valid = False
        self.counter = 0

        # Reset peer and ble state
        self._reset()

    def _reset(self):
        self.counter = 0

        # Peer address
        self._peer_addr = None
        self._peer_addr_type = None
        self._peer_addr_str = ""
        self._peer_rssi = -999

        # Local storage of handles etc for managing BLE connection
        self._handle = -1
        self._start_handle = -1
        self._end_handle = -1
        self._chr_handle = -1

    def _redraw(self):
        #ui.fill()
        ui.fill_rgb("/bg_ble_scanner.rgb")
        self._output.draw()
        ui.push(self.watch)
        self._valid = True

    def init(self):
        self.invalidate()

    def invalidate(self):
        self._valid = False

    def foreground(self):
        if not self._valid:
            self._redraw()

    def _ble_callback(self, event, data):
        """
        This is called from our helper BLE library which does almost nothing. 
        Make sure to register your callback and it will feed BT events directly
        to your callback function. 

        NOTE: Several apps may be receiving the same callbacks. So try to ignore
        those not meant for your app.

        The code below will attempt to connect to another BLE device, query services,
        and read all characteristics. If it works, you're lucky. It doesn't have much
        of a use case other than provide example code with no purpose. It's up to you
        to make something interesting with it, like hack a vodka bottle or something.
        """

        # Scan result event occurs for every result from the BLE scanner, process them 
        # individually, find what you're looking for, save for when scan results are 
        # done to do anything with them
        if event == lib_ble.IRQ_SCAN_RESULT:
            if self._state == STATE_SCANNING:
                if self.counter < self.MAX_RESULTS:
                    addr_type = data[0]
                    addr = self._addr = bytes(data[1])
                    addr_str = str(ubinascii.hexlify(bytes(addr), b':'), 'utf-8')
                    rssi = data[3]
                    payload = data[4]
                    mdata = self.watch.ble.decode_manufacturer_data(payload)
                    name = self.watch.ble.decode_name(payload)

                    # If first result, save address for connection later
                    if self._peer_rssi < rssi:
                        self._peer_addr_type = addr_type
                        self._peer_addr = addr
                        self._peer_addr_str = addr_str
                        self._peer_rssi = rssi
                    
                    payload = data[4]
                    self._output.append(addr_str + " " + str(rssi) + " " + name)
                    self.invalidate()
                    self.counter += 1
                    self.watch.defer_sleep()
                    print("BLE APP: Device found: {} Name: '{}' RSSI: {}".format(addr_str, name, str(rssi)))

        # Scan done event occurs after the scan is complete. This is when you should 
        # connect to or show something to the user, if you want. We aren't the boss
        # of you.
        elif event == lib_ble.IRQ_SCAN_DONE:
            if self._state != STATE_SCANNING:
                return

            if self.counter > 0:
                print("BLE APP: Scan found {} device(s)".format(self.counter))
                self._output.append("")
                self._output.append("Touch to interogate closest")
            else:
                print("BLE APP: No scan results :(")
                self.state = STATE_IDLE
                self._reset()
            self.invalidate()
            self.watch.defer_sleep()

        # Peripherical connect event occurs after successful connection. In this example
        # we are acting like the central device. Note, we kick off serice discovery here 
        # on the peripheral we connected to
        elif event == lib_ble.IRQ_PERIPHERAL_CONNECT:
            if self._state == STATE_CONNECTING:
                print("BLE APP: Peripheral Connected")
                self._handle, _, _ = data
                self.bt.gattc_discover_services(self._handle)
                self.watch.defer_sleep()

        # Disconnect occurs when, gasp, the we disconnect either intentionally or otherwise.
        # Some retail devices will forcefully disconnect if they don't trust us.
        elif event == lib_ble.IRQ_PERIPHERAL_DISCONNECT:
            if self._handle >= 0 or self._state == STATE_CONNECTING:
                print("BLE APP: Peripheral Disconnected")
                self._state = STATE_RESULT
                self.invalidate()

        # Central service result callback. This gets called for each service as it's discovered
        # If there is a particular service you are interested in, query for the UUID here
        # then save the start/end handles for that service to be used later
        elif event == lib_ble.IRQ_GATTC_SERVICE_RESULT:
            conn_handle, start_handle, end_handle, uuid = data

            # Ignore connections not for us
            if conn_handle != self._handle:
                return

            print("BLE APP: Service Result: handles: {},{} UUID: {}".format(start_handle, end_handle, str(uuid)))
            self._start_handle = start_handle
            self._end_handle = end_handle
            self._output.append("SVC:" + str(uuid))
            self.invalidate()
            self.watch.defer_sleep()
 
        # Service done event occurs when all services are discovered. This is a good time to 
        # discover characteristics for interesting service(s) we found previously.
        elif event == lib_ble.IRQ_GATTC_SERVICE_DONE:
            if self._start_handle >= 0 and self._end_handle >= 0:
                print("BLE APP: Found at least one service, reading characteristics from service with handles {},{}".format(self._start_handle, self._end_handle))
                self.bt.gattc_discover_characteristics(
                    self._handle, self._start_handle, self._end_handle)
            else:
                # Disconnect if no serivces found
                print("BLE APP: No services found, disconnecting")
                self._output.append("No services found")
                try:
                    self.bt.gap_disconnect(self._handle)
                except:
                    self._state = STATE_RESULT
                    print("BLE APP: Error while disconnecting")
                self.invalidate()
  
        # Each characteristic we discovered earlier will come here. We can do lots of interesting
        # things if the characteristic is one we want to mess with. In this example we are simply
        # reading it, but we can also write to the characteristic. For more advanced things like
        # notify etc go read some BLE documentation.
        elif event == lib_ble.IRQ_GATTC_CHARACTERISTIC_RESULT:
            conn_handle, def_handle, value_handle, properties, uuid = data
            # Ignore connections not for us
            if conn_handle != self._handle:
                return

            print("BLE APP: Characteristic result for handles {},{} UUID: {} handle:{}".format(self._start_handle, self._end_handle, str(uuid), value_handle))
            self._chr_handle = value_handle

        elif event == lib_ble.IRQ_GATTC_CHARACTERISTIC_DONE:
            if self._handle >= 0 and self._chr_handle >= 0:
                print("BLE APP: Characteristic discovery done, reading from characteristic handle {}".format(self._chr_handle))
                self.bt.gattc_read(self._handle, self._chr_handle)

        # Occurs when characteristic reads are done
        elif event == lib_ble.IRQ_GATTC_READ_DONE:
            if self._handle >= 0:
                print("BLE APP: GATTC read complete, Disconnecting")
                self.bt.gap_disconnect(self._handle)

        # Results form any reads go here. Simply get the data and do whatever you want.
        elif event == lib_ble.IRQ_GATTC_READ_RESULT:
            conn_handle, char_handle, packet = data
            if self._handle == conn_handle and self._chr_handle == char_handle:
                p_str = str(ubinascii.hexlify(bytes(packet), b':'), 'utf-8')
                print("BLE APP: Characteristic Read Result for handle {}: {}".format(self._chr_handle, p_str))
                self._output.append("D:" + p_str)

    def touch(self, x, y):
        if self._state == STATE_IDLE:
            self._state = STATE_SCANNING
            self._output.text("Scanning")
            self._counter = 0
            self.invalidate()

            # We are using the standard uPY BT library. Read their docs for syntax
            try:
                self.bt.gap_scan(2000, 30000, 30000)
            except Exception as e:
                print("BLE APP: Unable to scan:", e)
                self._state = STATE_IDLE
                self._output.text("Scanning failed, try again")
                self.invalidate()
        elif self._state == STATE_SCANNING:
            # If we have results and screen touched, connect to first result
            if self.counter > 0:
                self._state = STATE_CONNECTING
                addr_str = ubinascii.hexlify(self._peer_addr).decode("utf-8")
                self._output.text("Connecting to " + addr_str)
                print("BLE APP: Connecting to", addr_str)
                self.bt.gap_connect(self._peer_addr_type, self._peer_addr)
            else:
                self._state = STATE_IDLE
                self._output.text("Touch screen to scan")
            self.invalidate()
        elif self._state == STATE_RESULT:
            self._reset()
            self._state = STATE_IDLE
            self._output.text("Touch screen to scan")
            self.invalidate()
        