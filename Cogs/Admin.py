from typing import TYPE_CHECKING

from discord import (
    ApplicationContext,
    Cog,
    Option,
    SlashCommandOptionType,
    SlashCommandGroup
)

if TYPE_CHECKING:
    from Classes import FroggeBot
################################################################################
class Admin(Cog):
    
    def __init__(self, bot: "FroggeBot"):
        
        self.bot: "FroggeBot" = bot
        
################################################################################
        
    admin = SlashCommandGroup(
        name="admin",
        description="Administrative commands for bot configuration.",
        guild_only=True
    )
    
################################################################################
    @admin.command(
        name="forms",
        description="Manage forms for the bot."
    )
    async def forms_menu(self,  ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.forms_manager.main_menu(ctx.interaction)
        
################################################################################
def setup(bot: "FroggeBot") -> None:
    
    bot.add_cog(Admin(bot))
                
################################################################################
    