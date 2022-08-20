# Adventure Game framework forked from https://github.com/lakshaytalkstomachines/EscapeFromCave THANK YOU!!!

import ben_items

class NonPlayableCharacter():
    def __init__(self):
        raise NotImplementedError("Do not create raw Non Playable Character objects.")

    def __str__(self):
        return self.name

class Trader(NonPlayableCharacter):
    def __init__(self):
        self.name = "Trader"
        self.gold = 100
        self.inventory = [  ben_items.Ramen(),
                            ben_items.Ramen(),
                            ben_items.Ramen(),
                            ben_items.Ramen(),
                            ben_items.PinapplePizza(),
                            ben_items.PinapplePizza(),
                            ben_items.PinapplePizza(),
                            ben_items.FancyBoat(),
                            ben_items.FancyBoat(),
                            ben_items.FancyBoat(),
                            ben_items.Nokia(),
                            ben_items.Spearfish()]