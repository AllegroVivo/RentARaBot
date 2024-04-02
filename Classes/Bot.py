from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Any, Optional

from discord import Attachment, Bot, TextChannel
from discord.abc import GuildChannel

from .GuildManager import GuildManager
from Utilities.Database import Database

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
    @property
    def database(self) -> Database:
        
        return self._db
    
################################################################################
    @property
    def guild_manager(self) -> GuildManager:
        
        return self._guild_mgr
    
################################################################################
    async def load_all(self) -> None:

        print("Fetching image dump...")
        # Image dump can be hard-coded since it's never going to be different.
        self._img_dump = await self.fetch_channel(991902526188302427)
        
        # Generate all GuildDatas to load database info into.
        for g in self.guilds:
            self._guild_mgr.add_guild(g)

        print("Asserting database structure...")
        # Create the database structure if it doesn't exist.
        self._db._assert_structure()

        print("Loading data from database...")
        # Load all the data from the database.
        payload = self._db._load_all()
        data = self._parse_data(payload)
        
        if data:
            for frogge in self._guild_mgr.fguilds:
                await frogge.load_all(data[frogge.guild_id])

        print("Done!")

################################################################################
    def _parse_data(self, data: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
         
        pass
    
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
    async def get_or_fetch_channel(self, channel_id: int) -> Optional[GuildChannel]:
        
        if not channel_id:
            return

        ret = self.get_channel(channel_id)
        if ret is None:
            try:
                ret = await self.fetch_channel(channel_id)
            except:
                pass
            
        return ret
    
################################################################################
