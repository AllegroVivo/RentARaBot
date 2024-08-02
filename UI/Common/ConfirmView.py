from __future__ import annotations

from typing import TYPE_CHECKING, Union

from discord import ButtonStyle, Interaction, Member, User
from discord.ui import button

from .FroggeView import FroggeView

if TYPE_CHECKING:
    pass
################################################################################

__all__ = ("ConfirmView",)

################################################################################
class ConfirmView(FroggeView):

    def __init__(self, owner: Union[Member, User], **kwargs):
        
        super().__init__(owner, None, **kwargs)

    @button(
        style=ButtonStyle.success,
        label="Confirm",
        disabled=False,
        row=0
    )
    async def confirm(self, _, interaction: Interaction):
        self.value = True
        self.complete = True

        await interaction.response.edit_message()
        await self.stop()  # type: ignore

################################################################################
