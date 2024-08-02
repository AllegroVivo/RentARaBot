from __future__ import annotations

from typing import TYPE_CHECKING, List, Any, Dict, Optional, Union

from discord import (
    EmbedField,
    Embed,
    TextChannel,
    ForumChannel,
    Role,
    Interaction,
    SelectOption,
    ChannelType
)

from Utilities import Utilities as U
from UI.Common import FroggeSelectView
from UI.Profiles import ProfileManagerMenuView
from .Profile import Profile
from .ProfileRequirements import ProfileRequirements

if TYPE_CHECKING:
    from Classes import GuildData, RentARaBot, Character
################################################################################

__all__ = ("ProfileManager", )

################################################################################
class ProfileManager:

    __slots__ = (
        "_state",
        "_profiles",
        "_requirements",
        "_staff_channels",
        "_public_channels",
        "_staff_roles",
    )
    
    MAX_CHANNELS = 20
    MAX_ROLES = 20
    
################################################################################
    def __init__(self, state: GuildData) -> None:

        self._state: GuildData = state
        self._profiles: List[Profile] = []
        
        self._requirements: ProfileRequirements = ProfileRequirements(self)
        
        self._staff_channels: List[Union[TextChannel, ForumChannel]] = []
        self._public_channels: List[Union[TextChannel, ForumChannel]] = []
        
        self._staff_roles: List[Role] = []
    
################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:
        
        system_data = payload["system"]
        staff_channels = [
            await self.guild.get_or_fetch_channel(c) 
            for c in system_data[1]
        ]
        public_channels = [
            await self.guild.get_or_fetch_channel(c)
            for c in system_data[2]
        ]
        staff_roles = [
            await self.guild.get_or_fetch_role(r)
            for r in system_data[3]
        ]
        
        self._staff_channels = [c for c in staff_channels if c is not None]
        self._public_channels = [c for c in public_channels if c is not None]
        self._staff_roles = [r for r in staff_roles if r is not None]

        profiles = []
        for p in payload["profiles"]:
            if profile := Profile.load(self, p):  # Profile is None if user is not found.
                profiles.append(profile)
        self._profiles = profiles
        
        self._requirements.load(payload["requirements"])
    
################################################################################
    def __getitem__(self, profile_id: str) -> Optional[Profile]:

        return next((p for p in self._profiles if p.id == profile_id), None)
            
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._state.bot
    
################################################################################
    @property
    def guild(self) -> GuildData:
        
        return self._state
    
################################################################################
    @property
    def profiles(self) -> List[Profile]:
        
        return self._profiles
    
################################################################################
    @property
    def staff_requirements(self) -> ProfileRequirements:
        
        return self._requirements
    
################################################################################
    @property
    def staff_channels(self) -> List[Union[TextChannel, ForumChannel]]:
        
        return self._staff_channels
    
    @property
    def public_channels(self) -> List[Union[TextChannel, ForumChannel]]:
        
        return self._public_channels
    
################################################################################
    @property
    def staff_roles(self) -> List[Role]:
        
        return self._staff_roles
    
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.profile_manager(self)
        
################################################################################
    def status(self) -> Embed:
        
        channel_str = "\n".join([f"* {c.mention} *(Staff)*" for c in self.staff_channels])
        channel_str += "\n"
        channel_str += "\n".join([f"* {c.mention} *(Public)*" for c in self.public_channels])
        
        posted_profiles = [p for p in self._profiles if p.post_url is not None]
        posted_names = [p.name for p in posted_profiles]
        name_str1 = name_str2 = ""
        
        if len(posted_names) > 0:
            for i, name in enumerate(posted_names):
                if i % 2 == 0:
                    name_str1 += f"* `{name}`\n"
                else:
                    name_str2 += f"* `{name}`\n"
                    
        if not name_str1:
            name_str1 = "`None Posted`"
            name_str2 = "** **"
        
        return U.make_embed(
            title="__Profile System Management__",
            description=f"**[`{len(self._requirements)}/17`]** Requirements Active",
            fields=[
                EmbedField(
                    name="__Channels__",
                    value=channel_str,
                    inline=True
                ),
                EmbedField(
                    name="__Staff Roles__",
                    value="\n".join([f"* {r.mention}" for r in self.staff_roles]),
                    inline=True
                ),
                EmbedField("** **", "** **", inline=False),
                EmbedField(
                    name="__Posted Profiles__",
                    value=name_str1,
                    inline=True,
                ),
                EmbedField(
                    name="** **",
                    value=name_str2,
                    inline=True,
                ),
            ],
        )
    
################################################################################
    async def main_menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = ProfileManagerMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    def new_profile(self, character: Character) -> Profile:
        
        profile = Profile.new(self, character)
        self._profiles.append(profile)
        return profile

################################################################################
    async def add_channel(self, interaction: Interaction) -> None:
        
        options = [
            SelectOption(
                label="Staff Channel",
                value="Staff",
                description="A channel for staff to post profiles.",
            ),
            SelectOption(
                label="Public Channel",
                value="Public",
                description="A channel for public users to post profiles."
            ),
        ]
        
        prompt = U.make_embed(
            title="__Select Channel Type__",
            description="Please select the type of channel you would like to add.",
        )
        view = FroggeSelectView(interaction.user, options)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        channel_type = view.value
        
        prompt = U.make_embed(
            title="__Add Profile Post Channel__",
            description="Please mention the channel you would like to add.",
        )
        channel = await U.listen_for(
            interaction=interaction,
            prompt=prompt, 
            mentionable_type=U.MentionableType.Channel, 
            channel_restrictions=[ChannelType.text, ChannelType.forum]
        )
        
################################################################################
