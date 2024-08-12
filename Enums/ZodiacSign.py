from discord import PartialEmoji
from ._Enum import FroggeEnum
################################################################################
__all__ = ("ZodiacSign",)
################################################################################
class ZodiacSign(FroggeEnum):

    Aries = 1
    Taurus = 2
    Gemini = 3
    Cancer = 4
    Leo = 5
    Virgo = 6
    Libra = 7
    Scorpio = 8
    Sagittarius = 9
    Capricorn = 10
    Aquarius = 11
    Pisces = 12

################################################################################
    @property
    def emoji(self) -> PartialEmoji:
        
        if self.value == 1:
            return PartialEmoji(name="♈")
        elif self.value == 2:
            return PartialEmoji(name="♉")
        elif self.value == 3:
            return PartialEmoji(name="♊")
        elif self.value == 4:
            return PartialEmoji(name="♋")
        elif self.value == 5:
            return PartialEmoji(name="♌")
        elif self.value == 6:
            return PartialEmoji(name="♍")
        elif self.value == 7:
            return PartialEmoji(name="♎")
        elif self.value == 8:
            return PartialEmoji(name="♏")
        elif self.value == 9:
            return PartialEmoji(name="♐")
        elif self.value == 10:
            return PartialEmoji(name="♑")
        elif self.value == 11:
            return PartialEmoji(name="♒")
        elif self.value == 12:
            return PartialEmoji(name="♓")
        else:
            raise ValueError("Invalid Zodiac Sign value.")
    
################################################################################
