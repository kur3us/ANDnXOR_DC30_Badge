import bluetooth
import chomper
import chomper_config as config
from micropython import const
import struct
import sys
import ubinascii

ADV_TYPE_FLAGS = const(0x01)
ADV_TYPE_NAME = const(0x09)
ADV_TYPE_UUID16_COMPLETE = const(0x3)
ADV_TYPE_UUID32_COMPLETE = const(0x5)
ADV_TYPE_UUID128_COMPLETE = const(0x7)
ADV_TYPE_UUID16_MORE = const(0x2)
ADV_TYPE_UUID32_MORE = const(0x4)
ADV_TYPE_UUID128_MORE = const(0x6)
ADV_TYPE_APPEARANCE = const(0x19)
ADV_TYPE_MANUFACTURER_DATA = const(0xFF)

# GAP scan advertisement types (returned in scan results)
SCAN_ADV_TYPE_IND = const(0x00) #connectable and scannable undirected advertising
SCAN_ADV_TYPE_DIRECT_IND = const(0x01)  #connectable directed advertising
SCAN_ADV_TYPE_SCAN_IND = const(0x02) #scannable undirected advertising
SCAN_ADV_TYPE_NONCONN_IND = const(0x03) #non-connectable undirected advertising
SCAN_ADV_TYPE_SCAN_RSP = const(0x04) #scan response



IRQ_CENTRAL_CONNECT = const(1)
IRQ_CENTRAL_DISCONNECT = const(2)
IRQ_GATTS_WRITE = const(3)
IRQ_GATTS_READ_REQUEST = const(4)
IRQ_SCAN_RESULT = const(5)
IRQ_SCAN_DONE = const(6)
IRQ_PERIPHERAL_CONNECT = const(7)
IRQ_PERIPHERAL_DISCONNECT = const(8)
IRQ_GATTC_SERVICE_RESULT = const(9)
IRQ_GATTC_SERVICE_DONE = const(10)
IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
IRQ_GATTC_DESCRIPTOR_DONE = const(14)
IRQ_GATTC_READ_RESULT = const(15)
IRQ_GATTC_READ_DONE = const(16)
IRQ_GATTC_WRITE_DONE = const(17)
IRQ_GATTC_NOTIFY = const(18)
IRQ_GATTC_INDICATE = const(19)
IRQ_GATTS_INDICATE_DONE = const(20)
IRQ_MTU_EXCHANGED = const(21)
IRQ_L2CAP_ACCEPT = const(22)
IRQ_L2CAP_CONNECT = const(23)
IRQ_L2CAP_DISCONNECT = const(24)
IRQ_L2CAP_RECV = const(25)
IRQ_L2CAP_SEND_READY = const(26)
IRQ_CONNECTION_UPDATE = const(27)
IRQ_ENCRYPTION_UPDATE = const(28)
IRQ_GET_SECRET = const(29)
IRQ_SET_SECRET = const(30)

IRQ_ERROR = const(0xFF)

GATTS_NO_ERROR = const(0x00)
GATTS_ERROR_READ_NOT_PERMITTED = const(0x02)
GATTS_ERROR_WRITE_NOT_PERMITTED = const(0x03)
GATTS_ERROR_INSUFFICIENT_AUTHENTICATION = const(0x05)
GATTS_ERROR_INSUFFICIENT_AUTHORIZATION = const(0x08)
GATTS_ERROR_INSUFFICIENT_ENCRYPTION = const(0x0f)

PASSKEY_ACTION_NONE = const(0)
PASSKEY_ACTION_INPUT = const(2)
PASSKEY_ACTION_DISPLAY = const(3)
PASSKEY_ACTION_NUMERIC_COMPARISON = const(4)

ANDNXOR = const(0x49E)

# Ninja service/char constants
NINJA_UUID = bluetooth.UUID(0x1337)
NINJA_INFO_CHAR = (bluetooth.UUID(0x1337), bluetooth.FLAG_READ,)
NINJA_ATK_CHAR = (bluetooth.UUID(0xDC30), bluetooth.FLAG_READ | bluetooth.FLAG_WRITE | bluetooth.FLAG_NOTIFY,)

class BLE:
    def __init__(self):
        '''
        Setup Bluetooth, start advertising etc
        '''
        self.bt = bluetooth.BLE()
        try:
            self.bt.active(True)
        except Exception as e:
            print("CHOMPER: Error while activating Bluetooth radio, trying again", e)
            try:
                self.bt.active(True)
            except Exception as e:
                print("CHOMPER: Second attempt failed, no Bluetooth today :(", e)
                return

        # Setup callback for bluetooth events
        self.bt.irq(self._irq)

        print("Bluetooth radio activated")
        self._manufacturer = None

        # Register Services
        NINJA_SERVICE = (NINJA_UUID, (NINJA_INFO_CHAR, NINJA_ATK_CHAR),)
        ((self.ninja_info_handle, self.ninja_atk_handle,), ) = self.bt.gatts_register_services((NINJA_SERVICE,))
        self.bt.gatts_write(self.ninja_info_handle, struct.pack("<h", int(0)))
        self.bt.gatts_write(self.ninja_atk_handle, struct.pack("<h", int(0)))

        self.advertise()
        self.scanning = False
        self.connected = False
        self._connections = set()
        self._callbacks = []


    def advertise(self):
        name = config.config[config.KEY_NAME]
        payload = self._advertising_payload(name=name[:12], manufacturer=self._manufacturer)
        self.bt.gap_advertise(100000, adv_data=payload)

    # Generate a payload to be passed to gap_advertise(adv_data=...).
    def _advertising_payload(self, limited_disc=False, br_edr=False, name=None, services=None, appearance=0, manufacturer=None):
        payload = bytearray()

        def _append(adv_type, value):
            nonlocal payload
            payload += struct.pack("BB", len(value) + 1, adv_type) + value

        _append(
            ADV_TYPE_FLAGS,
            struct.pack("B", (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04)),
        )

        if name:
            _append(ADV_TYPE_NAME, name)

        if services:
            for uuid in services:
                b = bytes(uuid)
                if len(b) == 2:
                    _append(ADV_TYPE_UUID16_COMPLETE, b)
                elif len(b) == 4:
                    _append(ADV_TYPE_UUID32_COMPLETE, b)
                elif len(b) == 16:
                    _append(ADV_TYPE_UUID128_COMPLETE, b)

        # See org.bluetooth.characteristic.gap.appearance.xml
        if appearance:
            _append(ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))

        # Add manufacturer specific data
        m_buffer = struct.pack("H", ANDNXOR)
        if manufacturer:
            m_buffer = m_buffer + manufacturer
        _append(ADV_TYPE_MANUFACTURER_DATA, m_buffer)


        return payload

    def _irq(self, event, data):
        if event == IRQ_CENTRAL_DISCONNECT:
            self.advertise()

        for cb in self._callbacks:
            # try:
            cb(event, data)
            # except Exception as e:
            #     print("LIB_BLE: Invalid BLE callback, DFIU next time")
            #     sys.print_exception(e)
            #     cb(IRQ_ERROR, None)

    def decode_field(self, payload, adv_type):
        i = 0
        result = []
        while i + 1 < len(payload):
            if payload[i + 1] == adv_type:
                result.append(payload[i + 2 : i + payload[i] + 1])
            i += 1 + payload[i]
        return result


    def decode_name(self, payload):
        n = self.decode_field(payload, ADV_TYPE_NAME)
        return str(n[0], "utf-8") if n else ""

    def decode_manufacturer_data(self, payload):
        mdata = self.decode_field(payload, ADV_TYPE_MANUFACTURER_DATA)
        if len(mdata) == 0:
            return None
        else:
            return mdata[0]

    def decode_services(self, payload):
        services = []
        for u in self.decode_field(payload, ADV_TYPE_UUID16_COMPLETE):
            services.append(bluetooth.UUID(struct.unpack("<h", u)[0]))
        for u in self.decode_field(payload, ADV_TYPE_UUID32_COMPLETE):
            services.append(bluetooth.UUID(struct.unpack("<d", u)[0]))
        for u in self.decode_field(payload, ADV_TYPE_UUID128_COMPLETE):
            services.append(bluetooth.UUID(u))
        return services

    # Determine if bluetooth is being used (connected or scanning)
    def is_inuse(self):
        # return (self.scanning or self.connected)
        return False

    def register_callback(self, callback):
        self._callbacks.append(callback)
        print("LIB_BLE: Registered callback", str(callback), len(self._callbacks), "registered")