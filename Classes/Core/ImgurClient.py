from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional, Dict

import fleep
import requests
from discord import Interaction, Attachment
from dotenv import load_dotenv
from Errors import ImgurError

if TYPE_CHECKING:
    from Classes import RentARaBot
################################################################################

__all__ = ("ImgurClient", )

################################################################################
class ImgurClient:

    __slots__ = (
        "_state",
    )

    IMAGE_TYPES = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/apng",
        "image/tiff",
    ]
    API_URL = "https://api.imgur.com/3/"
    
################################################################################
    def __init__(self, state: RentARaBot) -> None:

        self._state: RentARaBot = state
    
################################################################################
    async def upload_image(self, interaction: Interaction, attachment: Attachment) -> Optional[str]:

        filename = attachment.filename
        await attachment.save(f"Files/{filename}")  # type: ignore

        if not self.check_type(filename):
            return

        files = {
            "image": open(f"Files/{filename}", "rb"),
        }
        payload = {
            "title": filename,
            "description": "Rent-a-Ra trading card game card",
        }

        request_url = self.API_URL + "image"
        request = requests.request("POST", request_url, files=files, data=payload, headers=self._headers())
        if not await self._check_response(request, interaction):
            return

        return request.json()["data"]["link"]
    
################################################################################
    def check_type(self, filename: str) -> bool:

        with open(f"Files/{filename}", "rb") as file:
            info = fleep.get(file.read(128))

        return info.mime[0] in self.IMAGE_TYPES
    
################################################################################
    @staticmethod
    def _headers() -> Dict[str, str]:
        
        load_dotenv()
        return {
            "Authorization": f"Client-ID {os.getenv('IMGUR_CLIENT_ID')}",
        }
    
################################################################################
    @staticmethod
    async def _check_response(request: requests.Response, interaction: Interaction) -> bool:
        
        if request.status_code == 200:
            return True
        else:
            error = ImgurError()
            await interaction.respond(embed=error, ephemeral=True)
            return False
    
################################################################################
