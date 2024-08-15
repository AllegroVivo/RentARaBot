from __future__ import annotations

from typing import Union

from discord import ButtonStyle, Interaction, Member, User
from discord.ui import button

from UI.Common import FroggeView
################################################################################

__all__ = ("PublicPrivateView",)

################################################################################
class PublicPrivateView(FroggeView):

    def __init__(self, owner: Union[Member, User]):
        
        super().__init__(owner, None)

    @button(
        style=ButtonStyle.success,
        label="Public",
        disabled=False,
        row=0
    )
    async def confirm(self, _, interaction: Interaction):
        self.value = True
        self.complete = True

        await interaction.response.edit_message()
        await self.stop()  # type: ignore

    @button(
        style=ButtonStyle.secondary,
        label="Private",
        disabled=False,
        row=0
    )
    async def cancel(self, _, interaction: Interaction):
        self.value = False
        self.complete = True

        await interaction.response.edit_message()
        await self.stop()  # type: ignore

################################################################################
