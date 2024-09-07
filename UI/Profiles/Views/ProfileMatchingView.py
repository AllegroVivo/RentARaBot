from __future__ import annotations

from typing import TYPE_CHECKING, List

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Profile
################################################################################

__all__ = ("ProfileMatchingView",)

################################################################################
class ProfileMatchingView(FroggeView):

    def __init__(self, owner: User, profiles: List[Profile]):
        
        super().__init__(owner, None)
        
        button_list = [
            ProfileContactButton(p, 0 if i <= 2 else 1) 
            for i, p in enumerate(profiles)
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class ProfileContactButton(FroggeButton):
    
    def __init__(self, profile: Profile, row: int):
        
        super().__init__(
            style=ButtonStyle.primary,
            label=f"Contact {profile.name}",
            disabled=False,
            row=row
        )
        
        self.profile = profile
        
    async def callback(self, interaction: Interaction):
        await self.profile.make_contact(interaction)
        
################################################################################
