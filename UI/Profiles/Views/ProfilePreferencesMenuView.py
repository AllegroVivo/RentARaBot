from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import ProfilePreferences
################################################################################

__all__ = ("ProfilePreferencesMenuView",)

################################################################################
class ProfilePreferencesMenuView(FroggeView):

    def __init__(self, owner: User, prefs: ProfilePreferences):
        
        super().__init__(owner, prefs)
        
        button_list = [
            MalePrefsButton(),
            FemalePrefsButton(),
            NonBinPrefsButton(),
            PreferredActivitiesButton(),
            SetMusicPrefsButton(),
            SetZodiacSelfButton(),
            SetZodiacPartnersButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class MalePrefsButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Male Preferences",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_male_prefs(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class FemalePrefsButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Female Preferences",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_female_prefs(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class NonBinPrefsButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="NB Preferences",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_nb_prefs(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class PreferredActivitiesButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Favorite FFXIV Activities",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_activities(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetMusicPrefsButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set Music Preferences",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_music_prefs(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetZodiacSelfButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set MY Zodiac Sign",
            disabled=False,
            row=2
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_zodiac_self(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
class SetZodiacPartnersButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Set My Preferred Zodiac Partners",
            disabled=False,
            row=2
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.set_zodiac_partners(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.status(), view=self.view
        )
        
################################################################################
