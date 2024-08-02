from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import CollectionManager
################################################################################

__all__ = ("CollectionManagerMenuView",)

################################################################################
class CollectionManagerMenuView(FroggeView):

    def __init__(self, owner: User, mgr: CollectionManager):
        
        super().__init__(owner, mgr)
        
        button_list = [
            ModifyCollectionButton(),
            ViewCollectionButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class ModifyCollectionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Manually Modify a Collection",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.modify_collection(interaction)
        
################################################################################
class ViewCollectionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="View a Collection",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.view_collection(interaction)
        
################################################################################
