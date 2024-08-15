from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Any, Dict

from discord import Interaction, Embed, EmbedField

from .CardSeries import CardSeries
from UI.Common import FroggeSelectView, BasicTextModal
from UI.TradingCardGame import CardManagerMenuView, CardSelectView
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import TCGManager, RentARaBot, TradingCard
################################################################################

__all__ = ("CardManager", )

################################################################################
class CardManager:

    __slots__ = (
        "_mgr",
        "_series_list",
    )
    
################################################################################
    def __init__(self, mgr: TCGManager) -> None:

        self._mgr: TCGManager = mgr
        self._series_list: List[CardSeries] = []
    
################################################################################
    def load_all(self, data: List[Dict[str, Any]]) -> None:
        
        self._series_list = [CardSeries.load(self, s) for s in data]
            
################################################################################
    def __len__(self) -> int:
        
        return len(self._series_list)
    
################################################################################
    def __getitem__(self, series_id: str) -> Optional[CardSeries]:
        
        for series in self._series_list:
            if series.id == series_id:
                return series
        
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._mgr.bot
        
################################################################################
    @property
    def guild_id(self) -> int:
        
        return self._mgr.guild_id
    
################################################################################
    @property
    def series_list(self) -> List[CardSeries]:
        
        return self._series_list
    
################################################################################
    @property
    def total_cards(self) -> int:
        
        return sum(len(series) for series in self._series_list) 
    
################################################################################
    @property
    def all_cards(self) -> List[TradingCard]:
        
        return [card for series in self._series_list for card in series.cards]
    
################################################################################
    def status(self) -> Embed:
        
        totals_str = ""
        for series in self._series_list:
            totals_str += f"{series.name}: `{len(series)} Cards`\n"
        
        return U.make_embed(
            title="__TCG Card Management__",
            description=(
                "Welcome to the Trading Card Game module!\n"
                "Select an option below to get started."
            ),
            fields=[
                EmbedField(
                    name="__Series Card Totals__",
                    value=totals_str or "`No cards found.`",
                    inline=False
                )
            ]
        )
        
################################################################################
    async def main_menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = CardManagerMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    async def select_series(self, interaction: Interaction, prompt: Embed) -> Optional[CardSeries]:

        view = FroggeSelectView(interaction.user, [s.select_option() for s in self._series_list])
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        return self[view.value]
    
################################################################################
    async def add_card(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Add New Card__",
            description=(
                "Please select the series you want to add the new card to."
            ),
        )
        series = await self.select_series(interaction, prompt)
        if series is None:
            return
        
        await series.add_card(interaction)
    
################################################################################
    async def modify_card(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Card__",
            description=(
                "Please select the series of the card you wish to modify."
            ),
        )
        series = await self.select_series(interaction, prompt)
        if series is None:
            return
        
        await series.modify_card(interaction)
    
################################################################################
    async def remove_card(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Card__",
            description=(
                "Please select the series of the card you wish to remove."
            ),
        )
        series = await self.select_series(interaction, prompt)
        if series is None:
            return
        
        await series.remove_card(interaction)
    
################################################################################
    async def add_series(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Add New Series - Enter Name",
            attribute="Name",
            max_length=50,
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        series = CardSeries.new(self, modal.value)
        self._series_list.append(series)
        
################################################################################
    def get_card(self, card_id: str) -> Optional[TradingCard]:
        
        for series in self._series_list:
            for card in series.cards:
                if card.id == card_id:
                    return card
    
################################################################################
    def get_series_by_order(self, order: int) -> Optional[CardSeries]:
        
        return next((s for s in self._series_list if s.order == order), None)
            
################################################################################
    def get_cards_by_name(self, name: str) -> List[TradingCard]:
        
        return [card for card in self.all_cards if card.name.lower() == name.lower()]
    
################################################################################
