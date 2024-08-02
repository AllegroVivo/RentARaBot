from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Dict, Type, TypeVar, Any, Tuple

from discord import User, Embed, EmbedField, Interaction
from Enums import CardRarity
from .CardCount import CardCount
from UI.TradingCardGame import CardCollectionMenuView
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import TradingCard, CollectionManager, CardManager, RentARaBot
################################################################################

__all__ = ("CardCollection", )

CC = TypeVar("CC", bound="CardCollection")

################################################################################
class CardCollection:

    __slots__ = (
        "_id",
        "_mgr",
        "_user",
        "_cards",
    )
    
################################################################################
    def __init__(
        self,
        mgr: CollectionManager,
        _id: str,
        user: User, 
        cards: Optional[List[CardCount]] = None
    ) -> None:

        self._id: str = _id
        self._mgr: CollectionManager = mgr
        
        self._user: User = user
        self._cards: List[CardCount] = cards or []
    
################################################################################
    @classmethod
    def new(cls: Type[CC], mgr: CollectionManager, user: User) -> CC:
        
        new_id = mgr.bot.database.insert.card_collection(mgr.guild_id, user.id)
        return cls(mgr, new_id, user)
    
################################################################################
    @classmethod
    async def load(cls: Type[CC], mgr: CollectionManager, data: Dict[str, Any]) -> CC:
        
        self = cls.__new__(cls)
        
        self._id = data["collection"][0]
        self._mgr = mgr
        
        self._user = await mgr.guild.get_or_fetch_member_or_user(data["collection"][2])
        self._cards = [CardCount.load(self, d) for d in data["cards"]]
        
        return self
    
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._mgr.bot
    
################################################################################
    @property
    def id(self) -> str:
        
        return self._id
    
################################################################################
    @property
    def card_manager(self) -> CardManager:
        
        return self._mgr._mgr.card_manager
    
################################################################################
    @property
    def user(self) -> User:
        
        return self._user
    
################################################################################
    @property
    def cards(self) -> List[CardCount]:
        
        return self._cards
    
    @property
    def common_cards(self) -> List[CardCount]:
        
        return [c for c in self._cards if c.card.rarity == CardRarity.Common]
    
    @property
    def uncommon_cards(self) -> List[CardCount]:
        
        return [c for c in self._cards if c.card.rarity == CardRarity.Uncommon]
    
    @property
    def rare_cards(self) -> List[CardCount]:
        
        return [c for c in self._cards if c.card.rarity == CardRarity.Rare]
    
    @property
    def ultra_rare_cards(self) -> List[CardCount]:
        
        return [c for c in self._cards if c.card.rarity == CardRarity.UltraRare]
    
    @property
    def legendary_cards(self) -> List[CardCount]:
        
        return [c for c in self._cards if c.card.rarity == CardRarity.Legendary]
    
################################################################################
    def has_card(self, card: TradingCard) -> bool:
        
        return any(c.card == card for c in self._cards)
    
################################################################################
    def status(self) -> Embed:
        
        series_str = ""
        for series in self.card_manager.series_list:
            series_str += (
                f"{series.order}. {series.name}: "
                f"`{len([c for c in self._cards if c.card.series == series])}`\n"
            )
        
        return U.make_embed(
            title=f"__`{self._user.display_name}'s` Collection__",
            description=(
                f"[`{len(self.common_cards)}`] **Common Cards**\n"
                f"[`{len(self.uncommon_cards)}`] **Uncommon Cards**\n"
                f"[`{len(self.rare_cards)}`] **Rare Cards**\n"
                f"[`{len(self.ultra_rare_cards)}`] **Ultra Rare Cards**\n"
                f"[`{len(self.legendary_cards)}`] **Legendary Cards**\n\n"
                
                f"[`{len(self._cards)}`] **Total Cards**"
            ),
            fields=[
                EmbedField(
                    name="__Series Breakdown__",
                    value=series_str or "`No cards in collection.`",
                    inline=False
                )
            ]
        )
        
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = CardCollectionMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
    async def add_card(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Add Single Card__",
            description=(
                "Please select the series of the card you would like to add."
            )
        )
        series = await self.card_manager._select_series(interaction, prompt)
        if series is None:
            return
        
        prompt = U.make_embed(
            title="__Add Single Card__",
            description=(
                "Please select the card you would like to add."
            )
        )
        card = await series._select_card(interaction, prompt)
        if card is None:
            return
        
        count_obj = self.get_card(card)
        if count_obj is None:
            count_obj = CardCount.new(self, card)
            self._cards.append(count_obj)
        else:
            count_obj.quantity += 1
            
        confirm = U.make_embed(
            title="__Card Added__",
            description=(
                f"Successfully added `{card.name}` to this user's collection!"
            )
        )
        await interaction.respond(embed=confirm, ephemeral=True)
    
################################################################################
    def get_card(self, card: TradingCard) -> Optional[CardCount]:
        
        return next((c for c in self.cards if c.card == card), None)
    
################################################################################
