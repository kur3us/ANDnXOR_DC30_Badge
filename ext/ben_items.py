# Adventure Game framework forked from https://github.com/lakshaytalkstomachines/EscapeFromCave THANK YOU!!!

class Weapon:
    def __init__(self):
        raise NotImplementedError("Dop not create raw Weapon objects.")

    def __str__(self):
        return self.name

class Fear(Weapon):
    def __init__(self):
        self.name = "Cyber Fear Mongering"
        self.description = "Screw risk management, take the most obscure 0-Day and hype your enemy into a crying fetal position."
        self.damage = 15
        self.value = 1

class Nokia(Weapon):
    def __init__(self):
        self.name = "Nokia Phone"
        self.description = "Solid THIKK design and attatched to the end of a chain for swingy bludgeony power."
        self.damage = 50
        self.value = 50

class Spearfish(Weapon):
    def __init__(self):
        self.name = "Spearfish"
        self.description = "A spear with a nasty old fish on the end of it. The fish is intended for your target."
        self.damage = 100
        self.value = 100

class Consumable:
    def __init__(self):
        raise NotImplementedError("Do not create raw Consumable objects.")

    def __str__(self):
        return "{} (+{} HP)".format(self.name, self.healing_value)

class Ramen(Consumable):
    def __init__(self):
        self.name = "Ramen Noodles"
        self.description = "Delicious keto friendly shirataki noodles."
        self.healing_value = 10
        self.value = 10

class PinapplePizza(Consumable):
    def __init__(self):
        self.name = "Pinapple Pizza Slice"
        self.description = "Delicious gluten powered cheesy tomatoe paste bread with tropical fruit. The Perfect Pairing."
        self.healing_value = 25
        self.value = 25

class FancyBoat(Consumable):
    def __init__(self):
        self.name = "Fancy Boat Cocktail"
        self.description = "Two Parts Vodka, Four Parts Coconut LaCroix, One Part Lime Juice"
        self.healing_value = 50
        self.value = 50