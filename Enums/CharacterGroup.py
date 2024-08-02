from ._Enum import FroggeEnum
################################################################################
__all__ = ("CharacterGroup",)
################################################################################
class CharacterGroup(FroggeEnum):

    Patron = 0
    EssentialStaff = 1
    Management = 2
    LifetimeVIP = 3
    RentableRa = 4
    Battlemaiden = 5

################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 1:
            return "Essential Staff"
        elif self.value == 3:
            return "Lifetime VIP"
        elif self.value == 4:
            return "Rentable-Ra"

        return self.name
    
################################################################################
    