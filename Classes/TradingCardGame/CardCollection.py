from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Dict, Type, TypeVar, Any, Tuple

from discord import User, Embed, EmbedField, Interaction, SelectOption
from Enums import CardRarity
from discord.ext.pages import Page
from Assets import BotEmojis, BotImages
from .CardCount import CardCount
from .DeckManager import DeckManager
from UI.Common import FroggeSelectView, Frogginator, CloseMessageView
from UI.TradingCardGame import CardCollectionMenuView, CardSelectView, UserCollectionMenuView
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
        "_boosters",
        "_deck_mgr",
    )
    
################################################################################
    def __init__(
        self,
        mgr: CollectionManager,
        _id: str,
        user: User, 
        cards: Optional[List[CardCount]] = None,
        boosters: Optional[int] = None,
        deck_mgr: Optional[DeckManager] = None
    ) -> None:

        self._id: str = _id
        self._mgr: CollectionManager = mgr
        
        self._user: User = user
        self._cards: List[CardCount] = cards or []
        self._deck_mgr: DeckManager = deck_mgr or DeckManager(self)
        
        self._boosters: int = boosters or 0
    
################################################################################
    @classmethod
    def new(cls: Type[CC], mgr: CollectionManager, user: User) -> CC:
        
        new_id = mgr.bot.database.insert.card_collection(mgr.guild_id, user.id)
        return cls(mgr, new_id, user)
    
################################################################################
    @classmethod
    async def load(cls: Type[CC], mgr: CollectionManager, data: Dict[str, Any]) -> CC:
        
        cdata = data["collection"]
        
        self = cls.__new__(cls)
        
        self._id = cdata[0]
        self._mgr = mgr
        
        self._user = await mgr.guild.get_or_fetch_member_or_user(data["collection"][2])
        self._cards = [CardCount.load(self, d) for d in data["cards"]]
        self._deck_mgr = DeckManager.load(self, data["decks"])
        
        self._boosters = cdata[3]
        
        return self
    
################################################################################
    def __getitem__(self, card: TradingCard) -> Optional[CardCount]:
        
        return next((c for c in self.cards if c.card == card), None)
    
################################################################################
    def __contains__(self, item: TradingCard) -> bool:
        
        return any(c.card == item for c in self._cards)
    
################################################################################
    def __len__(self) -> int:
        
        return sum(c.quantity for c in self._cards)
    
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
    def deck_manager(self) -> DeckManager:
        
        return self._deck_mgr
    
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
    @property
    def booster_packs(self) -> int:
        
        return self._boosters
    
    @booster_packs.setter
    def booster_packs(self, value: int) -> None:
        
        self._boosters = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.card_collection(self)
        
################################################################################
    def has_card(self, card: TradingCard) -> bool:
        
        return any(c.card == card for c in self._cards)
    
################################################################################
    def status(self) -> Embed:
        
        series_str = ""
        for series in self.card_manager.series_list:
            series_str += (
                f"{series.order}. {series.name}: "
                f"`{len([c for c in self._cards if c.card.series == series])}/{len(series)}`\n"
            )
        
        return U.make_embed(
            title=f"__`{self._user.display_name}'s` Collection__",
            description=(
                f"[`{len(self.common_cards)}`] **Common Cards**\n"
                f"[`{len(self.uncommon_cards)}`] **Uncommon Cards**\n"
                f"[`{len(self.rare_cards)}`] **Rare Cards**\n"
                f"[`{len(self.ultra_rare_cards)}`] **Ultra Rare Cards**\n"
                f"[`{len(self.legendary_cards)}`] **Legendary Cards**\n\n"
                
                f"[`{len(self._cards)}`] **Total Cards**\n"
                f"[`{self.booster_packs}`] **Booster Packs**\n\n"
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
    async def admin_menu(self, interaction: Interaction) -> None:
        
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
        series = await self.card_manager.select_series(interaction, prompt)
        if series is None:
            return
        
        prompt = U.make_embed(
            title="__Add Single Card__",
            description=(
                "Please select the card you would like to add."
            )
        )
        card = await series.select_card(interaction, prompt)
        if card is None:
            return
        
        self._add_card(card)
            
        confirm = U.make_embed(
            title="__Card Added__",
            description=(
                f"Successfully added `{card.name}` to this user's collection!"
            )
        )
        await interaction.respond(embed=confirm, ephemeral=True)
    
################################################################################
    async def remove_card(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Single Card__",
            description=(
                "Please select the series of the card you would like to remove."
            )
        )
        series = await self.card_manager.select_series(interaction, prompt)
        if series is None:
            return
        
        prompt = U.make_embed(
            title="__Remove Single Card__",
            description=(
                "Please select the card you would like to remove."
            )
        )
        view = CardSelectView(
            owner=interaction.user,
            options=[
                c.select_option() 
                for c 
                in [c.card for c in self.cards if c.card.series == series]
            ]
        )
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        card = self.card_manager.get_card(view.value)
        count_obj = self[card]
        if count_obj is None:
            error = U.make_embed(
                title="__Card Not Found__",
                description=(
                    f"`{card.name}` was not found in this user's collection."
                )
            )
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        await count_obj.remove(interaction)
        
################################################################################
    async def add_booster(self, interaction: Interaction) -> None:
        
        options = [
            SelectOption(label=str(i), value=str(i))
            for i in range(1, 11)
        ]
        prompt = U.make_embed(
            title="__Add Booster Pack__",
            description=(
                "Please select the number of booster packs you would like to add."
            )
        )
        view = FroggeSelectView(interaction.user, options)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return

        self.booster_packs += int(view.value)
        
################################################################################
    async def open_booster(self, interaction: Interaction) -> None:
        
        if not self.booster_packs:
            error = U.make_embed(
                title="__No Booster Packs__",
                description="You do not have any booster packs to open."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        cards = [
            cfg.get_card(self) for cfg in self._mgr.booster_config.card_configs
        ]
        
        self.booster_packs -= 1
        
        for card in cards:
            self._add_card(card)
            await interaction.respond(embed=card.status())

################################################################################
    def _add_card(self, card: TradingCard) -> None:
        
        count_obj = self[card]
        if count_obj is None:
            count_obj = CardCount.new(self, card)
            self._cards.append(count_obj)
        else:
            count_obj.quantity += 1
            
################################################################################
    async def view(self, interaction: Interaction) -> None:
        
        card_strs = []
        for series in self.card_manager.series_list:
            card_strs.extend(series.card_collection_strs(self))

        pages = []
        chunks = [card_strs[i:i + 20] for i in range(0, len(card_strs), 20)]
        
        total_owned = sum(c.quantity for c in self._cards)
        num_owned = len(self._cards)
        
        for chunk in chunks:
            embed = U.make_embed(
                title=f"__{self.user.display_name}'s Collection__",
                description="\n".join(chunk),
                thumbnail_url=BotImages.Pokedex,
                footer_text=(
                    f"Total: {total_owned} | "
                    f"Unique: {num_owned}/{self.card_manager.total_cards}"
                )
            )
            pages.append(Page(embeds=[embed]))
        
        froggintor = Frogginator(pages, custom_view=CloseMessageView(interaction.user))
        await froggintor.respond(interaction)
        
################################################################################
    async def edit_decks(self, interaction: Interaction) -> None:
        
        await self.deck_manager.main_menu(interaction)

################################################################################
    async def user_menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = UserCollectionMenuView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
