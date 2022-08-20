import font_digital16 as small_font
import font_digital32 as large_font
from micropython import const
import axp202c
import time
import ui
from ui import UIButton, UILabel

import ben_world
from ben_player import Player
from collections import OrderedDict

CLASSNAME = "BENDER"

class BENDER():
    APP_NAME = "BENDER"
    WEIGHT = 20

    def __init__(self, watch):
        self.watch = watch
        self._lbl_title = UILabel(self.watch, large_font, 77, 32, "BENDER", ui.GREEN)
        self._lbl_status_1 = UILabel(self.watch, small_font, 57, 62, "$echo Connect to", ui.GREEN)
        self._lbl_status_2 = UILabel(self.watch, small_font, 57, 77, "  PC over serial", ui.GREEN)
        self._lbl_status_3 = UILabel(self.watch, small_font, 57, 95, "$picocom -b 115200", ui.GREEN)
        self._lbl_status_4 = UILabel(self.watch, small_font, 57, 110, "  /dev/ttyACM0", ui.GREEN)
        self._btn_run = UIButton(self.watch, 40, 187, 'POWER')
        self._btn_run._bg = ui.INDIGO
        self._bender_running = False
        self.axp = axp202c.PMU()

    def init(self):
        self.invalidate()

    def _redraw(self):
        ui.fill_rgb("/bg_bender.rgb")
        self._lbl_title.fill_bg()
        self._lbl_title.draw()
        self._lbl_status_1.draw()
        self._lbl_status_2.draw()
        self._lbl_status_3.draw()
        self._lbl_status_4.draw()
        self._btn_run.draw()
        ui.push(self.watch)
        self._valid = True

    def foreground(self):
        if not self._valid:
            self._redraw()

    def invalidate(self):
        self._valid = False

    def touch(self, x, y):
        if self._btn_run.handle_touch(x, y):
            if self.axp.isVBUSPlugIn():
                self._btn_run._fg = ui.HOTPINK
                self._lbl_status_1._text = "$echo System Halt"
                self._lbl_status_2._text = "  Until Quit!"
                self._lbl_status_3._text = "$picocom -b 115200"
                self._lbl_status_4._text = "  /dev/ttyACM0"
                self._redraw()

                #Kickoff BENDER
                self.play()

                #BENDER has terminated, now revert
                self._btn_run._fg = ui.BLACK
                self._lbl_status_1._text = "$echo Connect to"
                self._lbl_status_2._text = "  PC over serial"
                self._redraw()
            else:
                #Incase a user accidently taps POWER but is not connected to a computer
                self._btn_run._fg = ui.RED
                self._lbl_status_1._text = "     REQUIRES USB"
                self._lbl_status_2._text = "       CONNECTION"
                self._lbl_status_3._text = "             TO"
                self._lbl_status_4._text = "        ACTIVATE"
                self._redraw()

                #Pause So They Can Read Their Misfortune
                time.sleep(7)

                #BENDER has terminated, now revert
                self._btn_run._fg = ui.BLACK
                self._lbl_status_1._text = "$echo Connect to"
                self._lbl_status_2._text = "  PC over serial"
                self._lbl_status_3._text = "$picocom -b 115200"
                self._lbl_status_4._text = "  /dev/ttyACM0"
                self._redraw()

    def play(self):
        print()
        print()
        print("""
DEF CON 30 AND!XOR Badge Enabled Non Directive Enigma Routine (B.E.N.D.E.R.)

   .+=   =+.                                                                      
     .+=   =+.                -**********=.    :++*****+=:   :************:       
       .+=   =+.              +%%=======*%%:  *#*=======##+  +%%==========.       
         .+=   =+.            +%%        %%+  +*.       =##  +%%                  
           .+=  .* *:         +%%        %%+            =##  +%%                  
             .+=.* %@*.       +%%        %%+       -****##-  +%%*******=          
         -*+.=.%.* %@@@=      +%%        %%+       .---=##+  +%%=======:          
         +@@:*.%.* %@@@@=     +%%        %%+            =##  +%%                  
           # *.%.* %@@@@+     +%%        %%+  ##:       =##  +%%                  
      .#@* # *.%.* %@@@@+     +%%*******#%#.  =##*+++++*##-  +%#                  
       *%* # *.%.* %@@@@+     .==========:     .-=======-    .=:                  
      . -= # *.%.* %@@@@+        ........        .......      .          .        
    =@- -= # *.%.* %@@@@+      =#%%%%%%%%%+   .+#########*:  -%%+.      *%+       
  -%@@- -= # *.%.* #@@@@+     -%%-      .#%*  *#*.      +##. -%%%%+.    #%*       
.#@@@@- -= # *.% *- -%@@+     =%%        .-.  ##=     :+###. -%%:+%%+.  #%*       
=@@@@@: -= # *.%  :+- -%+     =%%             ##=   -*##+##. -%%. .+%%+.#%*       
=@@@+..+= :# #.-+.  :+- .     =%%             ##= -##*- -##. -%%.   .+%%%%*       
=@= .+= :+-.+-   =+.  -@@#    =%%             #####+:   -##. -%%.     .+%%*       
. .+= :+-.+=       =+. +#+    =%%        :+:  ###=.     -##. -%%.       #%*       
##+ .+-.+=           =        :%%=::::::-%%+  *#*:::::::+##  -%%.       #%*       
@#-+-.+=                       :*%%%%%%%%#=    =*########+.  :%#        +%+       
.+-                                                                               
-                                                                                                                                                                                                                       
        """)
        ben_world.parse_world_dsl()
        player = Player(self.watch)

        self._bender_running = True
        while player.is_alive() and not player.victory:
            room = ben_world.tile_at(player.x, player.y)
            print(room.intro_text())
            room.modify_player(player)
            
            if player.is_alive() and not player.victory:
                self.choose_action(room, player)
            elif not player.is_alive():
                ben_world.world_map.clear
                print("Your journey has come to an early end! ")
            
            #Check for Quit 
            if self._bender_running == False:
                break

        #Final status display at end of game
        if player.is_alive() and player.victory:
            player.nOOb_status()
    
    def quit(self):
        self._bender_running = False

    def get_available_actions(self, room, player):
        actions = OrderedDict()
        print("Choose an action: ")
        if player.inventory:
            self.action_adder(actions, 'i', player.print_inventory, "Print inventory")
        if isinstance(room, ben_world.TraderTile):
            self.action_adder(actions, 't', player.trade, "Trade")
        if isinstance(room, ben_world.EnemyTile) and room.enemy.is_alive():
            self.action_adder(actions, 'a', player.attack, "Attack")
        else:
            if ben_world.tile_at(room.x, room.y - 1):
                self.action_adder(actions, 'n', player.move_north, "Go North")
            if ben_world.tile_at(room.x, room.y + 1):
                self.action_adder(actions, 's', player.move_south, "Go South")
            if ben_world.tile_at(room.x + 1, room.y):
                self.action_adder(actions, 'e', player.move_east, "Go East")
            if ben_world.tile_at(room.x - 1, room.y):
                self.action_adder(actions, 'w', player.move_west, "Go West")
            if player.hp < 100:
                self.action_adder(actions, 'h', player.heal, "Heal")
        self.action_adder(actions, 'p', self.quit, "Quit B.E.N.D.E.R.")
        return actions

    def action_adder(self, action_dict, hotkey, action, name):
        action_dict[hotkey.lower()] = action
        action_dict[hotkey.upper()] = action
        print("{} : {}".format(hotkey, name))

    def choose_action(self, room, player):
        action = None
        while not action:
            available_actions = self.get_available_actions(room, player)
            action_input = input("Action: ")
            action = available_actions.get(action_input)
            if action:
                print()
                action()
                print()
            else:
                print()
                print("Invalid action!")
                print()