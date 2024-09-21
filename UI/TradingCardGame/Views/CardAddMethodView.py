from __future__ import annotations

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton
################################################################################

__all__ = ("CardAddMethodView",)

################################################################################
class CardAddMethodView(FroggeView):

    def __init__(self, owner: User):
        
        super().__init__(owner, None)
        
        button_list = [
            AddViaIDButton(),
            # AddViaNameButton(),
            AddViaMenuButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class AddViaIDButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Add Using ID",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.value = 1, interaction
        self.view.complete = True
        
        await self.view.stop()  # type: ignore
        
################################################################################
class AddViaNameButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Add Using Name",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.complete = True

        await self.view.stop()  # type: ignore
        
################################################################################
class AddViaMenuButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Add via Select Menu",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.value = 3, interaction
        self.view.complete = True

        await self.view.stop()  # type: ignore
        
################################################################################
