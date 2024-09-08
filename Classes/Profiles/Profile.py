from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Any, Dict, List, Tuple, Union

from discord import (
    Message,
    Interaction,
    Colour,
    EmbedField,
    Embed,
    SelectOption,
    ChannelType,
    TextChannel,
    ForumChannel,
    Thread, 
    Forbidden,
    NotFound,
    User
)

from Assets import BotEmojis, BotImages
from Errors import (
    AboutMeNotSet,
    ProfileChannelsNotSet,
    ProfileIncomplete,
    ExceedsMaxLength,
    ChannelMissing,
    InsufficientPermissions,
    ProfileRoleNotOwned,
    PrefsNotSet,
    ProfileNotPosted,
    PreferencesIncomplete
)
from UI.Common import CloseMessageView, FroggeSelectView, ConfirmCancelView
from UI.Profiles import (
    ProfileMainMenuView,
    PersonalityPreferencePickView,
    PublicPrivateView,
    ProfileMatchingView,
)
from Utilities import Utilities as U
from .ProfileAtAGlance import ProfileAtAGlance
from .ProfileDetails import ProfileDetails
from .ProfileImages import ProfileImages
from .ProfilePersonality import ProfilePersonality
from .ProfilePreferences import ProfilePreferences
from Utilities.Constants import *

if TYPE_CHECKING:
    from Classes import ProfileManager, RentARaBot
################################################################################

__all__ = ("Profile", )

P = TypeVar("P", bound="Profile")

################################################################################
class Profile:

    __slots__ = (
        "_mgr",
        "_user",
        "_id",
        "_details",
        "_aag",
        "_personality",
        "_images",
        "_post_url",
        "_post_msg",
        "_preferences",
        "_public",
    )
    
    MAX_ADDL_IMAGES = 3
    
################################################################################
    def __init__(self, mgr: ProfileManager, user: User, _id: str) -> None:

        self._id: str = _id
        self._mgr: ProfileManager = mgr
        self._user: User = user
        self._public: bool = True
        
        self._details: ProfileDetails = ProfileDetails(self)
        self._aag: ProfileAtAGlance = ProfileAtAGlance(self)
        self._personality: ProfilePersonality = ProfilePersonality(self)
        self._images: ProfileImages = ProfileImages(self)
        self._preferences: ProfilePreferences = ProfilePreferences(self)
        
        self._post_url: Optional[str] = None
        self._post_msg: Optional[Message] = None
    
################################################################################
    @classmethod
    def new(cls: Type[P], mgr: ProfileManager, user: User) -> P:
        
        new_id = mgr.bot.database.insert.profile(mgr.guild.guild_id, user.id)
        return cls(mgr, user, new_id)
    
################################################################################
    @classmethod
    async def load(cls: Type[P], mgr: ProfileManager, data: Dict[str, Any]) -> P:
        
        profile_data = data["profile"]
        
        self: P = cls.__new__(cls)
        
        self._id = profile_data[0]
        self._mgr = mgr
        self._user = await mgr.guild.get_or_fetch_member_or_user(profile_data[2])
        self._public = profile_data[4]
        
        self._details = ProfileDetails.load(self, data["details"])
        self._aag = ProfileAtAGlance.load(self, data["aag"])
        self._personality = ProfilePersonality.load(self, data["personality"])
        self._images = ProfileImages.load(self, data["images"])
        self._preferences = ProfilePreferences.load(self, data["preferences"])
        
        self._post_url = profile_data[3]
        self._post_msg = None
        
        return self
    
################################################################################
    def __len__(self) -> int:
        
        return len(self.compile()[0])
    
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
    def user(self) -> User:
        
        return self._user
    
################################################################################
    @property
    def name(self) -> str:
        
        return self._details.name or self.user.display_name
    
################################################################################
    @property
    def post_url(self) -> str:
        
        return self._post_url
    
    @post_url.setter
    def post_url(self, value: str) -> None:
        
        self._post_url = value
        self.update()
        
################################################################################
    @property
    def details(self) -> ProfileDetails:
        
        return self._details
    
################################################################################
    @property
    def ataglance(self) -> ProfileAtAGlance:
        
        return self._aag
    
################################################################################
    @property
    def personality(self) -> ProfilePersonality:
        
        return self._personality
    
################################################################################
    @property
    def images(self) -> ProfileImages:
        
        return self._images
    
################################################################################
    @property
    def preferences(self) -> ProfilePreferences:
        
        return self._preferences
    
################################################################################
    @property
    def color(self) -> Optional[Colour]:
        
        return self._details.color or Colour.embed_background()
    
################################################################################
    @property
    def is_public(self) -> bool:
    
        return self._public
    
    @is_public.setter
    def is_public(self, value: bool) -> None:
        
        self._public = value
        self.update()
        
################################################################################
    def is_complete(self) -> bool:
        
        return self._mgr.profile_requirements.check(self)
    
################################################################################
    async def post_message(self) -> Optional[Message]:
        
        if self._post_msg is not None:
            return self._post_msg
        
        return await self._mgr.guild.get_or_fetch_message(self._post_url)
    
################################################################################
    def update(self) -> None:

        self.bot.database.update.profile(self)

################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = U.make_embed(
            title=f"__Profile Menu for `{self.name}`__",
            description=(
                "Select a button below to view or edit the corresponding "
                "section of your profile!"
            )
        )
        view = ProfileMainMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    def compile(self) -> Tuple[Embed, Optional[Embed], Optional[Embed]]:

        char_name, url, color, jobs, rates_field = self._details.compile()
        ataglance = self._aag.compile()
        likes, dislikes, personality, aboutme = self._personality.compile()
        thumbnail, main_image, additional_imgs = self._images.compile()
        preferences = self._preferences.compile()

        if char_name is None:
            char_name = f"Character Name: `Not Set`"
        elif url is not None:
            char_name = f"{BotEmojis.Envelope}  {char_name}  {BotEmojis.Envelope}"

        fields: List[EmbedField] = []
        if ataglance is not None:
            fields.append(ataglance)
        if rates_field is not None:
            fields.append(rates_field)
        if likes is not None:
            fields.append(likes)
        if dislikes is not None:
            fields.append(dislikes)
        if personality is not None:
            fields.append(personality)
        if additional_imgs is not None:
            additional_imgs.value += U.draw_line(extra=15)
            fields.append(additional_imgs)

        main_profile = U.make_embed(
            color=color or Colour.embed_background(),
            title=char_name,
            # description=description,
            url=url,
            thumbnail_url=thumbnail,
            image_url=main_image,
            fields=fields
        )

        return main_profile, preferences, aboutme
    
################################################################################
    async def main_details_menu(self, interaction: Interaction) -> None:
        
        await self._details.menu(interaction)
    
################################################################################
    async def ataglance_menu(self, interaction: Interaction) -> None:

        await self._aag.menu(interaction)
    
################################################################################
    async def personality_preferences_menu(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Personality/Preferences Menu__",
            description=(
                "Select a button below to view or edit the corresponding "
                "section of your profile!\n\n"
                
                "__**Personality:**__\n"
                "This section is where you can list your likes, dislikes, and a little "
                "bit about yourself!\n\n"
                
                "__**Preferences:**__\n"
                "This section is where you can list your favorite in-game activities and "
                "your bedroom preferences!"
            )
        )
        view = PersonalityPreferencePickView(interaction.user, self)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is None:
            return

        if view.value is True:
            await self._personality.menu(interaction)
        else:
            await self._preferences.menu(interaction)
    
################################################################################
    async def images_menu(self, interaction: Interaction) -> None:

        await self._images.menu(interaction)
    
################################################################################
    async def preview_profile(self, interaction: Interaction) -> None:

        main_profile, _, _ = self.compile()
        view = CloseMessageView(interaction.user)

        await interaction.respond(embed=main_profile, view=view)
        await view.wait()
    
################################################################################
    async def preview_preferences(self, interaction: Interaction) -> None:

        _, prefs, _ = self.compile()
        if prefs is None:
            error = PrefsNotSet()
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        view = CloseMessageView(interaction.user)

        await interaction.respond(embed=prefs, view=view)
        await view.wait()
    
################################################################################
    async def preview_aboutme(self, interaction: Interaction) -> None:

        _, _, aboutme = self.compile()
        if aboutme is None:
            error = AboutMeNotSet()
            await interaction.respond(embed=error, ephemeral=True)
            return

        view = CloseMessageView(interaction.user)

        await interaction.respond(embed=aboutme, view=view)
        await view.wait()
    
################################################################################
    async def post(self, interaction: Interaction) -> None:

        error = None
        if not await self._mgr.allowed_to_post(interaction.user):
            error = ProfileRoleNotOwned()
        if not self._mgr.post_channels:
            error = ProfileChannelsNotSet()
        if len(self) > MAX_EMBED_LENGTH:
            error = ExceedsMaxLength(len(self), MAX_EMBED_LENGTH)
        if not self.is_complete():
            error = ProfileIncomplete(self, self._mgr.profile_requirements.active_requirements)
            
        if error is not None:
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        public_prompt = U.make_embed(
            title="__Post Profile__",
            description=(
                "Would you like to post your profile publicly?\n\n"

                "Posting your profile publicly will allow others to view it and "
                "match with you using our matching feature. If you choose not to post "
                "it publicly, however, it will be kept private and only staff will be able "
                "to view it."
            )
        )
        view = PublicPrivateView(interaction.user)

        await interaction.respond(embed=public_prompt, view=view)
        await view.wait()

        if not view.complete:
            return
        
        previous_setting = self.is_public
        self.is_public = view.value

        if previous_setting == self.is_public:
            if await self.update_post_components():
                await interaction.respond(embed=self.success_message())
                return
        else:
            await self.delete_profile_post()
    
        options = [
            SelectOption(
                label=channel.name,
                value=str(channel.id),
            )
            for channel in await self._mgr.post_channels_for(interaction.user, not self.is_public)
        ][:25]
        
        if not options:
            error = ProfileChannelsNotSet()
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        if len(options) > 1:
            prompt = U.make_embed(
                title="__Select Profile Posting Channel__",
                description=(
                    "Select the channel you would like to post your profile in!\n"
                    "Please note that you can only post in one channel at a time."
                )
            )
            view = FroggeSelectView(
                owner=interaction.user,
                options=options
            )
            
            await interaction.respond(embed=prompt, view=view)
            await view.wait()
            
            if not view.complete or view.value is False:
                return
            
            channel: Union[TextChannel, ForumChannel] = (  # type: ignore
                await self._mgr.guild.get_or_fetch_channel(int(view.value)) 
            )  
        else:
            channel = await self._mgr.guild.get_or_fetch_channel(options[0].value)  # type: ignore

        if channel is None:
            error = ChannelMissing()
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        post_embeds = [e for e in self.compile() if e is not None]
        if channel.type == ChannelType.text:
            self._post_msg = await channel.send(embeds=post_embeds)
            self.post_url = self._post_msg.jump_url
            await interaction.respond(embed=self.success_message(not self.is_public))
            return

        # Must be a forum channel
        matching_thread = next(
            (t for t in channel.threads if t.name.lower() == self.name.lower()), 
            None
        )
        if matching_thread:
            async for m in matching_thread.history():
                await m.delete()
            action = matching_thread.send  # type: ignore
        else:
            action = lambda **kw: channel.create_thread(name=self.name, **kw)

        try:
            result = await action(embeds=post_embeds)
            if isinstance(result, Thread):
                self._post_msg = await result.fetch_message(result.last_message_id)
            else:
                self._post_msg = result
            self.post_url = self._post_msg.jump_url
            await interaction.respond(embed=self.success_message(not self.is_public))
        except Forbidden:
            error = InsufficientPermissions(channel, "Send Messages")
            await interaction.respond(embed=error, ephemeral=True)

################################################################################
    async def update_post_components(self) -> bool:
        
        if self._post_url is None:
            return False
        
        message = await self.post_message()
        if message is None:
            return False
        
        try:
            await message.edit(embeds=[e for e in self.compile() if e is not None])
        except NotFound:
            self.post_url = None
            return False
        else:
            return True
        
################################################################################
    def success_message(self, is_private: bool = False) -> Embed:
        
        if not is_private:
            link_text = (
                f"\n{BotEmojis.ArrowRight}  [Check It Out HERE!]"
                f"({self.post_url})  {BotEmojis.ArrowLeft}\n"
            )
        else:
            link_text = ""

        return U.make_embed(
            color=Colour.brand_green(),
            title="Profile Posted!",
            description=(
                "Hey, good job, you did it! Your profile was posted successfully!\n"
                "You may now use the matching system with the `/match` command!\n"
                f"{U.draw_line(extra=37)}\n"
                f"(__Character Name:__ ***{self.name}***)\n"
                f"{link_text}"
                f"{U.draw_line(extra=16)}"
            ),
            thumbnail_url=BotImages.ThumbsUpFrog,
            timestamp=True
        )

################################################################################
    async def progress(self , interaction: Interaction) -> None:

        em_final = self._details.progress_emoji(await self.post_message())
        progress = U.make_embed(
            color=self.color,
            title="Profile Progress",
            description=(
                self._details.progress() +
                self._aag.progress() +
                self._personality.progress() +
                self._images.progress() +
                self._preferences.progress() +
                f"{U.draw_line(extra=15)}\n"
                f"{em_final} -- Finalize"
            ),
            timestamp=False
        )
        view = CloseMessageView(interaction.user)

        await interaction.response.send_message(embed=progress, view=view)
        await view.wait()

################################################################################
    async def run_matching_routine(self, interaction: Interaction, public_profiles: List[Profile]) -> None:

        post_msg = await self.post_message()
        if post_msg is None:
            error = ProfileNotPosted()
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        if not self.preferences.is_matchable:
            error = PreferencesIncomplete(self)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        warning = U.make_embed(
            title="__Matching Warning__",
            description=(
                "To enhance the results of the matching process, please ensure that "
                "you have filled out your profile's `Preferences & Activities` section "
                "as accurately as possible!"
            )
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=warning, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        matches = []
        for profile in public_profiles:
            if profile == self:
                continue
            if not profile.preferences.is_matchable():
                continue
            if match := self._preferences.match(profile):
                matches.append(match)
                
        matches.sort(key=lambda x: x[1], reverse=True)
        matches = matches[:5]
        
        if not matches:
            await interaction.respond(
                embed=U.make_embed(
                    title="__No Matches Found__",
                    description=(
                        "Sorry, but we couldn't find any matches for you at this time!\n\n"
                        "Please try again later or consider updating your preferences!"
                    )
                ),
                ephemeral=True
            )
            return
        
        matches_str = ""
        for pair in matches:
            profile, score = pair
            matches_str += f"**{profile.user.display_name}** -- `{score}%`\n"

        embed = U.make_embed(
            title="__Top Matches__",
            description=(
                "Here are the top 5 matches for you based on your preferences!\n\n"
                f"{U.draw_line(extra=15)}\n"
                f"{matches_str}"
            )
        )
        view = ProfileMatchingView(interaction.user, [m[0] for m in matches])
        
        await interaction.respond(embed=embed, view=view)  # , ephemeral=True)
        await view.wait()
        
################################################################################
    async def delete_profile_post(self) -> bool:
        
        if self._post_url is None:
            return False
        
        message = await self.post_message()
        if message is None:
            return False
        
        try:
            if isinstance(message.channel, Thread):
                await message.channel.delete()
            else:
                await message.delete()
        except NotFound:
            return False
        else:
            self.post_url = None
            return True

################################################################################
    async def revive_if_necessary(self):
        
        message = await self.post_message()
        if message is None:
            return
        
        if not isinstance(message.channel, Thread):
            return
        
        if message.channel.archived:
            new_msg = await message.channel.send(embeds=[e for e in self.compile() if e is not None])
            await self.delete_profile_post()
            self.post_url = new_msg.jump_url

################################################################################
    async def make_contact(self, interaction: Interaction) -> None:
        
        p2 = self._mgr.get_profile(interaction.user)
        m1 = await self._mgr.guild.get_or_fetch_member(self.user.id)

        target = (
            self._mgr.match_category
            if self._mgr.match_category is not None
            else interaction.guild
        )
        
        channel = await target.create_text_channel(f"{self.name}-{p2.name}")
        await channel.send(f"♥ {m1.mention} ♥ {p2.user.mention} ♥")
        
        await channel.set_permissions(interaction.guild.default_role, view_channel=False)
        await channel.set_permissions(m1, view_channel=True)
        await channel.set_permissions(interaction.user, view_channel=True)
        
        success = U.make_embed(
            title="__Contact Created__",
            description=(
                f"A new contact channel has been created for you and {self.name}!\n\n"
                f"Please use this channel to communicate with one another.\n\n"
                
                f"**Channel:** {channel.mention}"
            )
        )
        await interaction.respond(embed=success)
    
################################################################################
