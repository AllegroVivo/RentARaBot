from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from Assets import BotEmojis
from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Profile
################################################################################

__all__ = ("PersonalityPreferencePickView",)

################################################################################
class PersonalityPreferencePickView(FroggeView):

    def __init__(self, owner: User, profile: Profile):
        
        super().__init__(owner, profile)
        
        button_list = [
            PersonalityMenuButton(),
            PreferencesMenuButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class PersonalityMenuButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Personality Elements",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.value = True
        self.view.complete = True
        
        await self.view.dummy_response(interaction)
        await self.view.stop()  # type: ignore
        
################################################################################
class PreferencesMenuButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Preferences & Activities",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.value = False
        self.view.complete = True

        await self.view.dummy_response(interaction)
        await self.view.stop()  # type: ignore
        
################################################################################
