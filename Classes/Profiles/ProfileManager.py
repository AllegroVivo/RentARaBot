from __future__ import annotations

from typing import TYPE_CHECKING, List, Any, Dict, Optional, Union

from discord import (
    EmbedField,
    Embed,
    Role,
    Interaction,
    TextChannel,
    ForumChannel,
    User
)

from Utilities import Utilities as U
from Errors import MaxItemsReached
from UI.Common import FroggeSelectView
from UI.Profiles import ProfileManagerMenuView, ProfileChannelsMenuView
from .Profile import Profile
from .ProfileRequirements import ProfileRequirements
from .ProfileChannelGroup import ProfileChannelGroup

if TYPE_CHECKING:
    from Classes import GuildData, RentARaBot
################################################################################

__all__ = ("ProfileManager", )

################################################################################
class ProfileManager:

    __slots__ = (
        "_state",
        "_profiles",
        "_requirements",
        "_channels",
    )
    
    MAX_CHANNEL_GROUPS = 8  # (Three fields per line in the embed) 
    MAX_ROLES = 20
    
################################################################################
    def __init__(self, state: GuildData) -> None:

        self._state: GuildData = state
        self._profiles: List[Profile] = []
        
        self._requirements: ProfileRequirements = ProfileRequirements(self)
        self._channels: List[ProfileChannelGroup] = []
    
################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:
        
        self._channels = [
            await ProfileChannelGroup.load(self, c) 
            for c in payload["channels"]
        ]
        
        profiles = []
        for p in payload["profiles"]:
            profile = await Profile.load(self, p)
            if profile is not None:  # Profile is None if user is not found.
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
    def guild_id(self) -> int:
        
        return self._state.guild_id
    
################################################################################
    @property
    def profiles(self) -> List[Profile]:
        
        return self._profiles
    
################################################################################
    @property
    def profile_requirements(self) -> ProfileRequirements:
        
        return self._requirements
    
################################################################################
    @property
    def allowed_roles(self) -> List[Role]:
        
        return [r for group in self._channels for r in group.roles]
    
################################################################################
    @property
    def post_channels(self) -> List[Union[TextChannel, ForumChannel]]:
        
        return [c for group in self._channels for c in group.channels]
    
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.profile_manager(self)
        
################################################################################
    def status(self) -> Embed:
        
        channels = []
        roles = []
        for group in self._channels:
            channels.extend(group.channels)
            roles.extend(group.roles)
        
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
            description=(
                f"**[`{len(self._requirements)}/17`]** Profile Requirements Selected\n\n"
                
                f"**[`{len(self._channels)}`]** Channel Groups Defined with...\n"
                f"**[`{len(channels)}`]** Channels available for posting by...\n"
                f"**[`{len(roles)}`]** Roles\n"
            ),
            fields=[
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
    async def user_menu(self, interaction: Interaction) -> None:
        
        profile = self.get_profile(interaction.user)
        if profile is None:
            profile = self.new_profile(interaction.user)
            
        await profile.menu(interaction)
        
################################################################################    
    def get_profile(self, user: User) -> Optional[Profile]:
        
        return next((p for p in self._profiles if p.user.id == user.id), None)
    
################################################################################
    def new_profile(self, user: User) -> Profile:
        
        profile = Profile.new(self, user)
        self._profiles.append(profile)
        return profile

################################################################################
    def channel_status(self) -> Embed:
        
        fields = []
        for i, group in enumerate(self._channels):
            channel_str = "\n".join([f"* {c.mention}" for c in group.channels])
            role_str = "\n".join([f"* {r.mention}" for r in group.roles])
            
            fields.append(
                EmbedField(
                    name=f"__Channel Group {i + 1}__",
                    value=(
                        f"__Channels__\n"
                        f"{channel_str}"
                    ),
                    inline=True
                )
            )
            fields.append(
                EmbedField(
                    name="** **",
                    value=(
                        f"__Roles__\n"
                        f"{role_str}"
                    ),
                    inline=True
                )
            )
            fields.append(EmbedField("** **", "** **", True))
            
        if not fields:
            fields.append(
                EmbedField(
                    name="__Channel Groups__",
                    value="`No Posting Channels Defined`",
                    inline=False
                )
            )
        
        return U.make_embed(
            title="__Profile Channel Associations__",
            fields=fields,
        )
        
################################################################################
    async def channels_menu(self, interaction: Interaction) -> None:
        
        embed = self.channel_status()
        view = ProfileChannelsMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    async def add_channel_group(self, interaction: Interaction) -> None:
        
        if len(self._channels) >= self.MAX_CHANNEL_GROUPS:
            error = MaxItemsReached("Channel Groups", self.MAX_CHANNEL_GROUPS)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        new_group = ProfileChannelGroup.new(self)
        self._channels.append(new_group)
        
        await new_group.menu(interaction)
        
################################################################################
    async def modify_channel_group(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Modify Channel Group__",
            description="Please select the channel group you would like to modify."
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=[g.select_option() for g in self._channels]
        )
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        group = next((g for g in self._channels if g.id == view.value), None)
        if group is None:
            return
        
        await group.menu(interaction)
        
################################################################################
    async def remove_channel_group(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Channel Group__",
            description="Please select the channel group you would like to remove."
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=[g.select_option() for g in self._channels]
        )
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        group = next((g for g in self._channels if g.id == view.value), None)
        if group is None:
            return
        
        await group.remove(interaction)
        
################################################################################
    async def requirements_menu(self, interaction: Interaction) -> None:
        
        await self._requirements.menu(interaction)
        
################################################################################
    async def allowed_to_post(self, user: User) -> bool:
        
        member = await self.guild.get_or_fetch_member(user.id)
        if member is None:
            return False
        
        return any(r in member.roles for r in self.allowed_roles)

################################################################################
    async def post_channels_for(self, user: User) -> List[Union[TextChannel, ForumChannel]]:
        
        member = await self.guild.get_or_fetch_member(user.id)
        if member is None:
            return []
        
        ret = []
        for group in self._channels:
            if any(r in member.roles for r in group.roles):
                ret.extend(group.channels)
                
        return ret

################################################################################
