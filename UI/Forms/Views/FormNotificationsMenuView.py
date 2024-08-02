from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import Form
################################################################################

__all__ = ("FormNotificationsMenuView",)

################################################################################
class FormNotificationsMenuView(FroggeView):

    def __init__(self, owner: User, form: Form):
        
        super().__init__(owner, form)
        
        button_list = [
            AddNotificationButton(),
            RemoveNotificationButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class AddNotificationButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Add User to Notify",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.add_notification(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.notifications_status(), view=self.view
        )
        
################################################################################
class RemoveNotificationButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove User to Notify",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.remove_notification(interaction)
        await self.view.edit_message_helper(
            interaction, embed=self.view.ctx.notifications_status(), view=self.view
        )
        
################################################################################
