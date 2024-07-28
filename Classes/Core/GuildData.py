from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from discord import Guild, NotFound, Role, Member, User, Emoji, Message
from discord.abc import GuildChannel

from Classes.Forms.FormsManager import FormsManager
from Utilities import log

if TYPE_CHECKING:
    from Classes import FroggeBot
################################################################################

__all__ = ("GuildData",)

################################################################################
class GuildData:

    __slots__ = (
        "_state",
        "_parent",
        "_forms",
    )

################################################################################
    def __init__(self, bot: FroggeBot, parent: Guild):

        self._state: FroggeBot = bot
        self._parent: Guild = parent
        
        self._forms: FormsManager = FormsManager(self)

################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:
        
        await self._forms.load_all(payload["forms"])
        
################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._state
    
################################################################################
    @property
    def parent(self) -> Guild:
        
        return self._parent
    
################################################################################
    @property
    def guild_id(self) -> int:
        
        return self._parent.id
    
################################################################################
    @property
    def name(self) -> str:
        
        return self._parent.name
    
################################################################################
    @property
    def forms_manager(self) -> FormsManager:
        
        return self._forms
    
################################################################################
    async def get_or_fetch_channel(self, channel_id: Optional[int]) -> Optional[GuildChannel]:
        
        log.debug(self, f"Fetching Channel: {channel_id}")
        
        if channel_id is None:
            return
        
        if channel := self.parent.get_channel(channel_id):
            log.debug(self, f"Channel Gotten: {channel.name}")
            return channel
        
        try:
            channel = await self.parent.fetch_channel(channel_id)
        except NotFound:
            return
        else:
            log.debug(self, f"Channel Fetched: {channel.name}")
            return channel
        
################################################################################
    async def get_or_fetch_role(self, role_id: Optional[int]) -> Optional[Role]:
        
        log.debug(self, f"Fetching Role: {role_id}")
        
        if role_id is None:
            return
        
        if role := self.parent.get_role(role_id):
            log.debug(self, f"Role Gotten: {role.name}")
            return role
        
        try:
            role = await self.parent._fetch_role(role_id)
        except NotFound:
            return
        else:
            log.debug(self, f"Role Fetched: {role.name}")
            return role
        
################################################################################
    async def get_or_fetch_member(self, user_id: int) -> Optional[Member]:
        
        log.debug(self, f"Fetching Member: {user_id}")
        
        if member := self.parent.get_member(user_id):
            log.debug(self, f"Member Gotten: {member.display_name}")
            return member
        
        try:
            member = await self.parent.fetch_member(user_id)
        except NotFound:
            return
        else:
            log.debug(self, f"Member Fetched: {member.display_name}")
            return member
        
################################################################################
    async def get_or_fetch_member_or_user(self, user_id: int) -> Optional[Union[Member, User]]:
        
        log.debug(self, f"Fetching Member or User: {user_id}")
        
        if member := await self.get_or_fetch_member(user_id):
            return member
        
        if user := self._state.get_user(user_id):
            log.debug(self, f"User Gotten: {user.name}")
            return user
        
        try:
            user = await self._state.fetch_user(user_id)
        except NotFound:
            return
        else:
            log.debug(self, f"User Fetched: {user.name}")
            return user
        
################################################################################
    async def get_or_fetch_emoji(self, emoji_id: int) -> Optional[Emoji]:
        
        log.debug(self, f"Fetching Emoji: {emoji_id}")
        
        for emoji in self.parent.emojis:
            if emoji.id == emoji_id:
                return emoji
        
        try:
            return await self.parent.fetch_emoji(emoji_id)
        except NotFound:
            return
        
################################################################################
    async def get_or_fetch_message(self, message_url: Optional[str]) -> Optional[Message]:
        
        log.debug(self, f"Fetching Message: {message_url}")
        
        if message_url is None:
            return
        
        url_parts = message_url.split("/")
        
        if message := self.bot.get_message(int(url_parts[-1])):
            return message
        
        if channel := await self.get_or_fetch_channel(int(url_parts[-2])):
            try:
                return await channel.fetch_message(int(url_parts[-1]))  # type: ignore
            except NotFound:
                return
        
################################################################################
