from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Attachment, Bot, TextChannel

from Classes.Database import Database
from .GuildManager import GuildManager

if TYPE_CHECKING:
    from Classes import GuildData
################################################################################

__all__ = ("RentARaBot",)

################################################################################
class RentARaBot(Bot):

    __slots__ = (
        "_img_dump",
        "_db",
        "_guild_mgr",
    )
    
    IMAGE_DUMP = 991902526188302427

################################################################################
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._img_dump: TextChannel = None  # type: ignore

        self._db: Database = Database(self)        
        self._guild_mgr: GuildManager = GuildManager(self)
        
################################################################################
    def __getitem__(self, guild_id: int) -> GuildData:
        
        return self._guild_mgr[guild_id]
    
################################################################################
    def __iter__(self):
        
        return iter(self._guild_mgr)
    
################################################################################    
    @property
    def database(self) -> Database:
        
        return self._db
    
################################################################################
    @property
    def guild_manager(self) -> GuildManager:
        
        return self._guild_mgr
    
################################################################################
    async def load_all(self) -> None:

        print("Initializing... Fetching image dump...")
        # Image dump can be hard-coded since it's never going to be different.
        self._img_dump = await self.fetch_channel(self.IMAGE_DUMP)
        
        # Generate all GuildDatas to load database info into.
        for g in self.guilds:
            self._guild_mgr.add_guild(g)

        print("Initializing... Retrieving database payload...")
        # Retrieve (and parse) database payload.
        payload = self.database.load_all()

        print("Initializing... Loading Frogge guilds...")  
        # Drop into each guild and load their data.
        for frogge in self._guild_mgr.fguilds:
            await frogge.load_all(payload[frogge.guild_id])

        print("Done!")
    
################################################################################
    async def dump_image(self, image: Attachment) -> str:
        """Dumps an image into the image dump channel and returns the URL.
        
        Parameters:
        -----------
        image : :class:`Attachment`
            The image to dump.
            
        Returns:
        --------
        :class:`str`
            The URL of the dumped image.
        """
        
        file = await image.to_file()
        post = await self._img_dump.send(file=file)   # type: ignore

        return post.attachments[0].url

################################################################################
    