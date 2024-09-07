from __future__ import annotations

from typing import TYPE_CHECKING, Tuple, List

from discord import Embed, EmbedField, Interaction
from Assets import BotEmojis
from Utilities import Utilities as U
from UI.Profiles import ProfileRequirementsToggleView

if TYPE_CHECKING:
    from Classes import ProfileManager, RentARaBot, Profile
################################################################################

__all__ = ("ProfileRequirements", )

################################################################################
class ProfileRequirements:

    # Everything besides the mgr should remain without the '_' prefix
    __slots__ = (
        "_mgr",
        # Details
        "url",
        "color",
        "jobs",
        "rates",
        # At A Glance
        "world",
        "gender",
        "race",
        "orientation",
        "height",
        "age",
        "mare",
        # Personality
        "likes",
        "dislikes",
        "personality",
        "about_me",
        # Images
        "thumbnail",
        "main_image",
    )
    
################################################################################
    def __init__(self, mgr: ProfileManager, **kwargs) -> None:

        self._mgr: ProfileManager = mgr
        
        self.url: bool = kwargs.get("url", False)
        self.color: bool = kwargs.get("color", False)
        self.jobs: bool = kwargs.get("jobs", False)
        self.rates: bool = kwargs.get("rates", False)
        
        self.world: bool = kwargs.get("world", False)
        self.gender: bool = kwargs.get("gender", True)
        self.race: bool = kwargs.get("race", True)
        self.orientation: bool = kwargs.get("orientation", False)
        self.height: bool = kwargs.get("height", False)
        self.age: bool = kwargs.get("age", False)
        self.mare: bool = kwargs.get("mare", False)
        
        self.likes: bool = kwargs.get("likes", False)
        self.dislikes: bool = kwargs.get("dislikes", False)
        self.personality: bool = kwargs.get("personality", False)
        self.about_me: bool = kwargs.get("aboutme", False)
        
        self.thumbnail: bool = kwargs.get("thumbnail", False)
        self.main_image: bool = kwargs.get("main_image", False)

################################################################################
    def load(self, data: Tuple[bool, ...]) -> None:
        
        self.url = data[1]
        self.color = data[2]
        self.jobs = data[3]
        self.rates = data[4]
        
        self.gender = True
        self.race = True
        self.orientation = data[7] 
        self.height = data[8]
        self.age = data[9]
        self.mare = data[10]
        self.world = data[11]
        
        self.likes = data[12]
        self.dislikes = data[13]
        self.personality = data[14]
        self.about_me = data[15]
        
        self.thumbnail = data[16]
        self.main_image = data[17]
        
################################################################################
    def __len__(self) -> int:
        
        flag = lambda x: 1 if x else 0
        return sum([flag(getattr(self, attr)) for attr in self.__slots__[1:]])
    
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._mgr.bot
    
################################################################################
    @property
    def guild_id(self) -> int:
    
        return self._mgr.guild.guild_id

################################################################################
    @property
    def active_requirements(self) -> List[str]:
        
        return [
            attr  # .replace("_", " ").title()
            for attr in self.__slots__[1:] 
            if getattr(self, attr)
        ]
    
################################################################################
    @staticmethod
    def emoji(value: bool) -> str:
        
        return str(BotEmojis.CheckGreen) if value else str(BotEmojis.CheckGray)
    
################################################################################
    def status(self) -> Embed:
        
        return U.make_embed(
            title="__Profile Requirements__",
            description=(
                "Use the buttons bellow to toggle the requirements for each "
                "section of your profile. If an item is required, it must be "
                "filled out before a profile will be posted.\n\n"
                
                "Note that Character Name is always required and cannot be toggled."
            ),
            fields=[
                EmbedField(
                    name="__Detail Items__",
                    value=(
                        f"{self.emoji(self.url)} - Custom URL\n"
                        f"{self.emoji(self.color)} - Accent Color\n"
                        f"{self.emoji(self.jobs)} - Jobs\n"
                        f"{self.emoji(self.rates)} - Rates"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__At A Glance Items__",
                    value=(
                        f"{self.emoji(self.gender)} - Gender/Pronouns\n"
                        f"{self.emoji(self.race)} - Race/Clan\n"
                        f"{self.emoji(self.orientation)} - Orientation\n"
                        f"{self.emoji(self.height)} - Height\n"
                        f"{self.emoji(self.age)} - Age\n"
                        f"{self.emoji(self.mare)} - Mare\n"
                        f"{self.emoji(self.world)} - Home World"
                    ),
                    inline=True
                ),
                EmbedField("** **", "** **", inline=False),
                EmbedField(
                    name="__Personality Items__",
                    value=(
                        f"{self.emoji(self.likes)} - Likes\n"
                        f"{self.emoji(self.dislikes)} - Dislikes\n"
                        f"{self.emoji(self.personality)} - Personality\n"
                        f"{self.emoji(self.about_me)} - About Me"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Images__",
                    value=(
                        f"{self.emoji(self.thumbnail)} - Thumbnail\n"
                        f"{self.emoji(self.main_image)} - Main Image"
                    ),
                    inline=True
                )
            ]
        )
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = ProfileRequirementsToggleView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################        
    def update(self) -> None:
        
        self.bot.database.update.profile_requirements(self)
        
################################################################################
    def toggle(self, attr: str) -> None:
        
        setattr(self, attr, not getattr(self, attr))
        self.update()
        
################################################################################
    def check(self, profile: Profile) -> bool:
        
        details_complete = all([
            profile.details.custom_url is not None if self.url else True,
            profile.details.color is not None if self.color else True,
            profile.details.jobs != [] if self.jobs else True,
            profile.details.rates is not None if self.rates else True
        ])
        
        aag_complete = all([
            profile.ataglance.world is not None if self.world else True,
            profile.ataglance.gender is not None if self.gender else True,
            profile.ataglance.race is not None if self.race else True,
            profile.ataglance.orientation is not None if self.orientation else True,
            profile.ataglance.height is not None if self.height else True,
            profile.ataglance.age is not None if self.age else True,
            profile.ataglance.mare is not None if self.mare else True
        ])
        
        personality_complete = all([
            profile.personality.likes != [] if self.likes else True,
            profile.personality.dislikes != [] if self.dislikes else True,
            profile.personality.personality is not None if self.personality else True,
            profile.personality.aboutme is not None if self.about_me else True
        ])
        
        images_complete = all([
            profile.images.thumbnail is not None if self.thumbnail else True,
            profile.images.main_image is not None if self.main_image else True
        ])
        
        return all([details_complete, aag_complete, personality_complete, images_complete])
        
################################################################################
        