from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Type, TypeVar, Any, Dict, Tuple

from discord import SelectOption, Interaction, Embed, EmbedField
from discord.ext.pages import Page

from Assets import BotEmojis, BotImages
from Errors import MaxCardsReached
from UI.TradingCardGame import CardSelectView
from Utilities import Utilities as U
from Utilities.Constants import *
from .TradingCard import TradingCard

if TYPE_CHECKING:
    from Classes import CardManager, RentARaBot, CardCollection
################################################################################

__all__ = ("CardSeries", )

CS = TypeVar("CS", bound="CardSeries")

################################################################################
class CardSeries:

    __slots__ = (
        "_id",
        "_mgr",
        "_order",
        "_name",
        "_cards",
    )
    
################################################################################
    def __init__(
        self, 
        mgr: CardManager,
        _id: str, 
        order: int, 
        name: str, 
        cards: Optional[List[TradingCard]] = None
    ) -> None:

        self._id: str = _id
        self._mgr: CardManager = mgr
        self._order: int = order
        
        self._name: str = name
        self._cards: List[TradingCard] = cards or []
    
################################################################################
    @classmethod
    def new(cls: Type[CS], mgr: CardManager, name: str) -> CS:
        
        order = len(mgr)
        new_id = mgr.bot.database.insert.card_series(mgr.guild_id, order, name)
        return cls(mgr, new_id, order, name)
    
################################################################################
    @classmethod
    def load(cls: Type[CS], mgr: CardManager, data: Dict[str, Any]) -> CS:
        
        sdata = data["series"]
        
        self: CS = cls.__new__(cls)
        
        self._id = sdata[0]
        self._mgr = mgr
        
        self._order = sdata[2]
        self._name = sdata[3]
        self._cards = [TradingCard.load(self, c) for c in data["cards"]]
        
        return self
    
################################################################################
    def __getitem__(self, card_id: str) -> Optional[TradingCard]:
        
        return next((c for c in self._cards if c.id == card_id), None)
        
################################################################################
    def __len__(self) -> int:
        
        max_idx = 0
        for card in self._cards:
            try:
                index = int(card.index)
                if index > max_idx:
                    max_idx = index
            except ValueError:
                continue
            
        return max_idx
    
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
    def card_manager(self) -> CardManager:
        
        return self._mgr
    
################################################################################
    @property
    def id(self) -> str:
        
        return self._id
    
################################################################################
    @property
    def name(self) -> str:
        
        return self._name
    
################################################################################
    @property
    def order(self) -> int:
        
        return self._order
    
################################################################################
    @property
    def cards(self) -> List[TradingCard]:
        
        self._cards.sort(key=lambda c: c.index)
        return self._cards
    
################################################################################
    def select_option(self) -> SelectOption:
        
        return SelectOption(
            label=self.name,
            value=self.id,
            description=f"({len(self)} cards)",
        )
    
################################################################################
    async def select_card(self, interaction: Interaction, prompt: Embed) -> Optional[TradingCard]:
        
        view = CardSelectView(interaction.user, [c.select_option() for c in self.cards])
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        return self[view.value]
    
################################################################################
    async def add_card(self, interaction: Interaction) -> None:
        
        if len(self) >= MAX_CARDS_PER_SERIES:
            error = MaxCardsReached(MAX_CARDS_PER_SERIES)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        new_card = TradingCard.new(self)
        self._cards.append(new_card)
        
        await new_card.menu(interaction)
        
################################################################################
    async def modify_card(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Modify Card__",
            description=(
                "Please select the card you want to modify."
            ),
        )
        card = await self.select_card(interaction, prompt)
        if card is None:
            return
        
        await card.menu(interaction)
        
################################################################################
    async def remove_card(self, interaction: Interaction) -> None:
    
        prompt = U.make_embed(
            title="__Remove Card__",
            description=(
                "Please select the card you want to remove."
            ),
        )
        card = await self.select_card(interaction, prompt)
        if card is None:
            return
        
        await card.remove(interaction)

################################################################################
    def get_card_totals(self, coll: CardCollection) -> Tuple[int, int]:
        
        num_owned = total_owned = 0
        for card in self.cards:
            qty = coll[card]
            if qty is not None:
                total_owned += qty.quantity
                num_owned += 1
                
        return num_owned, total_owned
    
################################################################################
    def card_collection_strs(self, coll: CardCollection) -> List[str]:
        
        if not self.cards:
            return []

        card_strs = [f"__{self.name}__"]
        for card in self.cards:
            qty = coll[card]
            if qty is not None:
                card_strs.append(f"`{card.index}` {BotEmojis.CheckGreen} {card.name} *(x{qty.quantity})*")
            else:
                card_strs.append(f"`{card.index}` {BotEmojis.CheckGray} {card.name}")
                
        return card_strs
    
################################################################################
    def get_card_by_index(self, index: str) -> Optional[TradingCard]:
        
        return next((c for c in self.cards if c.index.lower() == index.lower()), None)
            
################################################################################
