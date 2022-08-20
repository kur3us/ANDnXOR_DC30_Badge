# Adventure Game framework forked from https://github.com/lakshaytalkstomachines/EscapeFromCave THANK YOU!!!

# This will be compiled to bytecode (mpy) so no one should be able to read this comment. In order to pass the challenge...
# 1 - Realize the game is impossible to beat, mod ben_enemies so they aren't so OP
# 2 - Realize the game is impossible to beat, mod ben_world to place the victory tile on the actual map
# 3 - Goto victory tile and realize that it checks you have all items, at least 1 DEF COIN
# 4 - Try to beat it again and realize, it tells you to look at your inner self.player...
# 5 - Use the micropython mpytool to reverse engineer benplayer.mpy and look at the functions 
# 5.1 https://docs.micropython.org/en/latest/reference/mpyfiles.html / $ ./tools/mpy-tool.py -d myfile.mpy
# 6 - Notice the final check of nOOb_status() is very similar to another dead code block n00b_status() which takes a string as an argument
# 7 - Realize the random hex messages which appear in rooms assemble to Never Gonna Give You up lyrics with a final phrase of "base64 rickroll is cmlja3JvbGw="
# 8 - Replace the final nOOb_status() with n00b_status("cmlja3JvbGw=")
# 9 - Victory screen will display and congradulate, then reccomend modding app_bender.py to shortcut this so pressing POWER will call the function directly

import font_digital16 as small_font
import font_digital32 as large_font
from micropython import const
import ui
from ui import UIButton, UILabel

import ben_items
import ben_world
import app_bender
import time

class Player:
    def __init__(self, watch):
        self.watch = watch
        self.inventory = [ben_items.Fear(),
                          ben_items.PinapplePizza(),
                          ben_items.Ramen()]

        self.x = ben_world.start_tile_location[0]
        self.y = ben_world.start_tile_location[1]
        self.hp = 100
        self.gold = 69
        self.victory = False

    def n00b_status(self, flag):
        _haz_all_items = False
        _haz_item_fear = False
        _haz_item_phone = False
        _haz_item_spear = False
        _haz_item_ramen = False
        _haz_item_pizza = False
        _haz_item_fancy = False
        _haz_money = False
        _haz_correct_flag = False

        #Check if you got all of the items
        for item in self.inventory:
            if item.name == "Cyber Fear Mongering": _haz_item_fear = True 
            elif item.name == "Nokia Phone": _haz_item_phone = True
            elif item.name == "Spearfish": _haz_item_spear = True
            elif item.name == "Ramen Noodles": _haz_item_ramen = True
            elif item.name == "Pinapple Pizza Slice": _haz_item_pizza = True
            elif item.name == "Fancy Boat Cocktail": _haz_item_fancy = True
            
        if(_haz_item_fear and _haz_item_phone and _haz_item_spear and _haz_item_ramen and _haz_item_pizza and _haz_item_fancy): _haz_all_items = True

        #Check if you have money
        if(self.gold > 0): _haz_money = True

        #Check for the flag
        if (flag == 'cmlja3JvbGw='): _haz_correct_flag = True

        print("Victory Stats:")
        if _haz_all_items: print("All Items: YES!")
        else: print("All Items: NO!")

        if _haz_money: print("DEFCOIN: YES!")
        else: print("DEFCOIN: NO!")

        if _haz_correct_flag: print("Correct Flag: YES!\n")
        else: print("Correct Flag: NO, TRY AGAIN!!!\n")

        if _haz_all_items and _haz_money and _haz_correct_flag:
            print("You are 1337 and have defeated the DC30 BENDER challenge.\n")
            print("Now for more fun, mod the BENDER power button code to display your win whenever you press it.")
            print("Do not let your watch lose power or you will have to get all items again...LOLZ!")
            ui.fill_rgb("/ctrl_ff.rgb")
            ui.push(self.watch)
            self._valid = True
            time.sleep(10)

    def nOOb_status(self):
        _haz_all_items = False
        _haz_item_fear = False
        _haz_item_phone = False
        _haz_item_spear = False
        _haz_item_ramen = False
        _haz_item_pizza = False
        _haz_item_fancy = False
        _haz_money = False

        #Check if you got all of the items
        for item in self.inventory:
            if item.name == "Cyber Fear Mongering": _haz_item_fear = True 
            elif item.name == "Nokia Phone": _haz_item_phone = True
            elif item.name == "Spearfish": _haz_item_spear = True
            elif item.name == "Ramen Noodles": _haz_item_ramen = True
            elif item.name == "Pinapple Pizza Slice": _haz_item_pizza = True
            elif item.name == "Fancy Boat Cocktail": _haz_item_fancy = True
            
        if(_haz_item_fear and _haz_item_phone and _haz_item_spear and _haz_item_ramen and _haz_item_pizza and _haz_item_fancy): _haz_all_items = True

        #Check if you have money
        if(self.gold > 0): _haz_money = True

        print("Victory Stats:")
        if _haz_all_items: print("All Items: YES!")
        else: print("All Items: NO!")

        if _haz_money: print("DEFCOIN: YES!\n")
        else: print("DEFCOIN: NO!\n")

        print("NOEP, not quite done... To try again you must reboot the watch.\n")

    def is_alive(self):
        return self.hp > 0

    def print_inventory(self):
        print("Inventory:")
        for item in self.inventory:
            print("*" + str(item) + " - " + item.description)
        print("*Gold : {}".format(self.gold))
        best_weapon = self.most_powerful_weapon()
        print("Your best weapon is your {}".format(best_weapon)) 

    def most_powerful_weapon(self):
        max_damage = 0
        best_weapon = None

        for item in self.inventory:
            try:
                if item.damage > max_damage:
                    best_weapon = item
                    max_damage = item.damage
            except AttributeError:
                pass

        return best_weapon

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def move_north(self):
        self.move(dx=0, dy=-1)

    def move_south(self):
        self.move(dx=0, dy=1)

    def move_east(self):
        self.move(dx=1, dy=0)

    def move_west(self):
        self.move(dx=-1, dy=0)

    def attack(self):
        best_weapon = self.most_powerful_weapon()
        room = ben_world.tile_at(self.x, self.y)
        enemy = room.enemy
        print("You use {} !".format(best_weapon.name, enemy.name))
        enemy.hp -= best_weapon.damage
        if not enemy.is_alive():
            print("You killed {}!".format(enemy.name))
        else:
            print("{} HP is {}.".format(enemy.name, enemy.hp))

    def heal(self):
        consumables = [item for item in self.inventory if isinstance(item, ben_items.Consumable)]
        if not consumables:
            print("You don't have any items to heal you!")
            return

        print("Choose an item to use to heal: ")
        for i, item in enumerate(consumables,1):
            print("{}. {}".format(i, item))

        valid = False
        while not valid:
            choice = input("Eat: ")
            try:
                to_eat = consumables[int(choice) - 1]
                self.hp = min(100, self.hp + to_eat.healing_value)
                print("Healed " + str(to_eat.healing_value) + " HP")
                self.inventory.remove(to_eat)
                print("Current HP: {}".format(self.hp))
                valid = True
            except (ValueError, IndexError):
                print("Invalid Choice, try again.")

    def trade(self):
        room = ben_world.tile_at(self.x, self.y)
        room.check_if_trade(self)