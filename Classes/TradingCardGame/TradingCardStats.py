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
        "_cute",
        "_cuddle",
        "_crush",
        "_die",
    )
    
################################################################################
    def __init__(self, parent: TradingCard, **kwargs) -> None:

        self._parent: TradingCard = parent
        
        self._bad: Optional[int] = kwargs.get("bad")
        self._cute: Optional[int] = kwargs.get("cute")
        self._cuddle: Optional[int] = kwargs.get("cuddle")
        self._crush: Optional[int] = kwargs.get("crush")
        self._die: Optional[int] = kwargs.get("die")
    
################################################################################
    @classmethod
    def load(cls: Type[TCS], parent: TradingCard, data: Tuple[Any, ...]) -> TCS:
        
        return cls(
            parent=parent,
            bad=data[1],
            cute=data[2],
            cuddle=data[3],
            crush=data[4],
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
    def cute_stat(self) -> Optional[int]:
        
        return self._cute
    
    @cute_stat.setter
    def cute_stat(self, value: int) -> None:
        
        self._cute = value
        # self.update()
        
################################################################################
    @property
    def cuddle_stat(self) -> Optional[int]:
        
        return self._cuddle
    
    @cuddle_stat.setter
    def cuddle_stat(self, value: int) -> None:
        
        self._cuddle = value
        # self.update()
        
################################################################################
    @property
    def crush_stat(self) -> Optional[int]:
        
        return self._crush
    
    @crush_stat.setter
    def crush_stat(self, value: int) -> None:
        
        self._crush = value
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
            self.cute_stat,
            self.cuddle_stat,
            self.crush_stat
        ))
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        (
            self.die_marker,
            self.bad_stat, 
            self.cute_stat,
            self.cuddle_stat,
            self.crush_stat
        ) = modal.value
        self.update()
    
################################################################################
