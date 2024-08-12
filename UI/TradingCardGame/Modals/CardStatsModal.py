from __future__ import annotations

from typing import Optional, Tuple

from discord import InputTextStyle, Interaction
from discord.ui import InputText

from Errors._Error import ErrorMessage
from UI.Common import FroggeModal
################################################################################

__all__ = ("CardStatsModal",)

################################################################################
class CardStatsModal(FroggeModal):

    def __init__(self, current_values: Tuple[Optional[int], ...]):
        
        super().__init__(title="Set Card Stats")

        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="Die Marker",
                placeholder="Enter Die Marker Value",
                value=str(current_values[0]) if current_values[0] is not None else None,
                required=True,
                min_length=1,
                max_length=1,
            )
        )
        
        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="BAD",
                placeholder="Enter BAD Value",
                value=f"{current_values[1]:03d}" if current_values[1] is not None else None,
                required=True,
                min_length=3,
                max_length=3,
            )
        )
        
        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="BATTLE",
                placeholder="Enter BATTLE Value",
                value=f"{current_values[2]:03d}" if current_values[2] is not None else None,
                required=True,
                min_length=3,
                max_length=3,
            )
        )
        
        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="NSFW",
                placeholder="Enter NSFW Value",
                value=f"{current_values[3]:03d}" if current_values[3] is not None else None,
                required=True,
                min_length=3,
                max_length=3,
            )
        )
        
        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="SFW",
                placeholder="Enter SFW Value",
                value=f"{current_values[4]:03d}" if current_values[4] is not None else None,
                required=True,
                min_length=3,
                max_length=3,
            )
        )
        
    async def callback(self, interaction: Interaction):
        values = []
        for i in range(5):
            raw = self.children[i].value or None
            try:
                value = int(raw)
            except ValueError:
                error = InvalidNumber(raw)
                await interaction.respond(embed=error, ephemeral=True)
                return
            
            values.append(value)
            
        self.value = tuple(values)
        self.complete = True
        
        await self.dummy_response(interaction)
        self.stop()

################################################################################
class InvalidNumber(ErrorMessage):

    def __init__(self, value: str):
        super().__init__(
            title="Invalid Number",
            description=f"Invalid Value: {value}",
            message="The numerical value you entered is invalid.",
            solution="Enter a whole number.",
        )

################################################################################
