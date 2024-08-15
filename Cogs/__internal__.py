from __future__ import annotations

from discord import Cog, Member
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
    @tasks.loop(hours=6)
    async def revive_profiles(self) -> None:

        for fguild in self.bot.guild_manager.fguilds:
            await fguild.profile_manager.revive_profiles()
        
################################################################################
    @Cog.listener("on_member_remove")
    async def on_member_remove(self, member: Member) -> None:

        guild = self.bot[member.guild.id]
        await guild.member_left(member)
        
################################################################################
def setup(bot: RentARaBot) -> None:

    bot.add_cog(Internal(bot))

################################################################################
