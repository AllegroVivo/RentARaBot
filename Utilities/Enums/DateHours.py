from typing import List

from discord import SelectOption

from ._Enum import FroggeEnum
################################################################################
class DateHours(FroggeEnum):

    DontKnow = 0
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8

################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 0:
            return "I Don't Know"
        
        return self.name

################################################################################
    @staticmethod
    def select_options() -> List[SelectOption]:

        return [p.select_option for p in DateHours]

################################################################################
