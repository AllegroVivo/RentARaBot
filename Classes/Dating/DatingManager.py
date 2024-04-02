from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
from discord import Interaction

from .DatingRequest import DatingRequest

if TYPE_CHECKING:
    from Classes import GuildData, RentARaBot
################################################################################

__all__ = ("DatingManager",)

################################################################################
class DatingManager:
    
    __slots__ = (
        "_state",
        "_requests"
    )
    
################################################################################
    def __init__(self, bot: GuildData):
        
        self._state: GuildData = bot
        self._requests: List[DatingRequest] = []
        
################################################################################
    def __getitem__(self, request_id: str) -> Optional[DatingRequest]:
        
        for request in self._requests:
            if request.id == request_id:
                return request
            
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._state.bot
    
################################################################################ 
    @property
    def guild_id(self) -> int:
        
        return self._state.guild_id
    
################################################################################
    async def start_request(self, interaction: Interaction) -> None:
        
        patron = self._state.patron_manager.get_or_add_patron(interaction.user)
        request = DatingRequest.new(self, patron)
        self._requests.append(request)
        
        await interaction.respond(embed=request.status())
        
################################################################################
