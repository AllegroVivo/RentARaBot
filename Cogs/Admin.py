from typing import TYPE_CHECKING

from discord import (
    ApplicationContext,
    Cog,
    Option,
    SlashCommandOptionType,
    SlashCommandGroup,
    InteractionContextType
)

if TYPE_CHECKING:
    from Classes import RentARaBot
################################################################################
class Admin(Cog):
    
    def __init__(self, bot: "RentARaBot"):
        
        self.bot: "RentARaBot" = bot
        
################################################################################
        
    admin = SlashCommandGroup(
        name="admin",
        description="Administrative commands for bot configuration.",
        contexts=[InteractionContextType.guild]
    )
    
################################################################################
    @admin.command(
        name="forms",
        description="Manage forms for the bot."
    )
    async def forms_menu(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.forms_manager.main_menu(ctx.interaction)
        
################################################################################
    @admin.command(
        name="cards",
        description="Manage the bot's Trading Card Game module."
    )
    async def cards_menu(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.card_manager.main_menu(ctx.interaction)
        
################################################################################
    @admin.command(
        name="verification",
        description="Manage the bot's Verification module."
    )
    async def verification_menu(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.verification_manager.main_menu(ctx.interaction)
        
################################################################################
    @admin.command(
        name="profiles",
        description="Manage the bot's Profiles module."
    )
    async def profiles_menu(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.profile_manager.main_menu(ctx.interaction)
        
################################################################################
def setup(bot: "RentARaBot") -> None:
    
    bot.add_cog(Admin(bot))
                
################################################################################
    