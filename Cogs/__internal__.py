from __future__ import annotations

from discord import Cog
from typing import TYPE_CHECKING
from discord.ext import tasks

if TYPE_CHECKING:
    from Classes import RentARaBot
################################################################################
class Internal(Cog):

    def __init__(self, bot: RentARaBot):

        self.bot: RentARaBot = bot

################################################################################
    @Cog.listener("on_ready")
    async def load_internals(self) -> None:

        print("Loading internals...")
        await self.bot.load_all()
        
        print("Rent-a-Ra Bot Online!")

################################################################################
    @Cog.listener("on_guild_join")
    async def on_guild_join(self, guild) -> None:

        self.bot.guild_manager.add_guild(guild)

################################################################################
def setup(bot: RentARaBot) -> None:

    bot.add_cog(Internal(bot))

################################################################################
