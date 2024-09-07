from __future__ import annotations

from discord import User, Interaction, ButtonStyle

from UI.Common import FroggeView, FroggeButton
################################################################################

__all__ = ("CardBattleRollView",)

################################################################################
class CardBattleRollView(FroggeView):

    def __init__(self, owner: User):
        
        super().__init__(owner, None)
        self.add_item(RollDieButton())
        
################################################################################
class RollDieButton(FroggeButton):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Roll Die",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.value = True
        self.view.complete = True
        
        await self.view.dummy_response(interaction)
        await self.view.stop()  # type: ignore
        
################################################################################
