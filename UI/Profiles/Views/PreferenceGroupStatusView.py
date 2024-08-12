from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import PreferenceGroup
################################################################################

__all__ = ("PreferenceGroupStatusView",)

################################################################################
class PreferenceGroupStatusView(FroggeView):

    def __init__(self, owner: User, group: PreferenceGroup):
        
        super().__init__(owner, group)
        
        button_list = [
            BedroomPrefButton(),
            RacialPrefsButton(),
            RacialRestsButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class BedroomPrefButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Bedroom Preference",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_bedroom_pref(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RacialPrefsButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Racial Preference(s)",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_preferences(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class RacialRestsButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Racial Restriction(s)",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_restrictions(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
