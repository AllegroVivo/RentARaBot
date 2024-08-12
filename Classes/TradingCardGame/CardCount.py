from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar, Any, Tuple

from discord import Embed, Interaction
from Utilities import Utilities as U
from UI.Common import ConfirmCancelView

if TYPE_CHECKING:
    from Classes import CardCollection, TradingCard, RentARaBot
################################################################################

__all__ = ("CardCount", )

CC = TypeVar("CC", bound="CardCount")

################################################################################
class CardCount:

    __slots__ = (
        "_id",
        "_parent",
        "_card",
        "_qty",
    )
    
################################################################################
    def __init__(self, parent: CardCollection, _id: str, card: TradingCard, qty: int) -> None:

        self._id: str = _id
        self._parent: CardCollection = parent
        
        self._card: TradingCard = card
        self._qty: int = qty
    
################################################################################
    @classmethod
    def new(cls: Type[CC], parent: CardCollection, card: TradingCard, qty: int = 1) -> CC:
        
        new_id = parent.bot.database.insert.card_count(parent.id, card.id, qty)
        return cls(parent, new_id, card, qty)
    
################################################################################
    @classmethod
    def load(cls: Type[CC], parent: CardCollection, data: Tuple[Any, ...]) -> CC:
        
        return cls(
            parent=parent,
            _id=data[0],
            card=parent.card_manager.get_card(data[2]),
            qty=data[3]
        )
    
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._parent.bot
    
################################################################################
    @property
    def id(self) -> str:
        
        return self._id
    
################################################################################
    @property
    def card(self) -> TradingCard:
        
        return self._card
    
################################################################################
    @property
    def quantity(self) -> int:
        
        return self._qty
    
    @quantity.setter
    def quantity(self, value: int) -> None:
        
        self._qty = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.card_count(self)
    
################################################################################
    def delete(self) -> None:
        
        self.bot.database.delete.card_count(self)
        self._parent.cards.remove(self)
        
################################################################################
    async def remove(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Card__",
            description=(
                f"Are you sure you want to remove all copies of "
                f"`{self.card.name}` from this collection?"
            ),
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.delete()
    
################################################################################
