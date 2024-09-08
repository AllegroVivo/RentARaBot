from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Form
################################################################################

__all__ = ("FormNotificationPartyView",)

################################################################################
class FormNotificationPartyView(FroggeView):

    def __init__(self, owner: User, option: Form):
        
        super().__init__(owner, option)
        
        button_list = [
            PickUserButton(),
            PickRoleButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_attributes()
        
################################################################################
class PickUserButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="User",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.value = True
        self.view.complete = True

        await self.view.dummy_response(interaction)
        await self.view.stop()  # type: ignore
        
################################################################################
class PickRoleButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Role",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.value = False
        self.view.complete = True

        await self.view.dummy_response(interaction)
        await self.view.stop()  # type: ignore
        
################################################################################
