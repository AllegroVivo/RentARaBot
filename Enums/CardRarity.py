from ._Enum import FroggeEnum
################################################################################
__all__ = ("CardRarity",)
################################################################################
class CardRarity(FroggeEnum):

    Common = 0
    Uncommon = 1
    Rare = 2
    UltraRare = 3
    Legendary = 4

################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 3:
            return "Ultra Rare"

        return self.name
    
################################################################################
    