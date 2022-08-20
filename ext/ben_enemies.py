# Adventure Game framework forked from https://github.com/lakshaytalkstomachines/EscapeFromCave THANK YOU!!!

class Enemy:
    def __init__(self):
        raise NotImplementedError("Do not create raw Enemy objects.")

    def __str__(self):
        return self.name

    def is_alive(self):
        return self.hp > 0

class SAO(Enemy):
    def __init__(self):
        self.name = "Shitty Add On (SAO)"
        self.hp = 150
        self.damage = 10

class InfosecInfluencer(Enemy):
    def __init__(self):
        self.name = "Infosec Influencer"
        self.hp = 300
        self.damage = 20


class InfosecTwitterFlameWar(Enemy):
    def __init__(self):
        self.name = "Infosec Twitter Flame War"
        self.hp = 500
        self.damage = 50


class NFTEvangelistCryptoBro(Enemy):
    def __init__(self):
        self.name = "NFT Evangelist Crypto Bro"
        self.hp = 666
        self.damage = 100
