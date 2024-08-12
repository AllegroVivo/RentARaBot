from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

from discord import Embed, Interaction

from .ManagedItem import ManagedItem

if TYPE_CHECKING:
    from Classes import GuildData, RentARaBot
    from UI.Common import FroggeView
################################################################################

__all__ = ("ItemManager",)

################################################################################
class ItemManager(ABC):

    __slots__ = (
        "_state",
        "_managed",
        "_item_type",
        "_view_type",
    )
    
################################################################################
    def __init__(self, state: GuildData, item_type: Type[ManagedItem], view_type: Type[FroggeView]) -> None:

        self._state: GuildData = state
        self._managed: List[ManagedItem] = []
        
        self._item_type: Type[ManagedItem] = item_type
        self._view_type: Type[FroggeView] = view_type
    
################################################################################
    async def load_all(self, payload: List[Dict[str, Any]]) -> None:
        
        for data in payload:
            self._managed.append(await self._item_type.load(self, data))
    
################################################################################
    def __len__(self) -> int:
        
        return len(self._managed)
    
################################################################################
    def __getitem__(self, item_id: str) -> Optional[ManagedItem]:
        
        return next((m for m in self._managed if m.id == item_id), None)
    
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._state.bot
    
################################################################################
    @property
    def guild(self) -> GuildData:
        
        return self._state
    
################################################################################
    @property
    def guild_id(self) -> int:
        
        return self._state.guild_id
    
################################################################################
    @property
    def all_items(self) -> List[ManagedItem]:
        
        return self._managed
    
################################################################################
    @abstractmethod
    def status(self) -> Embed:
        
        raise NotImplementedError
    
################################################################################
    async def main_menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = self._view_type(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
