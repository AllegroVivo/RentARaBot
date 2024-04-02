from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
from discord import Interaction, User

from .Patron import Patron

if TYPE_CHECKING:
    from Classes import GuildData, RentARaBot
################################################################################

__all__ = ("PatronManager",)

################################################################################
class PatronManager:
    
    __slots__ = (
        "_state",
        "_patrons"
    )
    
################################################################################
    def __init__(self, bot: GuildData):
        
        self._state: GuildData = bot
        self._patrons: List[Patron] = []
        
################################################################################
    def __getitem__(self, user_id: int) -> Optional[Patron]:
        
        for patron in self._patrons:
            if patron.user.id == user_id:
                return patron
            
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._state.bot
    
################################################################################ 
    @property
    def guild_id(self) -> int:
        
        return self._state.guild_id

################################################################################
    def get_or_add_patron(self, user: User) -> Patron:
        
        ret = self[user.id]
        
        if ret is None:
            ret = Patron.new(user)
            self._patrons.append(ret)
            
        return ret

################################################################################
