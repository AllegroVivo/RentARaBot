from __future__ import annotations

from typing import TYPE_CHECKING, Union

from discord import ButtonStyle, Interaction, Member, User
from discord.ui import button

from .FroggeView import FroggeView

if TYPE_CHECKING:
    pass
################################################################################

__all__ = ("ConfirmCancelView",)

################################################################################
class ConfirmCancelView(FroggeView):

    def __init__(self, owner: Union[Member, User], return_interaction: bool = False, **kwargs):
        
        self.return_interaction: bool = return_interaction
        super().__init__(owner, None, **kwargs)

    @button(
        style=ButtonStyle.success,
        label="Confirm",
        disabled=False,
        row=0
    )
    async def confirm(self, _, interaction: Interaction):
        self.value = (
            True if not self.return_interaction
            else (True, interaction)
        )
        self.complete = True

        if not self.return_interaction:
            await interaction.response.edit_message()
        await self.stop()  # type: ignore

    @button(
        style=ButtonStyle.danger,
        label="Cancel",
        disabled=False,
        row=0
    )
    async def cancel(self, _, interaction: Interaction):
        self.value = False
        self.complete = True

        await interaction.response.edit_message()
        await self.stop()  # type: ignore

################################################################################
