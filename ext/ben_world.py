# Adventure Game framework forked from https://github.com/lakshaytalkstomachines/EscapeFromCave THANK YOU!!!

import random
import ben_enemies
import ben_characters

class MapTile:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def intro_text(self):
        raise NotImplementedError("Create a subclass instead!")

    def modify_player(self, player):
        pass


class StartTile(MapTile):
    def intro_text(self):
        return "You wake in a not so drunk but not so sober state. Its 3am.\nYou're in what looks like a conference area, but its empty-ish...or is it?\n"

class BENDERTile(MapTile):
    def switch_description(self, arg):
        switcher = {
            0:"Are you drunk? You see... 57 57 39 31 49 47 74 75 62 33 63 67 64 47 68 6c 49 48 4a 31 62 47 56 7a 49 47 46 75 5a 43 42\n",
            1:"Are you drunk? You see... 7a 62 79 42 6b 62 79 42 4a 43 6b 45 67 5a 6e 56 73 62 43 42 6a 62 32 31 74 61 58 52 74 5a 57\n",
            2:"Are you drunk? You see... 35 30 4a 33 4d 67 64 32 68 68 64 43 42 4a 4a 32 30 67 64 47 68 70 62 6d 74 70 62 6d 63 67 62\n",
            3:"Are you drunk? You see... 32 59 4b 57 57 39 31 49 48 64 76 64 57 78 6b 62 69 64 30 49 47 64 6c 64 43 42 30 61 47 6c 7a\n",
            4:"Are you drunk? You see... 49 47 5a 79 62 32 30 67 59 57 35 35 49 47 39 30 61 47 56 79 49 47 64 31 65 51 70 4a 49 47 70\n",
            5:"Are you drunk? You see... 31 63 33 51 67 64 32 46 75 62 6d 45 67 64 47 56 73 62 43 42 35 62 33 55 67 61 47 39 33 49 45\n",
            6:"Are you drunk? You see... 6b 6e 62 53 42 6d 5a 57 56 73 61 57 35 6e 43 6b 64 76 64 48 52 68 49 47 31 68 61 32 55 67 65\n",
            7:"Are you drunk? You see... 57 39 31 49 48 56 75 5a 47 56 79 63 33 52 68 62 6d 51 4b 54 6d 56 32 5a 58 49 67 5a 32 39 75\n",
            8:"Are you drunk? You see... 62 6d 45 67 5a 32 6c 32 5a 53 42 35 62 33 55 67 64 58 41 4b 54 6d 56 32 5a 58 49 67 5a 32 39\n",
            9:"Are you drunk? You see... 75 62 6d 45 67 62 47 56 30 49 48 6c 76 64 53 42 6b 62 33 64 75 43 6b 35 6c 64 6d 56 79 49 47\n",
            10:"Are you drunk? You see... 64 76 62 6d 35 68 49 48 4a 31 62 69 42 68 63 6d 39 31 62 6d 51 67 59 57 35 6b 49 47 52 6c 63\n",
            11:"Are you drunk? You see... 32 56 79 64 43 42 35 62 33 55 4b 54 6d 56 32 5a 58 49 67 5a 32 39 75 62 6d 45 67 62 57 46 72\n",
            12:"Are you drunk? You see... 5a 53 42 35 62 33 55 67 59 33 4a 35 43 6b 35 6c 64 6d 56 79 49 47 64 76 62 6d 35 68 49 48 4e\n",
            13:"Are you drunk? You see... 68 65 53 42 6e 62 32 39 6b 59 6e 6c 6c 43 6b 35 6c 64 6d 56 79 49 47 64 76 62 6d 35 68 49 48\n",
            14:"Are you drunk? You see... 52 6c 62 47 77 67 59 53 42 73 61 57 55 67 59 57 35 6b 49 47 68 31 63 6e 51 67 65 57 39 31 43\n",
            15:"Are you drunk? You see... 6c 6c 76 64 58 49 67 61 32 56 35 49 48 52 76 49 48 4e 30 59 58 52 31 63 79 42 70 63 79 42 69\n",
            16:"Are you drunk? You see... 59 58 4e 6c 4e 6a 51 67 4a 33 4a 70 59 32 74 79 62 32 78 73 4a 77 3d 3d\n",
            17:"Finally something new! You see, googly eyes on a advertisement...\n",
            18:"Are you drunk? You think to yourself, Security IS compliance.\n",
            19:"Are you drunk? You think about how awesome it is SETFACL and GETFACL provide access control fidelity at the file system level.\n",
            20:"Are you drunk? You think to yourself that COBIT is governance, not risk management, and somewhat believe it.\n",
            21:"Are you drunk? You think to yourself if there's an EvilMog and he's pretty damn awesome, is there a GoodMog who just sux?\n",
            22:"Are you drunk? You think to yourself its a good idea to take out a reverse 2nd mortgage to invest in cryptocurrency.\n",
            23:"Are you drunk? You think to yourself its a good idea to take out a reverse 3rd mortgage to invest in NFTs.\n",
            24:"Are you drunk? You think to yourself I could eat some ramen right now...\n",
            25:"Are you drunk? You think to yourself could I used Ghidra to reverse the Ida license file?\n",
            26:"Are you drunk? You think to yourself about making a badge with at least five 18650s powering it.\n",
            27:"Are you drunk? You think to yourself what if you hack all the booze and drink all the things?\n",
            28:"Are you drunk? You think to yourself that Arch Linux isn't all that bad...not nearly as bad as BSD...\n",
            29:"Are you drunk? You think to yourself that Web3 is a pretty good idea and has a solid foundation.\n",
            30:"Are you drunk? You think to yourself how you would rather be watching defrag right now.\n",
            31:"Are you drunk? You think to yourself how you would rather be watching SpinRite fix a drive right now.\n",
            32:"Are you drunk? You think to yourself about replacing the entire network stack with Alcatel switches.\n",
            33:"Are you drunk? You think you see written on the wall...\n"
                "You are accessing a U.S. Government (USG) Information System (IS) that is provided for USG-authorized use only.\n"
                "By using this IS (which includes any device attached to this IS), you consent to the following conditions:\n"
                "-The USG routinely intercepts and monitors communications on this IS for purposes including, but not limited to, penetration testing,\n"
                " COMSEC monitoring, network operations and defense, personnel misconduct (PM), law enforcement (LE), and counterintelligence (CI) investigations.\n"
                "-At any time, the USG may inspect and seize data stored on this IS.\n"
                "-Communications using, or data stored on, this IS are not private, are subject to routine monitoring, interception, and search, \n"
                " and may be disclosed or used for any USG-authorized purpose.\n"
                "-This IS includes security measures (e.g., authentication and access controls) to protect USG interests--not for your personal benefit or privacy.\n"
                "-Notwithstanding the above, using this IS does not constitute consent to PM, LE or CI investigative searching or monitoring of the content of\n" 
                " privileged communications, or work product, related to personal representation or services by attorneys, psychotherapists, or clergy, and their assistants.\n"
                " Such communications and work product are private and confidential. See User Agreement for details.\n"
                "I've read & consent to terms in IS user agreement.\n",
        }
        return switcher.get(arg, "You see nothing interesting...")

    def intro_text(self):
        return(self.switch_description(random.randint(0,33)))

class VictoryTile(MapTile):
    def intro_text(self):
        return "You see a bright light in the distance...it grows as you get closer! It's sunlight! You've been up a long time.\nVictory is yours? Is it really? Did you really overcome this challenge? As a player you should antithesize your inner self.python.\n"
        
    def modify_player(self, player):
        player.victory = True
        

#TODO ADD ANSI ART
class EnemyTile(MapTile):
    def __init__(self, x, y):
        r = random.random()
        if r < 0.25:
            self.enemy = ben_enemies.SAO()
            self.alive_text = """
You drunkely step barefoot on a Shitty Add On (SAO), its poison lead and e-waste fills your bloodstream.\n
                                             .                                            
                                            =@*                                           
                                            =@*                                           
                                            =@*                                           
                                             .                                            
                      :#-                                         -*:                     
                      :*@%-                                     -%@#:                     
                        .*@*                ...                +@*.                       
                          .            .=++==*@@@#=.            .                         
                                      **. .-+#@@@@@@*                                     
                                    .#: -%@@@@@@@@@@@%.                                   
                                    #- =@@@@@@@@@@@@@@@                                   
                                    @=-@@@@@@@@@@@@@@@@:                                  
                                    @@@@@@@@@@@@@@@@@@@:                                  
                                    @@@@@@@@@@@@@@@@@@@:                                  
                                    @@@@@@@@@@@@@@@@@@@:                                  
             -******                @@@@@%%%@@%%%%@@@@@:               =*****-            
             :======                @@@@:   :.     @@@@:               -=====:            
                                    @@@@: *: :#@#  @@@@:                                  
                                    @@@@: #@@@@@#  @@@@:                                  
                                    @@@@: #@@@@@#  @@@@:                                  
                                    ####. +#####+  ####.                                  
                                 :::::::::::::::::::::::::                                
                                :@@@@@@@@@@@@@@@@@@@@@@@@@-                               
                                .%%%%%%%%%%%%%%%%%%%%%%%%%:                               
                                        =+.      --                                       
                                        #@:     :@@                                       
                                        #@:     :@@                                       
                                        #@:     :@@                                       
                                        #@:     :@@                                       
                                        +#.     :@@                                       
                                                :@@                                       
                                                :%%                                       
"""
            self.dead_text = "An SAO lies smashed in a pile of FR4, header pins, cracked LEDs, and of course no resistors.\n"
        elif r < 0.50:
            self.enemy = ben_enemies.InfosecInfluencer()
            self.alive_text = """
A wild opinionated infosec influencer appears, powered by 30k+ followers, a wall of CompTIA certs, and no experience in system administration...\n

@@@@@@@@@@@@@@@@@@@@@@%%%%%%%%%%%%%%%%%%@@@@@@@@@%######################%%%%%%%%%%%%%%%%%%
@@@@@@@@@@@@@@@@@%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@@@@@@%#*#####################%%%%%%%%%%%%%%
@@@@@@@@@@@@@@%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@@@@@@@@@@@%#****####################%%%%%%%%%%
@@@@@@@@@@@%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@@@@@@@@@@@@@@%#******###################%%%%%%%
@@@@@@@@@@%%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@@@@@@@@@@@@@@@@@@%#******#####################%%%
@@@@@@@@%%%%%%%%%%%%%%%%%%%%#%%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%*********####################
@@@@@@@%%%%%%%%%%%%%%%%%#####%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%************################
@@@@%%%%%%%%%%%%%%%%%#######%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#*+*************############
########%%%%%%%%%##########%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%*+++**************#########
********##%%%#############@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*++++*****************#####
########################%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%*++++++*****************##
******+*****##***######%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%*+++++++++***************
+++*+++*++++*+*++*####%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%++++++++++++************
++****+*+*+**+*++*###%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#++++++++++++++*********
**###**#****#*#***##%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#+++++++++++++++*******
###********#*****##%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*====++++++--=========
###***************%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+=========---========
###***************@@@@@@@@@@@@@@@@@%%%%%%%%###%%@@@@@@@@@@@@@@@@@@@@@%=-========+++++++***
########*********#@@@@@@@@@@@@@@%#********++=++*##########%%@@@@@@@@@%=--=======++++++****
###########******#@@@@@@@@@@@@@@%*+++======----=++++====+**%@@@@@@@@@#---=======++++++****
############******@@@@@@@@@@@@@@@@%%%%%%###*-:-====+*#%%%#%%@@@@@@@@%=---=======+++++*****
##############****#%@@@@@@@@@@@@@#=------=**--+%%+=--::-+#%@@@@@@@@#------======+++++*****
%#############*****#%@@@@@@@@@@@@@#*+++++++=---=+=====+#%@@@@@@@@@%##*+=========++++******
%%%###########%%@@@@@@@@@@@@@@@@@@%*+++++===-----=====*%@@@@@@@@@%@@@@@@%#*+====++++******
##########%@@@@@@@@@@@@@@@@@@@@@@@@#+======---------=+#%@@@@@@@%%@@@@@@@@@@%%%*==+++******
%#######%@@@@@@@@@@@@@@@@@@@@@@@@@@@#+=====--====---+%@@@@@@@@@%@@@@@@@@@@@@@@@+-=+*******
%%%####%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%******#%%%%#*#%@@@@@@@@@%@@@@@@@@@@@@@@@@%*:=+*****+
##################################################%%%%%%%%%%%%%%%%%####%@@@@@@@@@#=******=
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@%%%%@@@@@@@@@@%******+
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@%%%@%%%@@@@@@@@@@@#***#*+
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@%%%%%%%%%%%@@@@@%%@@@@@@@@@@@@#*##*+
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@@%%@@@@@@@@@@@@%###*+
%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@%%%@@@@@%%%%@@@@@@@@@@@@@@@@@@@@@@@@@@@%@@@@@@@@@@@@@@#+*#*
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%@@@@@@@@@@@@@@%+==+
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%%@@@@%%@@@@@@@@@@@@@@@@%=:
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%%@%%@@@@@@@@@@@@@@@@@@%-
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%%@%%@@@@@@@@@@@@@@@@@@@*
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%%%%%%@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%%%#+*%@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%%#=+***%@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%%%%%%#*++*%@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%%@@@%%*#@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%@@@@@%%@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
"""
            self.dead_text = "A withered corpse of an influencer remains, only now followed by bots, to remind you of your triumph.\n"
        elif r < 0.75:
            self.enemy = ben_enemies.InfosecTwitterFlameWar()
            self.alive_text = """
You hear a squeaking noise growing louder...suddenly you are lost in a swarm of subjective opinions powered by emotion! Its an Infosec Twitter Flame War!\n

..........................................................................................
...................:::....................................................................
..................-*###*=:................................................................
...................+*******=:.............................................................
...................-**********-...........................................................
...................-**********#+-........::::.............................................
...................-***********##+:...::+*********+++===---::::...........................
..................:-#*****+******#*--=**#**********************+..........................
............:+*+=--=%*************##=***###********************:..........................
............-**####*%**************#%#****##******************:...........................
............:*#***#%%**********************##***#************-............................
............:*%*****************************#%*####*********-.............................
............:*%******************************%%#**#%#****#*-..............................
............-##**************+***************##*****#%**##=...............................
.........:::+%***************+++*********************#%##=................................
.......:++-=%#**************+++++*********************#%#+++==----:::.....................
......-######***********+***++++++*+****************###*****###*#####****+++===--::.......
.....:*#***#************++++++++++++++************###*****************************+-......
.....=#*****************++++++++++++++*++********%#****#**********************##***-......
....:+#*****************++++++++++++++++++****###***##**********************##*+++*-......
....:+#**************++++++++++++++++++++++*##****##*******#*******#******##++++++*-......
.....-#************++++++++++++++++++++++*##****##******##*******#*****##*++++++++*-......
.....:+#**********+++++++++++++++++++++*%#****##******##******##*****##*++++++++++*-......
......-##****+****+++++++++++++++++++#%#***###******##******##*****##*++++++*++++++-......
......-#############*****+++++++++*#%#*************#*******#*****##*++++++++*++++++-......
......-#*+++++++++******#########%%%#######*******************###+++++++++++*++++++-......
......-#*++++++++++++++++++++++++++++*******###################+++++++++++++*++++**-......
......-#*++++**+++++++++++++++++++++++++++++++++++++++++***##+++++++*+++++++*+****++:.....
......-#*++++++*****************+++++++++++++++++++++++++++*%+++++++*++++++**++++++*+.....
......-#*+++++++++++++++++++++++++****************+++++++++*%+++++++#++****+++++++++*-....
......-#*++++++++++++++++++++++++++++++++++++++++++****++++*%++++++*#***+++++++++++*+:....
......-#*++++++++++***+++++++++++++++++++++++++++++++++++++#%++++*##*++++++++++****=:.....
......-#*++++++++*%%%%%*+++++++++++++++++++++++++++++++++++*%+++##++++++++++***++++-......
......=#*++++++++#%%%%%%+++++++++++++++++++#%%#*+++++++++++*%+++%*++++++*****+++++*-......
......=#*+++++++++#%%%%#++++*#++++++++++++#%%%%%*++++++++++*%+++*#*****#*+++*+++++*-......
......=#*+++++++++++++++++++*#%#**#%%*++++*%%%%%#++++++++++*%++++++*#*++++++*+++++*-......
......=#*+++++++++++++++++++++*####*++++++++****+++++++++++*%+++++++*+++++++*+++++*=......
......=#*++++++++++++++++++++++++++++++++++++++++++++++++++*%+++++++*++++++++++++**=......
......=#*+++*******++++++++++++++++++++++++++++++++++++++++*%+++++++*++++++++***++*=......
......=#*+++++++++*******************++++++++++++++++++++++*%+++++++*+++++****+++*+:......
......=#*++++++++++++++++++++++++++++****************++++++*%++++++++++**+=:--==-:........
......=###*******++++++++++++++++++++++++++++++++++++++++++*%+++++++**+=:.................
......-#*+***##+++++******##******+++++++++++++++++++++++++*#++++**+=:....................
.......-++*#*+-:.....::::::----===++++*************++++++++*#*##*=:.......................
..........:::..........................:::::-------===++#*****#*:.........................
......................................................:-++++***=..........................
........................................................:-=++=:...........................
"""
            self.dead_text = "The tweet thread of emotion and circular arguments is dead, hopefully it stays that way an doesn't get a retweet.\n"
        else:
            self.enemy = ben_enemies.NFTEvangelistCryptoBro()
            self.alive_text = """
From around the corner lunges a Crypto Bro! They are coked up on ponzi schemes, wanting you to join their Discord,\n and slice at you with a piece of paper...A fungable piece of paper with a photo of some drunk ape.\n"

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++++++++++++++++++++++*******+++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++++++*****############*+++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++****##################**+++++++++++++++++++++++++++
+++++++++++++++++++++++++*******+++++**##***********####*++=*##+++++++++++++++++++++++++++
++++++++++++++++++++++++*###**###***######*+==+++++===*++++=*#***###**++++++++++++++++++++
+++++++++++++++++++++++*##+=++++*%######*===+*#*+#*+==***+#++###***###++++++++++++++++++++
++++++++++++++++++++++*##+++=++++#%##*++==++==+###+*==*=*%***#+++++=##++++++++++++++++++++
+++++++++++++++++++++*###====++===*#*+*+=+*++##+=+##++**#+*#*====+=+##++++++++++++++++++++
+++++++++++++++++++++*###====+====+##++*+==+*****##***#**++*====+++##*++++++++++++++++++++
++++++++++++++++++++++###+===+====+##++=-++*+***+=+===*++**+++==+*##*+++++++++++++++++++++
++++++++++++++++++++++*###+=====+++###*==++++*###*++==**###**++*#**+++++++++++++++++++++++
+++++++++++++++++++++++*####**++**%###**#*++++++===+=+*==+++#*#**+++++++++++++++++++++++++
++++++++++++++++++++++***#********#####**++*+===++====*====+#**+++++++++++++++++++++++++++
++++++++++++++++++++++****++++++++#####++*+*+**+======++====+*++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++*###*++==-+---==+=+++*++++++**+++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++*###+++=--+=---======+*====***+++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++*####++*=+====*------++===+++*+++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++*####+++++==+++*****+++===++*+++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++*+*###==++===============+**++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++**++*##*+=============++**++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++*##++***####**+++++****+++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++###*#*+****#%#++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++++###**#*+++**%#++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++*#*#+*##+*++*##*+++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++++*##*#+*##*+++*##*+++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++++*#####*+####***#####**++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++**+*%%###**#############%%*+++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++***#####***%%##############%%#***###***++++++++++++++++++++++++++++++
++++++++++++++++++**##**+==-=++**#%%%%%%%%%%%%%%#***+++=+++#*+++++++++++++++++++++++++++++
+++++++++++++++++*#++++**##**++====--===----------====+++*#=**++++++++++++++++++++++++++++
++++++++++++++++*+==+**====++***######***################**#**++++++++++++++++++++++++++++
+++++++++++++++***##**+##**++==---=====================---+++#*+++++++++++++++++++++++++++
+++++++++++++++#+++======++**#####*****+++++***********####*++*+++++++++++++++++++++++++++
++++++++++++++*+**#*####*#+=---===++++++***++++++++++++==+***##+++++++++++++++++++++++++++
-++++++++++++*#++++===--=*###***+++++=============+++++++*#+==**+++++++++++++++++++++++++-
"""
            self.dead_text = "Defeated, a crypto bro lies limp & breathless on the floor, just like any coin or NFT from a few weeks ago.\n"

        super().__init__(x, y)

    def intro_text(self):
        text = self.alive_text if self.enemy.is_alive() else self.dead_text
        return text

    def modify_player(self, player):
        if self.enemy.is_alive():
            player.hp = player.hp - self.enemy.damage
            print("Enemy does {} damage. You have {} HP remaining.\n"
                  .format(self.enemy.damage, player.hp))


class TraderTile(MapTile):
    def intro_text(self):
        return """
A Frail not-quite-human, not-quite-creature squats in a booth, clinking their 3d printed DEFCOINs together.
They look willing to trade as long as they can add you to their monthly infosec newsletter.      
                                       #@@@@@%%%%%%%%%%%%%%%%%%#*                         
                                      =@@@@@@%%%%%%%%%%%%%%%%%%%%*                        
                                      %@@@@%@%%%%%%%%%%%%%%%%%%%#%:                       
             -=-:.     .--=====++++**#@@@@@@@%@%%@@@@@@@@@@@%%%%%%-                       
            :+#=+:    :@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%#+=:                   
             =*-+:     +@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%*-                
             :..:-      :#@@@@@@@@@@@%%####*****####%@@@@@@@@@@@@@@@@@@@@@%+.             
             :.  -        :*@@@@@@@@*+===============+*##%%%@@@@@@@@@@@@@@@@@=            
           .:::..:-.:.      .=#@@@%#*++===-==========+***+===*%@@@@@@@@@@@@@@@*           
         -#%#=====---=+        .-=+##**++===++***==-:-=++=---==+*%@@@@@@@@@@@@@-          
         %%@*.   .   .=.         ..##*##++=-*****=-=-....:....:::=%@@@@@@@@@@@@+          
         *%@#..----:-.-:          :***+*=..-+**=*##++=--:::.:::-=+*#@@@@@@@@@@@:          
         *%%%:...::.. :=          +****+:...:===-:--:......::-:::=+=#@@@@@@@@#:           
       -+%@%@:  .::.  .+         :+++++:.....:--::......:::.::-=*=-=*@@@@@#+:             
     .-*#%@%@-  ....  .+.        -++*#*+=+=:+:.........:::..+-::+=-:**+=:                 
   -====-:*%%=.........*-.       ***+=++-::-==-.........:..:=*--=-.                       
   -+++=--=*%+.........+=.       ***=-:::....-+=:...........:-::.                         
    ---:::...=. .......+*.       +#%%#*++==----++-:::.:.:::.::                            
    :+*#%###%#. .......-=        -####**+=---=+==---::-:=#+-.                             
    .:-:--=+*%. ...:...-=         #####**+=-::=*+-------==*%                              
   .===--:::-*: ..::::..+      .:=#%##+-:.::..:=+=----:-:=%@*                             
    *#%%@%%%@@-..:=+=-:::...-*%@@@@@@%%#*=---=+##*++=-:.=%@@@*   .-=*####***+=-:.         
     +**++*@%@%###%@@%#+---:::-+#@@@@@@%@%%%#+*%%%#+-::#@@@@@@@%%@@@@@@@@@@@@%%%%#+:      
      *++++#%%@@@@@%%*+@%#+=---:::-=*%%#*#%%%#+++=:. -%@@@@@@@@@@@@@@@@@@@@@@@@@@@%%=     
       +#******++**+=*@@@@@%#+=:::::::==-::*@@#:.  .+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%-    
        -%#**++=+===*@@@@@@@#+=:::::::::::+@@#*=  .+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#    
        -++========+@@@@@@@%**=------::::::-+*+=-.=@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*    
      .*%*+==--===+%@@@@@@@##+--==------::::::::::=+*#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+.  
     -%@@#+=====+*%@@@@@@@@%*=======-------::::::::::-%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%= 
   .#@@@@%+++++*%@@@@@@@@@@@+========--------------::+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%
  +@@@@@@%**+*%@@@@@@@@@@@@@%#+===--=========--------#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
:%@@@@@@@#**#@@@@@@@@@@@@@@@@%***+==---==+++++==++++*%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@%@@@@@@@@@@@@@@@@@@@%%%%#**###########*#*#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%#%#####@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
"""

    def __init__(self,x,y):
        self.trader = ben_characters.Trader()
        super().__init__(x, y)

    def trade(self, buyer, seller):
        while True:
            item_count = 0
            for i, item in enumerate(seller.inventory, 1):
                item_count = item_count + 1
                print("{}. {} - {} DEFCOIN".format(i, item.name, item.value))
            if item_count > 0:
                user_input = input("Choose an item or press Q to exit: ")
            else:
                print("No more shit to trade, go away!\n")
                return
            if user_input in ['Q', 'q']:
                return
            else:
                try:
                    choice = int(user_input)
                    if (choice < 1) or (choice > item_count):
                        print("You fail...the validation of inputs. IN-PUT!\n")
                        return
                    to_swap = seller.inventory[choice - 1]
                    self.swap(seller, buyer, to_swap)
                except ValueError:
                    print("Invalid Choice!")

    def swap(self, seller, buyer, item):
        if item.value > buyer.gold:
            print("That's too expensive, hack better, or steal more money!")
            return
        seller.inventory.remove(item)
        buyer.inventory.append(item)
        seller.gold = seller.gold + item.value
        buyer.gold = buyer.gold - item.value
        print("Trade Complete!\n")

    def check_if_trade(self, player):
        while True:
            print("Would you like to (B)uy, (S)ell, or (Q)uit?")
            user_input = input("Action: ")
            if user_input in ['q', 'Q']:
                return
            elif user_input in ['B', 'b']:
                print("Here's whats available to buy: ")
                self.trade(buyer = player, seller = self.trader)
            elif user_input in ['S', 's']:
                print("Here's whats available to sell: ")
                self.trade(buyer=self.trader, seller=player)
            else:
                print("Invalid choice!")


class FindGoldTile(MapTile):
    def __init__(self, x, y):
        self.gold = random.randint(1, 50)
        self.gold_claimed = False
        super().__init__(x, y)

    def modify_player(self, player):
        if not self.gold_claimed:
            self.gold_claimed = True
            player.gold = player.gold + self.gold
            print("+{} DEFCOIN added.".format(self.gold))

    def intro_text(self):
        if self.gold_claimed:
            return"""
            Another unremarkable part of the conference hall at 3AM.
            You must forge onward.
            """
        else:
            return"""
            Someone dropped some DEFCOIN. You pick it up.
            """  
 
def is_dsl_valid(dsl):
    if dsl.count("|ST|") != 1:
        return False
    if dsl.count("|VT|") == 0:
        return False
    lines = dsl.splitlines()
    lines = [l for l in lines if l]
    pipe_counts = [line.count("|") for line in lines]
    for count in pipe_counts:
        if count != pipe_counts[0]:
            return False
    return True

def parse_world_dsl():
    if not is_dsl_valid(world_dsl):
        raise SyntaxError("DSL is invalid")

    dsl_lines = world_dsl.splitlines()
    dsl_lines = [x for x in dsl_lines if x]

    for y, dsl_row in enumerate(dsl_lines):
        row = []
        dsl_cells = dsl_row.split("|")
        dsl_cells = [c for c in dsl_cells if c]
        for x, dsl_cell in enumerate(dsl_cells):
            tile_type = tile_type_dict[dsl_cell]
            if tile_type == StartTile:
                global start_tile_location
                start_tile_location = x, y
            row.append(tile_type(x, y) if tile_type else None)
        world_map.append(row)

def tile_at(x, y):
    if x < 0 or y < 0:
        return None
    try:
        return world_map[y][x]
    except IndexError:
        return None

world_dsl = """
|ST||BT||  ||  ||  ||ET||ET|
|BT||BT||ET||  ||BT||ET||FT|
|BT||  ||BT||  ||BT||  ||  |
|ET||  ||BT||TT||ET||  ||  |
|BT||  ||BT||  ||BT||  ||  |
|BT||  ||BT||  ||BT||  ||  |
|BT||BT||ET||  ||BT||ET||BT|
|FT||BT||  ||  ||  ||BT||FT|
|  ||  ||  ||VT||  ||BT||  |
|ET||BT||BT||  ||  ||ET||  |
|  ||  ||BT||  ||BT||BT||ET|
|  ||  ||BT||  ||ET||  ||BT|
|BT||BT||ET||  ||BT||  ||FT|
|ET||BT||ET||  ||ET||  ||BT|
|  ||  ||BT||  ||FT||  ||BT|
|  ||  ||BT||TT||BT||BT||BT|
|BT||BT||BT||  ||  ||ET||  |
"""

world_map = []

tile_type_dict = {"VT": VictoryTile,
                  "ET": EnemyTile,
                  "ST": StartTile,
                  "FT": FindGoldTile,
                  "TT": TraderTile,
                  "BT": BENDERTile,
                  "  ": None}

start_tile_location = None
