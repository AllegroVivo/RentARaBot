from __future__ import annotations

from typing import TYPE_CHECKING, List, Union, Type, TypeVar, Any, Tuple

from discord import (
    TextChannel,
    Role,
    Interaction,
    ForumChannel,
    Embed,
    EmbedField,
    SelectOption,
    ChannelType,
)
from Errors import MaxItemsReached
from Utilities import Utilities as U
from UI.Common import ConfirmCancelView, FroggeSelectView
from UI.Profiles import ProfileChannelGroupStatusView

if TYPE_CHECKING:
    from Classes import ProfileManager, RentARaBot
################################################################################

__all__ = ("ProfileChannelGroup",)

PCG = TypeVar("PCG", bound="ProfileChannelGroup")

################################################################################
class ProfileChannelGroup:

    __slots__ = (
        "_id",
        "_mgr",
        "_channels",
        "_roles",
    )
    
    MAX_ITEMS = 10
    
################################################################################
    def __init__(self, mgr: ProfileManager, _id: str, **kwargs) -> None:

        self._id: str = _id
        self._mgr: ProfileManager = mgr
        
        self._channels: List[Union[TextChannel, ForumChannel]] = kwargs.get("channels", [])
        self._roles: List[Role] = kwargs.get("roles", [])
    
################################################################################
    @classmethod
    def new(cls: Type[PCG], mgr: ProfileManager) -> PCG:
        
        new_id = mgr.bot.database.insert.profile_channel_group(mgr.guild_id)
        return cls(mgr, new_id)
    
################################################################################
    @classmethod
    async def load(cls: Type[PCG], mgr: ProfileManager, data: Tuple[Any, ...]) -> PCG:
        
        channels = [await mgr.guild.get_or_fetch_channel(c) for c in data[2]]
        roles = [await mgr.guild.get_or_fetch_role(r) for r in data[3]]
        
        return cls(
            mgr=mgr,
            _id=data[0],
            channels=[c for c in channels if c is not None],
            roles=[r for r in roles if r is not None]
        )
    
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._mgr.bot
    
################################################################################
    @property
    def id(self) -> str:
        
        return self._id
    
################################################################################
    @property
    def channels(self) -> List[Union[TextChannel, ForumChannel]]:
        
        return self._channels
    
################################################################################
    @property
    def roles(self) -> List[Role]:
        
        return self._roles
    
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.profile_channel_group(self)
        
################################################################################
    def delete(self) -> None:
        
        self.bot.database.delete.profile_channel_group(self)
        self._mgr._channels.remove(self)
        
################################################################################
    def status(self) -> Embed:
        
        channel_str = "\n".join([f"* {c.mention}" for c in self.channels])
        role_str = "\n".join([f"* {r.mention}" for r in self.roles])
        
        return U.make_embed(
            title="__Profile Channel Group Status__",
            description=(
                "**What's This?**\n"
                "*The following list of channels may\n"
                "be used to post profiles by users\n"
                "with the given linked roles.*"
            ),
            fields=[
                EmbedField(
                    name="__Channels__",
                    value=channel_str or "`No Channels Defined`",
                    inline=True
                ),
                EmbedField(
                    name="__Roles__",
                    value=role_str or "`No Roles Linked`",
                    inline=True
                )
            ]
        )
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = ProfileChannelGroupStatusView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
    def select_option(self) -> SelectOption:
        
        ch_str = ", ".join([c.name for c in self.channels])
        if not ch_str:
            ch_str = "No Channels Defined"
        return SelectOption(
            label=U.string_clamp(ch_str, 95),
            value=self.id
        )
    
################################################################################
    async def remove(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Channel Group__",
            description=(
                "Are you sure you want to remove this profile posting channel group?\n"
                "This action cannot be undone."
            )
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.delete()
        
################################################################################
    async def add_channel(self, interaction: Interaction) -> None:
        
        if len(self._channels) >= self.MAX_ITEMS:
            error = MaxItemsReached("Posting Channels", self.MAX_ITEMS)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        prompt = U.make_embed(
            title="__Add Posting Channel__",
            description=(
                "Please mention the channel you would like to add to this "
                "posting channel group."
            )
        )
        channel = await U.listen_for(
            interaction=interaction, 
            prompt=prompt, 
            mentionable_type=U.MentionableType.Channel,
            channel_restrictions=[ChannelType.text, ChannelType.forum]
        )
        if channel is None:
            return
        
        self._channels.append(channel)  # type: ignore
        self.update()
        
################################################################################
    async def add_role(self, interaction: Interaction) -> None:
        
        if len(self._roles) >= self.MAX_ITEMS:
            error = MaxItemsReached("Linked Roles", self.MAX_ITEMS)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        prompt = U.make_embed(
            title="__Add Linked Role__",
            description=(
                "Please mention the role you would like to link to this "
                "posting channel group."
            )
        )
        role = await U.listen_for(
            interaction=interaction, 
            prompt=prompt, 
            mentionable_type=U.MentionableType.Role
        )
        if role is None:
            return
        
        self._roles.append(role)
        self.update()
        
################################################################################
    async def remove_channel(self, interaction: Interaction) -> None:
        
        options = [
            SelectOption(
                label=c.name,
                value=str(c.id)
            ) for c in self.channels
        ]
        
        prompt = U.make_embed(
            title="__Remove Posting Channel(s)__",
            description=(
                "Please select the channel(s) you would like to remove from this "
                "posting channel group."
            )
        )
        view = FroggeSelectView(interaction.user, options, multi_select=True)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        channel_ids_to_remove = [int(i) for i in view.value]
        for channel in self.channels:
            if channel.id in channel_ids_to_remove:
                self._channels.remove(channel)
                
        self.update()
        
################################################################################
    async def remove_role(self, interaction: Interaction) -> None:
        
        options = [
            SelectOption(
                label=r.name,
                value=str(r.id)
            ) for r in self.roles
        ]
        
        prompt = U.make_embed(
            title="__Remove Linked Role(s)__",
            description=(
                "Please select the role(s) you would like to remove from this "
                "posting channel group."
            )
        )
        view = FroggeSelectView(interaction.user, options, multi_select=True)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        role_ids_to_remove = [int(i) for i in view.value]
        for role in self.roles:
            if role.id in role_ids_to_remove:
                self._roles.remove(role)
                
        self.update()
        
################################################################################
