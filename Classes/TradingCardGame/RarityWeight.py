from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar, Any, Tuple

from discord import Embed, EmbedField, Interaction, SelectOption

from UI.Common import BasicNumberModal, ConfirmCancelView
from Enums import CardRarity
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import BoosterCardConfig, RentARaBot
################################################################################

__all__ = ("RarityWeight", )

RW = TypeVar("RW", bound="RarityWeight")

################################################################################
class RarityWeight:

    __slots__ = (
        "_id",
        "_parent",
        "_rarity",
        "_weight",
    )
    
################################################################################
    def __init__(self, parent: BoosterCardConfig, _id: str, rarity: CardRarity, weight: int = 1) -> None:

        self._id: str = _id
        self._parent: BoosterCardConfig = parent
        
        self._rarity: CardRarity = rarity
        self._weight: int = weight
    
################################################################################
    @classmethod
    def new(cls: Type[RW], parent: BoosterCardConfig, rarity: CardRarity) -> RW:
        
        new_id = parent.bot.database.insert.rarity_weight(parent.id, rarity.value)
        return cls(parent, new_id, rarity)
    
################################################################################
    @classmethod
    def load(cls: Type[RW], parent: BoosterCardConfig, data: Tuple[Any, ...]) -> RW:
        
        return cls(
            parent=parent, 
            _id=data[0], 
            rarity=CardRarity(data[2]), 
            weight=data[3]
        )
    
################################################################################
    def __eq__(self, other: RarityWeight) -> bool:
        
        return self.id == other.id
    
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
    def rarity(self) -> CardRarity:
        
        return self._rarity
    
################################################################################
    @property
    def weight(self) -> int:

        return self._weight
    
    @weight.setter
    def weight(self, value: int) -> None:
        
        self._weight = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.rarity_weight(self)
        
################################################################################
    def delete(self) -> None:
        
        self.bot.database.delete.rarity_weight(self)
        self._parent.weights.remove(self)
        
################################################################################
    def select_option(self) -> SelectOption:
        
        return SelectOption(
            label=self.rarity.proper_name,
            value=self.id
        )
    
################################################################################
    async def set_weight(self, interaction: Interaction) -> None:
        
        modal = BasicNumberModal(
            title="Set Booster Card Rarity Weight",
            attribute="Weight",
            cur_val=self.weight
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        self.weight = modal.value
    
################################################################################
    async def remove(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Rarity__",
            description=(
                f"Are you sure you want to remove the `{self.rarity.proper_name}` "
                f"rarity from this card slot?"
            )
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.delete()
        
################################################################################
