from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from discord import Interaction, Embed

from .Identifiable import Identifiable

if TYPE_CHECKING:
    from Classes import ItemManager, RentARaBot, GuildData
################################################################################

__all__ = ("ManagedItem", )

################################################################################
class ManagedItem(Identifiable):

    __slots__ = (
        "_mgr",
        "_view_type",
    )
    
################################################################################
    def __init__(self, mgr: ItemManager, _id: str) -> None:
        
        super().__init__(_id)
        
        self._mgr: ItemManager = mgr
    
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._mgr.bot
    
################################################################################
    @property
    def guild(self) -> GuildData:
        
        return self._mgr.guild
    
################################################################################
    @property
    def guild_id(self) -> int:
        
        return self.guild_id
    
################################################################################
    @abstractmethod
    def status(self) -> Embed:
        
        pass
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = self._view_type(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
