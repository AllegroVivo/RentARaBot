from typing import TYPE_CHECKING

from discord import (
    ApplicationContext,
    Cog,
    SlashCommandGroup
)

if TYPE_CHECKING:
    from Classes import TrainingBot
################################################################################
class Trainers(Cog):

    def __init__(self, bot: "TrainingBot"):

        self.bot: "TrainingBot" = bot

################################################################################

    dating = SlashCommandGroup(
        name="dating",
        description="Commands for dating-related tasks and queries."
    )

################################################################################
    @dating.command(
        name="request",
        description="Request a dating session with one of our Ras."
    )
    async def trainer_dashboard(self, ctx: ApplicationContext) -> None:

        guild = self.bot[ctx.guild_id]
        await guild.dating_manager.start_request(ctx.interaction)

################################################################################
def setup(bot: "TrainingBot") -> None:

    bot.add_cog(Trainers(bot))

################################################################################
