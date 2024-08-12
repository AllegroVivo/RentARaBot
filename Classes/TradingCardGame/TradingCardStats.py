from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Tuple, Any

from discord import Interaction
from UI.TradingCardGame import CardStatsModal

if TYPE_CHECKING:
    from Classes import TradingCard, RentARaBot
################################################################################

__all__ = ("TradingCardStats", )

TCS = TypeVar("TCS", bound="TradingCardStats")

################################################################################
class TradingCardStats:

    __slots__ = (
        "_parent",
        "_bad",
        "_battle",
        "_nsfw",
        "_sfw",
        "_die",
    )
    
################################################################################
    def __init__(self, parent: TradingCard, **kwargs) -> None:

        self._parent: TradingCard = parent
        
        self._bad: Optional[int] = kwargs.get("bad")
        self._battle: Optional[int] = kwargs.get("battle")
        self._nsfw: Optional[int] = kwargs.get("nsfw")
        self._sfw: Optional[int] = kwargs.get("sfw")
        self._die: Optional[int] = kwargs.get("die")
    
################################################################################
    @classmethod
    def load(cls: Type[TCS], parent: TradingCard, data: Tuple[Any, ...]) -> TCS:
        
        return cls(
            parent=parent,
            bad=data[1],
            battle=data[2],
            nsfw=data[3],
            sfw=data[4],
            die=data[5],
        )
    
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._parent.bot
    
################################################################################
    @property
    def bad_stat(self) -> Optional[int]:
        
        return self._bad
    
    @bad_stat.setter
    def bad_stat(self, value: int) -> None:
        
        self._bad = value
        # self.update()
        
################################################################################
    @property
    def battle_stat(self) -> Optional[int]:
        
        return self._battle
    
    @battle_stat.setter
    def battle_stat(self, value: int) -> None:
        
        self._battle = value
        # self.update()
        
################################################################################
    @property
    def nsfw_stat(self) -> Optional[int]:
        
        return self._nsfw
    
    @nsfw_stat.setter
    def nsfw_stat(self, value: int) -> None:
        
        self._nsfw = value
        # self.update()
        
################################################################################
    @property
    def sfw_stat(self) -> Optional[int]:
        
        return self._sfw
    
    @sfw_stat.setter
    def sfw_stat(self, value: int) -> None:
        
        self._sfw = value
        # self.update()
        
################################################################################
    @property
    def die_marker(self) -> Optional[int]:
        
        return self._die
    
    @die_marker.setter
    def die_marker(self, value: int) -> None:
        
        self._die = value
        # self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.trading_card_stats(self)
        
################################################################################
    async def set_values(self, interaction: Interaction) -> None:
        
        modal = CardStatsModal((
            self.die_marker,
            self.bad_stat, 
            self.battle_stat,
            self.nsfw_stat,
            self.sfw_stat
        ))
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        (
            self.die_marker,
            self.bad_stat, 
            self.battle_stat, 
            self.nsfw_stat, 
            self.sfw_stat
        ) = modal.value
        self.update()
    
################################################################################
