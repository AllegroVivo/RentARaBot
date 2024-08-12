from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Any, Dict

from discord import Embed, EmbedField, Interaction, SelectOption

from Assets import BotEmojis
from Enums import CharacterGroup, CardRarity
from .TradingCardStats import TradingCardStats
from .TradingCardDetails import TradingCardDetails
from UI.Common import ConfirmCancelView, BasicTextModal, InstructionsInfo
from UI.TradingCardGame import TradingCardStatusView
from Utilities import Utilities as U, FroggeColor

if TYPE_CHECKING:
    from Classes import CardSeries, RentARaBot, CardManager
################################################################################

__all__ = ("TradingCard", )

TC = TypeVar("TC", bound="TradingCard")

################################################################################
class TradingCard:

    __slots__ = (
        "_id",
        "_parent",
        "_details",
        "_stats",
        "_index",
    )
    
################################################################################
    def __init__(self, parent: CardSeries, _id: str, index: str, **kwargs) -> None:

        self._id: str = _id
        self._parent: CardSeries = parent
        self._index: str = index
        
        self._details: TradingCardDetails = kwargs.get("details") or TradingCardDetails(self)
        self._stats: TradingCardStats = kwargs.get("stats") or TradingCardStats(self)
    
################################################################################
    @classmethod
    def new(cls: Type[TC], series: CardSeries) -> TC:
        
        new_index = f"{(len(series) + 1):03d}"
        new_id = series.bot.database.insert.trading_card(series.id, new_index)
        
        return cls(series, new_id, new_index)
    
################################################################################
    @classmethod
    def load(cls: Type[TC], series: CardSeries, data: Dict[str, Any]) -> TC:
        
        self: TC = cls.__new__(cls)
        
        self._parent = series
        self._id = data["card"][0]
        self._index = data["card"][2]
        
        self._details = TradingCardDetails.load(self, data["details"])
        self._stats = TradingCardStats.load(self, data["stats"])

        return self
    
################################################################################
    def __eq__(self, other: TradingCard) -> bool:
        
        return self.id == other.id
    
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._parent.bot
    
################################################################################
    @property
    def card_manager(self) -> CardManager:
        
        return self._parent.card_manager
    
################################################################################
    @property
    def id(self) -> str:
        
        return self._id
    
################################################################################
    @property
    def name(self) -> Optional[str]:
        
        return self._details.name
    
################################################################################
    @property
    def index(self) -> str:
        
        return self._index
    
    @index.setter
    def index(self, value: str) -> None:
            
        self._index = value
        self.update()
        
################################################################################
    @property
    def group(self) -> Optional[CharacterGroup]:
        
        return self._details.group
    
################################################################################
    @property
    def series(self) -> Optional[CardSeries]:
        
        return self._parent
    
################################################################################
    @property
    def image(self) -> Optional[str]:
        
        return self._details.image
    
################################################################################
    @property
    def rarity(self) -> CardRarity:
        
        return self._details.rarity
    
################################################################################
    @property
    def bad(self) -> Optional[int]:
        
        return self._stats.bad_stat
    
    @property
    def bad_split(self) -> Optional[str]:
        
        if self.bad is None:
            return
        
        str_val = str(self.bad).zfill(3)
        return f"[{str_val[0]}]-[{str_val[1]}]-[{str_val[2]}]"
    
################################################################################
    @property
    def battle(self) -> Optional[int]:
        
        return self._stats.battle_stat
    
################################################################################
    @property
    def nsfw(self) -> Optional[int]:
        
        return self._stats.nsfw_stat
    
################################################################################
    @property
    def sfw(self) -> Optional[int]:
        
        return self._stats.sfw_stat
    
################################################################################
    @property
    def die_marker(self) -> Optional[int]:
        
        return self._stats.die_marker
    
################################################################################
    @property
    def is_filled_out(self) -> bool:
        
        return all([
            self.name is not None,
            self.group is not None,
            self.image is not None,
            self.rarity is not None,
            self.battle is not None,
            self.nsfw is not None,
            self.sfw is not None,
            self.die_marker is not None,
            self.bad is not None
        ]) 
    
################################################################################
    @property
    def rarity_color(self) -> FroggeColor:
        
        match self.rarity:
            case CardRarity.Common:
                return FroggeColor(int("808080", 16))
            case CardRarity.Uncommon:
                return FroggeColor(int("00FF00", 16))
            case CardRarity.Rare:
                return FroggeColor(int("0000FF", 16))
            case CardRarity.UltraRare:
                return FroggeColor(int("800080", 16))
            case CardRarity.Legendary:
                return FroggeColor(int("FFA500", 16))
            case _:
                raise ValueError(f"Invalid Rarity: {self.rarity.proper_name}")
    
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.trading_card(self)
        
################################################################################
    def status(self) -> Embed:
        
        battle_stat = f"{self.battle:03d}" if self.battle is not None else "---"
        nsfw_stat = f"{self.nsfw:03d}" if self.nsfw is not None else "---"
        sfw_stat = f"{self.sfw:03d}" if self.sfw is not None else "---"
        
        return U.make_embed(
            color=self.rarity_color,
            title=f"__Trading Card Details for `{self.name or 'Unnamed Card'}`__",
            description=(
                f"**Subgroup:** `{self.group.proper_name if self.group else 'Not Set'}`\n"
                f"**Series:** `{self.series.name}`\n"
                f"**Rarity:** `{self.rarity.proper_name}`"
            ),
            fields=[
                EmbedField(
                    name="__Card Stats__",
                    value=(
                        f"{BotEmojis.Die} **[DIE]:** `{self.die_marker or '---'}`\n"
                        f"{BotEmojis.DoNotEnter} **[BAD]:** `{self.bad_split or '---'}`\n"
                        f"{BotEmojis.Sword} **[BATTLE]:** `{battle_stat}`\n"
                        f"{BotEmojis.HeartSparkle} **[NSFW]:** `{nsfw_stat}`\n"
                        f"{BotEmojis.Diamond} **[SFW]:** `{sfw_stat}`"
                    ),
                    inline=False
                ),
            ],
            thumbnail_url=self.image,
            footer_text=f"Card Index: {self.index}/{len(self.series):03d}"
        )
        
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = TradingCardStatusView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
    async def set_name(self, interaction: Interaction) -> None:
        
        await self._details.set_name(interaction)
        
################################################################################
    async def set_group(self, interaction: Interaction) -> None:
        
        await self._details.set_group(interaction)
        
################################################################################
    async def set_image(self, interaction: Interaction) -> None:
        
        await self._details.set_image(interaction)
        
################################################################################
    async def set_rarity(self, interaction: Interaction) -> None:
        
        await self._details.set_rarity(interaction)
        
################################################################################
    async def set_index(self, interaction: Interaction) -> None:
        
        modal = BasicTextModal(
            title="Set Card Index",
            attribute="Index Value",
            example="eg. '042' or '003-a'",
            cur_val=self.index,
            max_length=5,
            instructions=InstructionsInfo(
                placeholder="Enter the card's index value.",
                value=(
                    "Enter the card's index value, using a format "
                    "of '###' or '###-a' (for alternate cards).\n"
                )
            )
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        self.index = modal.value
        
################################################################################
    def select_option(self) -> SelectOption:
        
        return SelectOption(
            label=self.name or "Unnamed Card",
            value=self.id,
            description=f"ID: {self.index} ({self.rarity.proper_name})"
        )
    
################################################################################
    async def remove(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Card__",
            description=(
                "__*Are you sure you want to remove this card?*__\n\n"
                
                "**This action is irreversible and will delete the card from the series.\n"
                "All data associated with this card will be lost.**"
            ),
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.bot.database.delete.trading_card(self)
        self._parent.cards.remove(self)
        
################################################################################
    async def set_stats(self, interaction: Interaction) -> None:
        
        await self._stats.set_values(interaction)
                    
################################################################################
