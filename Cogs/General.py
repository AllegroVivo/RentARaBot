from typing import TYPE_CHECKING

from discord import (
    ApplicationContext,
    Cog,
    User,
    slash_command,
    user_command,
)

if TYPE_CHECKING:
    from Classes import RentARaBot
################################################################################
class General(Cog):
    
    def __init__(self, bot: "RentARaBot"):
        
        self.bot: "RentARaBot" = bot
    
################################################################################
    @slash_command(
        name="verify",
        description="Verify your humanity.",
    )
    async def user_verify(self,  ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.verification_manager.verify(ctx.interaction)
        
################################################################################
    @slash_command(
        name="profile",
        description="View and edit your personal profile.",
    )
    async def user_profile(self, ctx: ApplicationContext) -> None:
        
        guild = self.bot[ctx.guild_id]
        await guild.profile_manager.user_menu(ctx.interaction)
        
################################################################################
    @slash_command(
        name="booster",
        description="Open a booster pack from your collection.",
    )
    async def booster_pack(self, ctx: ApplicationContext) -> None:
        
        guild = self.bot[ctx.guild_id]
        await guild.card_manager.open_booster(ctx.interaction)
        
################################################################################
    @user_command(name="Card Menu")
    async def card_menu(self, ctx: ApplicationContext, user: User) -> None:
        
        guild = self.bot[ctx.guild_id]
        await guild.card_manager.user_ctx_menu(ctx.interaction, user)
        
################################################################################
def setup(bot: "RentARaBot") -> None:
    
    bot.add_cog(General(bot))
                
################################################################################
    