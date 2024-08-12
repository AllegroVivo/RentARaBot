from __future__ import annotations

from typing import TYPE_CHECKING, List, Any, Dict

from discord import Embed, Interaction

from Errors import MaxItemsReached
from UI.Common import FroggeSelectView
from UI.TradingCardGame import BoosterPackConfigMenuView
from Utilities import Utilities as U
from .BoosterCardConfig import BoosterCardConfig

if TYPE_CHECKING:
    from Classes import CollectionManager, RentARaBot
################################################################################

__all__ = ("BoosterPackConfig",)

################################################################################
class BoosterPackConfig:

    __slots__ = (
        "_mgr",
        "_configs",
    )
    
    MAX_CONFIGS = 10

################################################################################
    def __init__(self, mgr: CollectionManager) -> None:

        self._mgr: CollectionManager = mgr
        
        self._configs: List[BoosterCardConfig] = []

################################################################################
    def load_all(self, data: Dict[str, Any]) -> None:
        
        self._configs = [BoosterCardConfig.load(self, d) for d in data["card_configs"]]

################################################################################
    def __getitem__(self, config_id: str) -> BoosterCardConfig:
        
        return next((c for c in self.card_configs if c.id == config_id), None)
    
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
    def card_configs(self) -> List[BoosterCardConfig]:
        
        self._configs.sort(key=lambda x: x.order)
        return self._configs
    
################################################################################
    @property
    def slots(self) -> int:

        return len(self.card_configs)
        
################################################################################
    def status(self) -> Embed:
        
        return U.make_embed(
            title="__Booster Pack Configuration__",
            description=f"**Current Pack Slots: [`{self.slots}`]**",
            fields=[c.field() for c in self.card_configs]
        )
        
################################################################################
    async def main_menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = BoosterPackConfigMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
    async def add_card_config(self, interaction: Interaction) -> None:
        
        if len(self.card_configs) >= self.MAX_CONFIGS:
            error = MaxItemsReached("Booster Card Configurations", self.MAX_CONFIGS)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        new_config = BoosterCardConfig.new(self)
        self._configs.append(new_config)
        
        await new_config.menu(interaction)
    
################################################################################
    async def modify_card_config(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Modify Booster Card Config__",
            description="Please select the card slot you would like to modify."
        )
        view = FroggeSelectView(interaction.user, [c.select_option() for c in self.card_configs])
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        config = self[view.value]
        await config.menu(interaction)
    
################################################################################
    async def remove_card_config(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Booster Card Config__",
            description="Please select the card slot you would like to modify."
        )
        view = FroggeSelectView(interaction.user, [c.select_option() for c in self.card_configs])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        config = self[view.value]
        await config.remove(interaction)
    
################################################################################
