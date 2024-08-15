from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, CloseMessageButton, FroggeButton

if TYPE_CHECKING:
    from Classes import CardCollection
################################################################################

__all__ = ("UserCollectionMenuView",)

################################################################################
class UserCollectionMenuView(FroggeView):

    def __init__(self, owner: User, coll: CardCollection):
        
        super().__init__(owner, coll)
        
        button_list = [
            EditDecksButton(),
            ViewCollectionButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
        
################################################################################
class EditDecksButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Edit Battle Deck(s)",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.edit_decks(interaction)
        
################################################################################
class ViewCollectionButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="View My Collection",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.ctx.view(interaction)
        
################################################################################
