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
        name="fill_out",
        description="Fill out a form",
    )
    async def complete_form(self,  ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.forms_manager.user_menu(ctx.interaction)
        
################################################################################
    @user_command(name="Card Menu")
    async def card_menu(self, ctx: ApplicationContext, user: User) -> None:
        
        guild = self.bot[ctx.guild_id]
        await guild.card_manager.user_ctx_menu(ctx.interaction, user)
        
################################################################################
def setup(bot: "RentARaBot") -> None:
    
    bot.add_cog(General(bot))
                
################################################################################
    