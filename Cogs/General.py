from typing import TYPE_CHECKING

from discord import (
    ApplicationContext,
    Cog,
    User,
    slash_command,
    user_command,
    Option,
    SlashCommandOptionType
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
    @slash_command(
        name="match",
        description="Match your dating profile with other users.",
    )
    async def user_matching(self, ctx: ApplicationContext) -> None:
        
        guild = self.bot[ctx.guild_id]
        await guild.profile_manager.user_matching(ctx.interaction)
        
################################################################################
    @slash_command(
        name="challenge",
        description="Challenge another user to a card battle.",
    )
    async def card_challenge(
        self,
        ctx: ApplicationContext,
        user: Option(
            SlashCommandOptionType.user,
            name="opponent",
            description="The user you want to challenge.",
            required=True
        )
    ) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.card_manager.challenge_user(ctx.interaction, user)
    
################################################################################
    @slash_command(
        name="collection",
        description="View and manage your card collection.",
    )
    async def card_user_menu(self, ctx: ApplicationContext) -> None:
        
        guild = self.bot[ctx.guild_id]
        await guild.card_manager.user_collection_menu(ctx.interaction)
        
################################################################################
    @user_command(name="Card Menu")
    async def admin_card_menu(self, ctx: ApplicationContext, user: User) -> None:
        
        guild = self.bot[ctx.guild_id]
        await guild.card_manager.admin_ctx_menu(ctx.interaction, user)
        
################################################################################
def setup(bot: "RentARaBot") -> None:
    
    bot.add_cog(General(bot))
                
################################################################################
    