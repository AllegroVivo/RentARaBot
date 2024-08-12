from ._Enum import FroggeEnum
################################################################################
__all__ = ("BedroomPreference",)
################################################################################
class BedroomPreference(FroggeEnum):

    Dom_Only = 1
    Dom_By_Nature = 2
    Dom_By_Request = 3
    Dom_By_Mood = 4
    Switch = 5
    Sub_By_Mood = 6
    Sub_By_Request = 7
    Sub_By_Nature = 8
    Sub_Only = 9
    Romance = 10
    NA = 11

################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 10:
            return "Romance/Affection Only"
        elif self.value == 11:
            return "Not Applicable"
        else:
            return (self.name.replace("Dom", "Dominant")
                    .replace("Sub", "Submissive")
                    .replace("_", " "))
        
################################################################################
