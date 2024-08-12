from ._Enum import FroggeEnum
################################################################################
__all__ = ("MusicGenre",)
################################################################################
class MusicGenre(FroggeEnum):

    Rock = 1
    Pop = 2
    Jazz = 3
    Classical = 4
    HipHop = 5
    Blues = 6
    Country = 7
    EDM = 8
    Reggae = 9
    RnB = 10
    Soul = 11
    Funk = 12
    Metal = 13
    Punk = 14
    Folk = 15
    Gospel = 16
    Ska = 17
    Latin = 18
    KPop = 19
    World = 20
    Indie = 21
    Ambient = 22
    Opera = 23
    Techno = 24
    Dubstep = 25

################################################################################
    @property
    def proper_name(self) -> str:

        if self.value == 5:
            return "Hip-Hop"
        elif self.value == 8:
            return "Electronic Dance Music (EDM)"
        elif self.value == 10:
            return "Rhythm and Blues (RnB)"
        elif self.value == 19:
            return "K-Pop"
        elif self.value == 20:
            return "World Music"
        
        return self.name
    
################################################################################
    