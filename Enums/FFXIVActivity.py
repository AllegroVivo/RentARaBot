from ._Enum import FroggeEnum
################################################################################
__all__ = ("FFXIVActivity",)
################################################################################
class FFXIVActivity(FroggeEnum):

    MSQ = 1
    Fate = 2
    Crafting = 3
    Gathering = 4
    DeepDungeon = 5
    RP = 6
    GoldSaucer = 7
    GPose = 8
    Collector = 9
    ExtremeSavage = 10
    PvP = 11
    Raid = 12
    TreasureHunt = 13
    Fashion = 14
    Hunts = 15
    
################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 1:
            return "MSQ Aficionado"
        elif self.value == 2:
            return "FATE Farmer"
        elif self.value == 3:
            return "Crafting Fanatic"
        elif self.value == 4:
            return "Gathering Guru"
        elif self.value == 5:
            return "Deep Dungeon Diver"
        elif self.value == 6:
            return "Roleplay Enthusiast"
        elif self.value == 7:
            return "i LoVe GoLd SaUcEr"
        elif self.value == 8:
            return "GPose Wizard"
        elif self.value == 9:
            return "Must Collect ALL THE THINGS"
        elif self.value == 10:
            return "Extreme/Savage Enthusiast"
        elif self.value == 11:
            return "PvP Gladiator"
        elif self.value == 12:
            return "Raid Devotee"
        elif self.value == 13:
            return "Treasure Map Maniac"
        elif self.value == 14:
            return "Fashionista"
        elif self.value == 15:
            return "Hunt Train Attendee"

        return self.name

################################################################################
