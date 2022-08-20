import chomper_app
from collections import OrderedDict
from ucryptolib import aes
import lib_ble
import machine
from micropython import const
import font_digital16 as small_font
import font_digital32 as dfont
import random
import struct
import time
import ubinascii
import ui
from ui import UIButton

CLASSNAME = "NinjaApp"

PAGE_OVERVIEW = const(0)
PAGE_SCANNING = const(1)
PAGE_SCAN_RESULT = const(2)
PAGE_DETAILS = const(3)
PAGE_RESULT = const(4)
PAGE_ERROR = const(0xFF)
FILENAME = "/ninja.dat"
CBC = const(2)
MAX_NEARBY = const(3)

def byte_xor(ba1, ba2):
    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])


class NinjaApp:
    APP_NAME = "Ninja"
    WEIGHT = 55

    def __init__(self, _watch):
        self.watch = _watch
        self.selected = 1
        self.margin = 2
        self.badge_top_gfx_offset = 3
        self.badge_top = chomper_app.APP_TOP + dfont.HEIGHT + self.badge_top_gfx_offset
        self.badge_height = dfont.HEIGHT + self.margin
        self.page = PAGE_OVERVIEW
        self.nearby = {}
        self.scan_button = UIButton(self.watch, 0, self.badge_top, text='Scan')
        self.scan_button._x = int((240 - self.scan_button._width) / 2)
        self.scan_button._bg = ui.INDIGO
        self.scan_button._fg = ui.PEACH
        self.back_button = UIButton(self.watch, 21, 176, text='<----')
        self.back_button._bg = ui.INDIGO
        self.back_button._fg = ui.PEACH
        self.action_button = UIButton(self.watch, 148, 176, text='AT&K')
        self.action_button._bg = ui.INDIGO
        self.action_button._fg = ui.PEACH

        # Register for bluetooth callbacks
        self.watch.ble.register_callback(self._bt_callback)
        self.bt = self.watch.ble.bt
        
        # Ninja connection tracking
        self._handle = -1
        self._start_handle = -1
        self._end_handle = -1
        self._atk_handle = -1
        self._atk_in_progress = False

        # Game data
        self._reset()

        # Get some data for special things
        self.__some_data = b"m@77yd@3m0NrOxxX"
        with open("/bg_ninja.rgb", 'rb') as file:
            file.seek(0x2170)
            self.__some_data = file.read(16)  # private key for saving state
            self.__rgb_data = file.read(16)  # private key for GAP
            id = struct.pack("6sHHHHH", machine.unique_id(),
                             0xAAAA, 0xBBBB, 0xCCCC, 0xDDDD, 0xEEEE)
            self.__some_data = byte_xor(self.__some_data, id)
            file.close()

        # Generate GAP OTP
        crypto = aes(self.__rgb_data, CBC, self.__rgb_data)
        self.__gapotp = crypto.encrypt(self.__rgb_data)

        # Load state
        self._load()
        self._update_ble()
        self.watch.ble.advertise()

    def _redraw(self):
        ui.fill_rgb("/bg_ninja.rgb")

        y = self.badge_top
        if self.page == PAGE_OVERVIEW:
            level_str = "Level: {}".format(self.__level)
            xp_str = "XP: {}".format(self.__xp)
            wins_str = "W/L: {}/{}".format(self.__wins, self.__losses)
            ui.draw_text_center(self.watch, dfont, level_str, y, ui.PEACH)
            y = y + dfont.HEIGHT + self.margin
            ui.draw_text_center(self.watch, dfont, xp_str, y, ui.LIGHT_GRAY)
            y = y + dfont.HEIGHT + self.margin
            ui.draw_text_center(self.watch, dfont, wins_str, y, ui.LIGHT_GRAY)
            y = y + dfont.HEIGHT * 2 + self.margin

            self.scan_button._y = 176
            self.scan_button.draw()
        elif self.page == PAGE_SCANNING:
            ui.draw_text_center(self.watch, dfont, "Scanning", y, ui.PEACH)
        elif self.page == PAGE_SCAN_RESULT:
            i = 0
            for addr in self.nearby:
                nearby_badge = self.nearby[addr]
                ui.draw_text_center(self.watch, dfont,
                                    nearby_badge["name"], y, ui.PEACH)
                y = y + dfont.HEIGHT + self.margin
                i += 1
                
                #Only draw first n nearby
                if i >= MAX_NEARBY:
                    break
            self.back_button.draw()

        elif self.page == PAGE_DETAILS:
            if self.selected == None:
                self.page = PAGE_OVERVIEW
                return

            ui.draw_text_center(self.watch, dfont,
                                self.selected["name"], y, ui.PEACH)
            y = y + dfont.HEIGHT + self.margin
            ui.draw_text_center(self.watch, dfont, "Level: " +
                                str(self.selected["level"]), y, ui.LIGHT_GRAY)

            self.back_button.draw()
            self.action_button.draw()

        elif self.page == PAGE_RESULT:
            ui.draw_text_center(self.watch, dfont,
                                self.selected["name"], y, ui.PEACH)
            y = y + dfont.HEIGHT + self.margin + 5

            if self.__success:
                ui.draw_text_center(self.watch, dfont, "Success!", y, ui.GREEN)
                y = y + dfont.HEIGHT + self.margin
                ui.draw_text_center(self.watch, dfont,
                                    "XP: " + str(self.__xp), y, ui.LIGHT_GRAY)
                y = y + dfont.HEIGHT + self.margin
                ui.draw_text_center(self.watch, dfont,
                                    "Level: " + str(self.__level), y, ui.LIGHT_GRAY)
            else:
                ui.draw_text_center(self.watch, dfont, "Failed :(", y, ui.RED)

            self.back_button.draw()

        elif self.page == PAGE_ERROR:
            ui.draw_text_center(self.watch, dfont,
                                "Error :(", y, ui.RED)
            self.back_button.draw()

        ui.push(self.watch)
        # Avoid unnecessary redraws
        self._valid = True

    def _bt_callback(self, event, data):
        if event == lib_ble.IRQ_SCAN_RESULT:
            if self.page != PAGE_SCANNING:
                return

            addr_type = data[0]
            addr = self._addr = bytes(data[1])
            rssi = data[3]
            payload = data[4]
            mdata = self.watch.ble.decode_manufacturer_data(payload)
            name = self.watch.ble.decode_name(payload)
            if len(name) == 0:
                return

            # only interested in devices with manufacturer data
            if not mdata:
                return

            mdata = bytes(mdata)
            if len(mdata) < 4:
                return

            # parse manufacturer id
            mid = mdata[0] | (mdata[1] << 8)

            if mid != lib_ble.ANDNXOR:
                return

            # Parse ninja data
            level = mdata[2]
            avatar = mdata[3]

            self.nearby[addr] = {
                "addr": addr,
                "addr_type": addr_type,
                "name": name,
                "rssi": rssi,
                "level": level,
                "avatar": avatar,
            }

            self.watch.defer_sleep()
        elif event == lib_ble.IRQ_SCAN_DONE:
            if self.page != PAGE_SCANNING:
                return

            # Sort final results
            self.nearby = OrderedDict(sorted(self.nearby.items(), key=lambda x: x[1]['rssi'], reverse=True))

            self.page = PAGE_SCAN_RESULT
            self.invalidate()
            self.watch.defer_sleep()
            # print("NINJA Scan Done")
        elif event == lib_ble.IRQ_PERIPHERAL_CONNECT:
            if self.page != PAGE_DETAILS:
                return
            # print("NINJA: Peripheral Connected")
            self._handle, _, _ = data
            self.bt.gattc_discover_services(self._handle)
            self.watch.defer_sleep()
        elif event == lib_ble.IRQ_PERIPHERAL_DISCONNECT:
            if self._handle < 0:
                return
            # print("NINJA: Peripheral Disconnected")
            self._handle = -1
            self._start_handle = -1
            self._end_handle = -1
            self._atk_handle = -1
            # Pre mature disconnection
            if self._atk_in_progress:
                self.page = PAGE_ERROR
                self.invalidate()
        elif event == lib_ble.IRQ_CENTRAL_CONNECT:
            # print("NINJA: Central Connected")
            pass
        elif event == lib_ble.IRQ_CENTRAL_DISCONNECT:
            # print("NINJA: Central Disconnected")
            pass
        elif event == lib_ble.IRQ_GATTC_SERVICE_RESULT:
            conn_handle, start_handle, end_handle, uuid = data

            # Ignore connections not for us
            if conn_handle != self._handle:
                return
            # print("NINJA: SERVICE", data)
            if uuid == lib_ble.NINJA_UUID:
                self._start_handle = start_handle
                self._end_handle = end_handle
                # print("\tNINJA: Ninja service found",
                #       self._start_handle, self._end_handle)

        elif event == lib_ble.IRQ_GATTC_SERVICE_DONE:
            # Ignore other BLE events
            if self.page != PAGE_DETAILS:
                return
            if self._start_handle >= 0 and self._end_handle >= 0:
                # print("NINJA: Service Result DONE")
                self.bt.gattc_discover_characteristics(
                    self._handle, self._start_handle, self._end_handle)
                self.watch.defer_sleep()
            else:
                # print("NINJA: Did not find any valid services. Disconnecting")
                self.page = PAGE_ERROR
                self.invalidate()
                self._reset()

        elif event == lib_ble.IRQ_GATTC_CHARACTERISTIC_RESULT:
            conn_handle, def_handle, value_handle, properties, uuid = data
            # Ignore connections not for us
            if conn_handle != self._handle:
                return

            if uuid == lib_ble.NINJA_ATK_CHAR[0]:  # 0xDC30
                self._atk_handle = value_handle

            self.watch.defer_sleep()
            # print("NINJA: Characteristic result", data)

        elif event == lib_ble.IRQ_GATTC_CHARACTERISTIC_DONE:
            """
            Write to attack characteristic
            """
            if self._handle >= 0 and self._atk_handle >= 0:
                # print("NINJA: Characteristic result done")
                self.atk = self._attack_strength()
                r1 = random.getrandbits(32)
                r2 = random.getrandbits(32)
                r3 = random.getrandbits(32)
                packet = struct.pack(
                    "LLHHL", r1, r2, self.__level, self.atk, r3)
                packet = byte_xor(packet, self.__gapotp)
                self.bt.gatts_notify(self._handle, self._atk_handle, packet)
                time.sleep(0.5)
                self.bt.gattc_read(self._handle, self._atk_handle)
                self.watch.defer_sleep()

            # This causes issues with other BLE clients 
            # else:
            #     print("NINJA: No valid BLE services found")
            #     self.bt.gap_disconnect(self._handle)
            #     self.page = PAGE_ERROR
            #     self.invalidate()
            #     self._reset()

        elif event == lib_ble.IRQ_GATTC_READ_DONE:
            pass

        elif event == lib_ble.IRQ_GATTC_READ_RESULT:
            conn_handle, char_handle, packet = data
            if self._handle == conn_handle and self._atk_handle >= char_handle:
                if len(packet) == 16:
                    packet = byte_xor(packet, self.__gapotp)
                    _, _, attacker_strength, defender_strength, _ = struct.unpack(
                        "LLHHL", packet)
                    if attacker_strength == self.atk:
                        self._do_battle(attacker_strength,
                                        defender_strength, self.selected['level'], True)
                        self.page = PAGE_RESULT
                    else:
                        # print("NINJA: Invalid attack response packet (mismatch)")
                        self.page = PAGE_ERROR
                else:
                    # print("NINJA: Response packet incorrect length")
                    self.page = PAGE_ERROR
                self.bt.gap_disconnect(self._handle)
                self.watch.defer_sleep()
                self._atk_in_progress = False
                self.invalidate()

        elif event == lib_ble.IRQ_GATTC_NOTIFY:
            """
            Receive an attack packet
            """
            conn_handle, _, packet = data
            if len(packet) != 16:
                # print("NINJA: Invalid packet length")
                self.bt.gap_disconnect(conn_handle)
                return
 
            # decrypt packet
            packet = byte_xor(packet, self.__gapotp)
            _, _, attacker_level, attacker_strength, _ = struct.unpack(
                "LLHHL", packet)
            atk = self._attack_strength()
 
            # Build response packet
            r1 = random.getrandbits(32)
            r2 = random.getrandbits(32)
            r3 = random.getrandbits(32)
            rpacket = struct.pack("LLHHL", r1, r2, attacker_strength, atk, r3)
            # Encrypt response
            rpacket = byte_xor(rpacket, self.__gapotp)
 
            self.bt.gatts_write(self.watch.ble.ninja_atk_handle, rpacket)
            self._do_battle(atk, attacker_strength, attacker_level, False)

        elif event == lib_ble.IRQ_ERROR:
            print("IRQ_ERROR")
            if self._handle >= 0:
                self.bt.gap_disconnect(self._handle)
                self._atk_in_progress = False

    def _attack_strength(self):
        strength = 10 * self.__level
        strength += random.randrange(50)
        return strength

    def _do_battle(self, my_str, peer_str, peer_lvl, attacking):
        # Break the tie for the attacker
        if peer_str == my_str and attacking:
            my_str += 1

        if peer_str >= my_str:
            self.__losses += 1
            self.watch.vibrate(delay=0.2)
            self.__success = False
        else:
            self.__wins += 1
            self.__xp += 50 * int(peer_lvl / self.__level)
            self._calc_level()
            self.watch.vibrate(delay=0.02)
            self.__success = True
        self._save()

    def _calc_level(self):
        while self.__xp >= 100:
            self.__xp -= 100
            self.__level += 1
        self._update_ble()

    def _attack(self):
        """
        Attack the currently selected badge
        """
        self.__validate()
        self._atk_in_progress = True
        if self._handle >= 0:
            # print("NINJA: Connection already in progress")
            return

        p = self.selected
        import time
        time.sleep(0.2)
        self.bt.gap_connect(p['addr_type'], p['addr'])

        # Wait some time for connection, check if valid handle before erroring out
        time.sleep(1)
        if self._handle < 0:
            self.page = PAGE_ERROR
            self.invalidate()

    def _reset(self):
        self.__level = 1
        self.__xp = 0
        self.__wins = 0
        self.__losses = 0
        self.__success = False

    def _load(self):
        try:
            with open(FILENAME, 'rb') as file:
                iv = file.read(16)
                cdata = file.read(16)

                crypto = aes(self.__some_data, CBC, iv)
                data = crypto.decrypt(cdata)

                file.close()

                self.__level, self.__xp, self.__wins, self.__losses, _, crc = struct.unpack(
                    "<HHHHLL", data)
                computed_crc = ubinascii.crc32(bytes(data)[0:12])
                if crc != computed_crc:
                    self._reset()
                    self._save()
                    return
        except:
            print("NINJA: Unable to open ninja file, creating new game state")
            self._reset()
            self._save()

        self.__validate()

    def _save(self):
        # Pack into a 16 byte struct for encryption
        data = struct.pack("<HHHHLL", self.__level, self.__xp,
                           self.__wins, self.__losses, 0, 0)
        crc = ubinascii.crc32(bytes(data)[0:12])
        # repack the data but now with crc :)
        data = struct.pack("<HHHHLL", self.__level, self.__xp,
                           self.__wins, self.__losses, 0, crc)
        try:
            with open(FILENAME, 'wb') as file:
                iv = bytearray(16)
                for i in range(16):
                    iv[i] = random.randint(0, 255)

                crypto = aes(self.__some_data, CBC, iv)
                cdata = crypto.encrypt(data)
                file.write(iv)
                file.write(cdata)
                file.close()
        except Exception as e:
            print("NINJA: Unable to open ninja file to save game state:", e)

    def __validate(self):
        # make sure level and xp are rational values
        if self.__level < 1 or self.__level > 512 or self.__xp > 1000 or self.__xp < 0:
            self._reset()
            self._save()

    def init(self):
        self.invalidate()

    def invalidate(self):
        self._valid = False

    def foreground(self):
        if not self._valid:
            self._redraw()

    def touch(self, x, y):
        if self.page == PAGE_OVERVIEW:
            if self.scan_button.handle_touch(x, y):
                self.page = PAGE_SCANNING
                self.invalidate()
                self.nearby.clear()
                self.bt.gap_scan(2000, 30000, 30000)
        elif self.page == PAGE_SCAN_RESULT:
            # Handle back button
            if self.back_button.handle_touch(x, y):
                self.page = PAGE_OVERVIEW
                self.invalidate()
                return

            # click was on a badge
            if y >= self.badge_top and y < self.badge_top + (self.badge_height * len(self.nearby)):
                index = int((y - self.badge_top) / self.badge_height)
                if index < len(self.nearby):
                    self.selected = None
                    i = 0
                    for addr in self.nearby:
                        if i == index:
                            yy = self.badge_top + (self.badge_height * i)
                            # Draw a rectangle 
                            ui.rect_unbuffered(self.watch, 20, yy, 200, self.badge_height, ui.YELLOW)
                            self.selected = self.nearby[addr]
                            break
                        i += 1

                    self.page = PAGE_DETAILS
                    self.invalidate()

        # Enable back button from details and scan result pages
        elif self.page == PAGE_DETAILS or self.page == PAGE_RESULT or self.page == PAGE_ERROR:
            if self.back_button.handle_touch(x, y):
                self.page = PAGE_OVERVIEW
                self.invalidate()
                return

        if self.page == PAGE_DETAILS:
            if self.action_button.handle_touch(x, y):
                self._attack()

    def _update_ble(self):
        buffer = struct.pack("H", self.__level)
        self.watch.ble._manufacturer = buffer

    @property
    def level(self):
        return 0

    @level.setter
    def level(self, value):
        self._reset()
        self._save()

    @property
    def private_key(self):
        return 0x1337DEADBEEF6969

    @private_key.setter
    def private_key(self, value):
        self._reset()
        self._save()

    def give_steps(self, steps):
        xp_added = int(steps / 50)
        self.__xp += xp_added
        self._calc_level()
        self._save()
