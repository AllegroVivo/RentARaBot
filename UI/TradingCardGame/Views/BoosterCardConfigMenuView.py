from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import BoosterCardConfig
################################################################################

__all__ = ("BoosterCardConfigMenuView",)

################################################################################
class BoosterCardConfigMenuView(FroggeView):

    def __init__(self, owner: User, config: BoosterCardConfig):
        
        super().__init__(owner, config)
        
        button_list = [
            AddRarityButton(),
            ModifyRarityButton(),
            RemoveRarityButton(),
            ToggleAlwaysNewButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class AddRarityButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Rarity Weight",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_rarity(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ModifyRarityButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Rarity",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_rarity(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveRarityButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Rarity",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_rarity(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ToggleAlwaysNewButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Toggle Always New",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.toggle_always_new(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
