from __future__ import annotations
from discord.ui import InputText
from discord import InputTextStyle, Interaction
from UI.Common import FroggeModal
################################################################################

__all__ = ("CharacterNameModal",)

################################################################################
class CharacterNameModal(FroggeModal):

    def __init__(self):

        super().__init__(title="Character Name Entry")
        
        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="Forename",
                placeholder="eg. 'Allegro'",
                max_length=15,
                required=True,
            )
        )

        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="Surname",
                placeholder="eg. 'Vivo'",
                max_length=15,
                required=True,
            )
        )
        
    async def callback(self, interaction: Interaction):
        self.value = (
            self.children[0].value,
            self.children[1].value
        )
        self.complete = True
        
        await self.dummy_response(interaction)
        self.stop()
        
################################################################################
