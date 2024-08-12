from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import TCGManager
################################################################################

__all__ = ("TradingCardMainMenuView",)

################################################################################
class TradingCardMainMenuView(FroggeView):

    def __init__(self, owner: User, mgr: TCGManager):
        
        super().__init__(owner, mgr)
        
        button_list = [
            TradingCardsSetupButton(),
            BoosterPackManagementButton(),
            CollectionMenuButton(),
            BattleSystemConfigButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class TradingCardsSetupButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Configure Trading Cards",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.trading_cards_menu(interaction)
        
################################################################################
class BoosterPackManagementButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Configure Booster Pack Behavior",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.booster_management_menu(interaction)
        
################################################################################
class CollectionMenuButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify User Collections",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.collections_menu(interaction)
        
################################################################################
class BattleSystemConfigButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Configure Battle System",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.battle_configuration_menu(interaction)
        
################################################################################
