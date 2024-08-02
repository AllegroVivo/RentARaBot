from __future__ import annotations

from discord import ButtonStyle, Interaction
from discord.ext.pages import Paginator
from discord.ui import Button
################################################################################

__all__ = (
    "CloseMessageButton",
)

################################################################################
class CloseMessageButton(Button):

    def __init__(self):
        super().__init__(
            style=ButtonStyle.success,
            label="Close Message",
            disabled=False,
            row=4
        )

    async def callback(self, interaction: Interaction):
        self.view.value = False
        self.view.complete = True
        self.view._close_on_complete = True

        await interaction.response.edit_message()

        if isinstance(self.view, Paginator):
            await self.view.cancel()
        else:
            await self.view.stop()  # type: ignore

################################################################################
