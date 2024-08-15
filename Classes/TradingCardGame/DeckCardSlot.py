from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar, Any, Tuple

from discord import Interaction

from UI.Common import ConfirmCancelView
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import TradingCard, CardDeck
################################################################################

__all__ = ("DeckCardSlot", )

DCS = TypeVar("DCS", bound="DeckCardSlot")

################################################################################
class DeckCardSlot:

    __slots__ = (
        "_id",
        "_parent",
        "_order",
        "_card"
    )
    
################################################################################
    def __init__(self, parent: CardDeck, _id: str, order: int, card: TradingCard) -> None:

        self._id: str = _id
        self._parent: CardDeck = parent
        
        self._order: int = order
        self._card: TradingCard = card
    
################################################################################
    @classmethod
    def new(cls: Type[DCS], parent: CardDeck, card: TradingCard) -> DCS:

        new_order = len(parent) + 1
        new_id = parent.bot.database.insert.deck_card_slot(parent.id, new_order, card.id)
        return cls(parent, new_id, new_order, card)
    
################################################################################
    @classmethod
    def load(cls: Type[DCS], parent: CardDeck, data: Tuple[Any, ...]) -> DCS:

        return cls(
            parent=parent,
            _id=data[0],
            order=data[2],
            card=parent.card_manager.get_card(data[3])
        )
    
################################################################################
    def __eq__(self, other: DeckCardSlot) -> bool:
        
        return self.id == other.id
    
################################################################################
    @property
    def id(self) -> str:
        
        return self._id
    
################################################################################
    @property
    def order(self) -> int:
        
        return self._order
    
    @order.setter
    def order(self, value: int) -> None:
        
        self._order = value
        self.update()
    
################################################################################
    @property
    def card(self) -> TradingCard:
        
        return self._card
    
    @card.setter
    def card(self, value: TradingCard) -> None:
        
        self._card = value
        self.update()
        
################################################################################
    def update(self) -> None:
            
        self._parent.bot.database.update.deck_card_slot(self)
        
################################################################################
    def delete(self) -> None:
        
        self._parent.bot.database.delete.deck_card_slot(self)
        self._parent._cards.remove(self)
        
################################################################################
    async def remove(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Card__",
            description=f"Are you sure you want to remove {self.card.name} from this deck?",
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.delete()
        
################################################################################
