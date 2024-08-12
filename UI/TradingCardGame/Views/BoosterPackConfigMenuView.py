from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import BoosterPackConfig
################################################################################

__all__ = ("BoosterPackConfigMenuView",)

################################################################################
class BoosterPackConfigMenuView(FroggeView):

    def __init__(self, owner: User, pack_config: BoosterPackConfig):
        
        super().__init__(owner, pack_config)
        
        button_list = [
            AddCardConfigButton(),
            ModifyCardConfigButton(),
            RemoveCardConfigButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class AddCardConfigButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add Booster Card",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_card_config(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class ModifyCardConfigButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Modify Card Config",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_card_config(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RemoveCardConfigButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Booster Card",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_card_config(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
