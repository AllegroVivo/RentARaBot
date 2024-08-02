from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Any, Tuple

from discord import Interaction

from UI.Common import BasicTextModal, FroggeSelectView
from Enums import CharacterGroup, CardRarity
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import TradingCard, RentARaBot, CardSeries
################################################################################

__all__ = ("TradingCardDetails", )

D = TypeVar("D", bound="TradingCardDetails")

################################################################################
class TradingCardDetails:

    __slots__ = (
        "_parent",
        "_name",
        "_description",
        "_group",
        "_image",
        "_rarity",
    )
    
################################################################################
    def __init__(self, parent: TradingCard, **kwargs) -> None:

        self._parent: TradingCard = parent
        
        self._name: Optional[str] = kwargs.get("name")
        self._description: Optional[str] = kwargs.get("description")
        self._image: Optional[str] = kwargs.get("image")
        
        self._group: Optional[CharacterGroup] = kwargs.get("group")
        self._rarity: CardRarity = kwargs.get("rarity", CardRarity.Common)
    
################################################################################
    @classmethod
    def load(cls: Type[D], parent: TradingCard, data: Tuple[Any, ...]) -> D:
        
        return cls(
            parent=parent,
            name=data[1],
            description=data[2],
            group=CharacterGroup(data[3]) if data[3] else None,
            image=data[4],
            rarity=CardRarity(data[5]),
        )
    
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._parent.bot
    
################################################################################
    @property
    def name(self) -> Optional[str]:
        
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        
        self._name = value
        self.update()
        
################################################################################
    @property
    def description(self) -> Optional[str]:
        
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        
        self._description = value
        self.update()
        
################################################################################
    @property
    def group(self) -> Optional[CharacterGroup]:
        
        return self._group
    
    @group.setter
    def group(self, value: CharacterGroup) -> None:
        
        self._group = value
        self.update()
        
################################################################################
    @property
    def series(self) -> Optional[CardSeries]:
        
        return self._parent.series

################################################################################
    @property
    def image(self) -> Optional[str]:
        
        return self._image
    
    @image.setter
    def image(self, value: str) -> None:
        
        self._image = value
        self.update()
        
################################################################################
    @property
    def rarity(self) -> CardRarity:
        
        return self._rarity
    
    @rarity.setter
    def rarity(self, value: CardRarity) -> None:
        
        self._rarity = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.trading_card_details(self)
        
################################################################################
    async def set_name(self, interaction: Interaction) -> None:
        
        modal = BasicTextModal(
            title="Set Card Name",
            attribute="Name",
            cur_val=self.name,
            example="eg. 'Sifu Komodo'",
            max_length=50,
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        self.name = modal.value
    
################################################################################
    async def set_image(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="Set Card Image",
            description=(
                "Please provide an image to use for this card."
            ),
        )
        image_url = await U.wait_for_image(interaction, prompt)
        if image_url is None:
            return
        
        self.image = image_url
        
################################################################################
    async def set_group(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="Set Card Subgroup",
            description=(
                "Please select the subgroup this card belongs to."
            ),
        )
        view = FroggeSelectView(interaction.user, CharacterGroup.select_options())
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.group = CharacterGroup(int(view.value))
        
################################################################################
    async def set_rarity(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="Set Card Rarity",
            description=(
                "Please select the rarity for this card."
            ),
        )
        view = FroggeSelectView(interaction.user, CardRarity.select_options())
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.rarity = CardRarity(int(view.value))
        
################################################################################
