from typing import TYPE_CHECKING

from discord import (
    ApplicationContext,
    Cog,
    Option,
    SlashCommandOptionType,
    slash_command
)

if TYPE_CHECKING:
    from Classes import FroggeBot
################################################################################
class General(Cog):
    
    def __init__(self, bot: "FroggeBot"):
        
        self.bot: "FroggeBot" = bot
    
################################################################################
    @slash_command(
        name="fill_out",
        description="Fill out a form",
    )
    async def complete_form(self,  ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.forms_manager.user_menu(ctx.interaction)
        
################################################################################
def setup(bot: "FroggeBot") -> None:
    
    bot.add_cog(General(bot))
                
################################################################################
    