from __future__ import annotations

import random
from typing import TYPE_CHECKING, Type, TypeVar, Any, Dict, List, Optional

from discord import Embed, EmbedField, Interaction, SelectOption

from Enums import CardRarity
from UI.Common import FroggeSelectView, ConfirmCancelView
from Utilities import Utilities as U
from UI.TradingCardGame import BoosterCardConfigMenuView
from .RarityWeight import RarityWeight

if TYPE_CHECKING:
    from Classes import BoosterPackConfig, RentARaBot, CardCollection, TradingCard, CardManager
################################################################################

__all__ = ("BoosterCardConfig", )

BCC = TypeVar("BCC", bound="BoosterCardConfig")

################################################################################
class BoosterCardConfig:

    __slots__ = (
        "_id",
        "_parent",
        "_order",
        "_weights",
        "_always_new",
    )
    
################################################################################
    def __init__(self, parent: BoosterPackConfig, _id: str, order: int, **kwargs) -> None:

        self._id: str = _id
        self._parent: BoosterPackConfig = parent
        self._order: int = order

        self._weights: List[RarityWeight] = kwargs.get("weights", [])
        self._always_new: bool = kwargs.get("always_new", False)
    
################################################################################
    @classmethod
    def new(cls: Type[BCC], parent: BoosterPackConfig) -> BCC:
        
        order = len(parent.card_configs) + 1
        new_id = parent.bot.database.insert.booster_card_config(parent.guild_id, order)
        
        return cls(parent, new_id, order)
    
################################################################################
    @classmethod
    def load(cls: Type[BCC], parent: BoosterPackConfig, data: Dict[str, Any]) -> BCC:
        
        config = data["config"]
        
        self: BCC = cls.__new__(cls)
        
        self._id = config[0]
        self._parent = parent
        self._order = config[2]
        
        self._weights = [RarityWeight.load(self, d) for d in data["weights"]]
        self._always_new = config[3]
        
        return self
    
################################################################################
    def __eq__(self, other: BoosterCardConfig) -> bool:
        
        return self.id == other.id
    
################################################################################
    def __getitem__(self, weight_id: str) -> Optional[RarityWeight]:
    
        return next((w for w in self.weights if w.id == weight_id), None)
    
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._parent.bot
    
################################################################################
    @property
    def card_manager(self) -> CardManager:
        
        return self._parent._mgr.card_manager
    
################################################################################
    @property
    def id(self) -> str:
        
        return self._id
    
################################################################################
    @property
    def order(self) -> int:
        
        return self._order
    
################################################################################
    @property
    def weights(self) -> List[RarityWeight]:
        
        self._weights.sort(key=lambda x: x.rarity.value)
        return self._weights
    
################################################################################
    @property
    def always_new(self) -> bool:
        
        return self._always_new
    
    @always_new.setter
    def always_new(self, value: bool) -> None:
        
        self._always_new = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.booster_card_config(self)
        
################################################################################
    def delete(self) -> None:
        
        self.bot.database.delete.booster_card_config(self)
        self._parent.card_configs.remove(self)
        
################################################################################
    def select_option(self) -> SelectOption:
        
        return SelectOption(
            label=f"Pack Slot #{self.order}",
            value=self.id
        )
    
################################################################################
    def field(self) -> EmbedField:
        
        weight_total = sum(w.weight for w in self.weights)
        rarity_list = ""
        
        for weight in self.weights:
            rarity_list += (
                f"**{weight.rarity.proper_name}** - [`{((weight.weight / weight_total) * 100):.1f}%`]\n"     
            )
        if not rarity_list:
            rarity_list = "`No Rarities Assigned`"
        
        return EmbedField(
            name=f"__Pack Slot #{self.order}__",
            value=(
                f"**Always New:** [`{self.always_new}`]\n"
                f"{rarity_list}"
            ),
            inline=True
        )
    
################################################################################
    def status(self) -> Embed:
        
        return U.make_embed(
            title="__Booster Card Configuration__",
            fields=[self.field()]
        )
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = BoosterCardConfigMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
    async def add_rarity(self, interaction: Interaction) -> None:
        
        options = CardRarity.select_options()
        options = [o for o in options if o.value not in [w.rarity.value for w in self.weights]]
        
        prompt = U.make_embed(
            title="__Add Rarity__",
            description="Please select the rarities you would like to assign to this card slot."
        )
        view = FroggeSelectView(interaction.user, options)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        for value in view.value:
            rarity = RarityWeight.new(self, CardRarity(int(value)))
            self.weights.append(rarity)
    
################################################################################
    async def modify_rarity(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Modify Rarity__",
            description="Please select the rarity you would like to modify the weight of."
        )
        view = FroggeSelectView(
            owner=interaction.user, 
            options=[w.select_option() for w in self.weights],
            return_interaction=True
        )
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        rarity_id, inter = view.value
        
        rarity = self[rarity_id]
        await rarity.set_weight(inter)
    
################################################################################
    async def remove_rarity(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Rarity__",
            description="Please select the rarity you would like to modify the weight of."
        )
        view = FroggeSelectView(interaction.user, [w.select_option() for w in self.weights])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        rarity = self[view.value]
        await rarity.remove(interaction)
    
################################################################################
    async def toggle_always_new(self, interaction: Interaction) -> None:
        
        self.always_new = not self.always_new
        await interaction.respond("** **",delete_after=0.1)
        
################################################################################
    async def remove(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Card Slot__",
            description=(
                f"Are you sure you want to remove card slot #{self.order} "
                f"from this booster pack configuration?\n\n"
                
                "**This action cannot be undone.**"
            )
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.delete()
        
################################################################################
    def get_card(self, coll: CardCollection) -> TradingCard:
        
        allowed_rarities = [w.rarity for w in self.weights]
        allowed = [c for c in self.card_manager.all_cards if c.rarity in allowed_rarities]
        if self.always_new:
            final_cards = [c for c in allowed if c not in coll]
        else:
            final_cards = allowed
            
        # If there are no cards to choose from, most likely meaning the user already 
        # owns all the available cards, then return a random card from the allowed list
        if not final_cards:
            return random.choice(allowed)

        rarity_weights = {w.rarity: w.weight for w in self.weights}
        cards = []
        weights = []
    
        for card in final_cards:
            cards.append(card)
            weights.append(rarity_weights[card.rarity])
    
        return random.choices(cards, weights=weights, k=1)[0]
    
################################################################################
    def get_weight(self, rarity: CardRarity) -> int:
        
        rarity_weight = next((w for w in self.weights if w.rarity == rarity), None)
        if rarity_weight is None:
            return 0
        
        return rarity_weight.weight
    
################################################################################
