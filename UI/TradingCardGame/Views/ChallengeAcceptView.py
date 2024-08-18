from __future__ import annotations

from typing import TYPE_CHECKING

from discord import User, Interaction, ButtonStyle
from discord.ui import Button

from UI.Common import FroggeView

if TYPE_CHECKING:
    from Classes import Challenge
################################################################################

__all__ = ("ChallengeAcceptView",)

################################################################################
class ChallengeAcceptView(FroggeView):

    def __init__(self, owner: User, challenge: Challenge):
        
        super().__init__(owner, challenge, timeout=600)
        self.add_item(AcceptChallengeButton(owner.id))

################################################################################
class AcceptChallengeButton(Button):
    
    def __init__(self, user_id: int):
        
        super().__init__(
            style=ButtonStyle.success,
            label="Accept Challenge",
            disabled=False,
            row=0,
            custom_id=f"accept_challenge:{user_id}"
        )
        
    async def callback(self, interaction: Interaction):
        self.view.value = True
        self.view.complete = True
        
        await self.view.stop()  # type: ignore
        await self.view.ctx.accept(interaction)
        
################################################################################
