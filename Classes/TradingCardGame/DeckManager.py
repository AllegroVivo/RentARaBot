from __future__ import annotations

from typing import TYPE_CHECKING, List, Type, TypeVar, Any, Dict, Optional

from discord import Interaction, Embed, EmbedField, User

from .CardDeck import CardDeck
from Errors import MaxItemsReached
from Utilities import Utilities as U
from UI.Common import BasicTextModal, FroggeSelectView
from UI.TradingCardGame import DeckManagerMenuView

if TYPE_CHECKING:
    from Classes import CardCollection, CardManager, RentARaBot
################################################################################

__all__ = ("DeckManager", )

DM = TypeVar("DM", bound="DeckManager")

################################################################################
class DeckManager:

    __slots__ = (
        "_parent",
        "_decks",
    )
    
    MAX_DECKS = 10
    
################################################################################
    def __init__(self, parent: CardCollection, decks: List[CardDeck] = None) -> None:

        self._parent: CardCollection = parent
        self._decks: List[CardDeck] = decks or []
    
################################################################################
    @classmethod
    def load(cls: Type[DM], parent: CardCollection, data: List[Dict[str, Any]]) -> DM:

        self: DM = cls.__new__(cls)
        
        self._parent = parent
        self._decks = [CardDeck.load(self, deck) for deck in data]
        
        return self
    
################################################################################
    def __getitem__(self, deck_id: str) -> Optional[CardDeck]:
        
        return next((deck for deck in self._decks if deck.id == deck_id), None)
        
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._parent.bot
    
################################################################################
    @property
    def user(self) -> User:
        
        return self._parent.user
    
################################################################################
    @property
    def card_manager(self) -> CardManager:
        
        return self._parent.card_manager
    
################################################################################
    @property
    def collection_id(self) -> str:
        
        return self._parent.id
    
################################################################################
    def status(self) -> Embed:
        
        return U.make_embed(
            title="__Battle Deck Management__",
            description=f"Decks for {self._parent.user.display_name}",
            fields=[
                EmbedField(
                    name=deck.name, 
                    value=f"{len(deck)}x cards",
                    inline=True
                ) 
                for deck in self._decks
            ]
        )
    
################################################################################
    async def main_menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = DeckManagerMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    async def add_deck(self, interaction: Interaction) -> None:
        
        if len(self._decks) >= self.MAX_DECKS:
            error = MaxItemsReached("Battle Decks", self.MAX_DECKS)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        modal = BasicTextModal(
            title="Enter Deck Name",
            attribute="Name",
            example="eg. 'Baby's First Deck'",
            max_length=50
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        new_deck = CardDeck.new(self, modal.value)
        self._decks.append(new_deck)
        
        await new_deck.menu(interaction)
        
################################################################################
    async def modify_deck(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Modify Deck__",
            description="Please select the deck you wish to modify.",
        )
        view = FroggeSelectView(interaction.user, [deck.select_option() for deck in self._decks])
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        deck = self[view.value]
        await deck.menu(interaction)
    
################################################################################
