from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from Classes.Dating.DatingManager import DatingManager
from Classes.General.PatronManager import PatronManager

from discord import Guild

if TYPE_CHECKING:
    from Classes import RentARaBot
################################################################################

__all__ = ("GuildData",)

################################################################################
class GuildData:
    """A container for bot-specific guild data and settings."""

    __slots__ = (
        "_state",
        "_parent",
        "_patron_mgr",
        "_dating_mgr",
    )

################################################################################
    def __init__(self, bot: RentARaBot, parent: Guild):

        self._state: RentARaBot = bot
        self._parent: Guild = parent
        
        self._patron_mgr: PatronManager = PatronManager(self)
        self._dating_mgr: DatingManager = DatingManager(self)

################################################################################
    async def load_all(self, data: Dict[str, Any]) -> None:
        
        pass
        
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._state
    
################################################################################
    @property
    def parent(self) -> Guild:
        
        return self._parent
    
################################################################################
    @property
    def guild_id(self) -> int:
        
        return self._parent.id
    
################################################################################
    @property
    def patron_manager(self) -> PatronManager:
        
        return self._patron_mgr
    
################################################################################
    @property
    def dating_manager(self) -> DatingManager:
        
        return self._dating_mgr
    
################################################################################
