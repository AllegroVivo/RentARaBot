from __future__ import annotations

import os
import random
from typing import TYPE_CHECKING, List, Any, Dict, Optional, Tuple

from captcha.image import ImageCaptcha
from discord import (
    TextChannel,
    Embed,
    EmbedField,
    Interaction,
    File,
    SelectOption,
    NotFound,
    Forbidden
)

from Assets import BotEmojis
from Enums import World
from Errors import MaxItemsReached, InvalidCaptcha, UnableToVerify, InsufficientPermissions
from UI.Common import FroggeSelectView
from UI.Verification import (
    VerificationManagerMenuView,
    CharacterNameModal,
    HomeWorldSelectView
)
from Utilities import Utilities as U
from .RoleRelation import RoleRelation
from .VerificationConfig import VerificationConfig

if TYPE_CHECKING:
    from Classes import RentARaBot, GuildData
################################################################################

__all__ = ("VerificationManager",)

################################################################################
class VerificationManager:

    __slots__ = (
        "_state",
        "_relations",
        "_void",
        "_config",
    )

    CAPTCHA_VOID = 1260812137220149268
    MAX_ROLE_RELATIONS = 20
    
################################################################################
    def __init__(self, state: GuildData) -> None:

        self._state: GuildData = state
        self._void: TextChannel = None  # type: ignore
        
        self._relations: List[RoleRelation] = []
        self._config: VerificationConfig = VerificationConfig(self)
    
################################################################################
    async def load_all(self, data: Dict[str, Any]) -> None:
        
        self._config = await VerificationConfig.load(self, data["config"])
        
        self._void = await self.bot.fetch_channel(self.CAPTCHA_VOID)
        self._relations = [await RoleRelation.load(self, role) for role in data["roles"]]
        
################################################################################
    def __getitem__(self, relation_id: str) -> Optional[RoleRelation]:
        
        return next((r for r in self._relations if r.id == relation_id), None)
    
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
    def role_relations(self) -> List[RoleRelation]:
        
        return self._relations
    
################################################################################
    @property
    def captcha_void(self) -> TextChannel:
        
        return self._void

################################################################################
    @property
    def log_events(self) -> bool:
        
        return self._config.log_events
    
################################################################################
    @property
    def require_captcha(self) -> bool:
        
        return self._config.require_captcha
    
################################################################################
    @property
    def change_name(self) -> bool:
        
        return self._config.change_name
    
################################################################################
    def status(self) -> Embed:
        
        col1 = col2 = col3 = ""
        for role in self._relations:
            col1 += (
                f"{role.pending_role.mention}\n" 
                if role.pending_role is not None 
                else "`Pending Role Not Set`\n"
            )
            col2 += f"{BotEmojis.ArrowRight}{BotEmojis.ArrowRight}{BotEmojis.ArrowRight}\n"
            col3 += (
                f"{role.final_role.mention}\n" 
                if role.final_role is not None
                else "`Final Role Not Set`\n"
            )
            
        if not col1:
            col1 = "`No Relations`"
            col2 = col3 = "** **"

        def check(value: bool) -> str:
            return str(BotEmojis.Check) if value else str(BotEmojis.Cross)
        
        return U.make_embed(
            title="__Verification Module Status__",
            description=(
                "**[Log Events]**: *Whether or not to log\n"
                "verification events to the server log stream.*\n"
                "**[Change Name]**: *Users' server display names\n"
                "will be force-changed to their character name\n"
                "upon successful verification*\n"
                "**[Require Captcha]**: *Users must complete a\n"
                "captcha to verify their human-ness.*\n"
            ),
            fields=[
                EmbedField(
                    name="Log Events",
                    value=check(self.log_events),
                    inline=True
                ),
                EmbedField(
                    name="Change Name",
                    value=check(self.change_name),
                    inline=True
                ),
                EmbedField(
                    name="Require Captcha",
                    value=check(self.require_captcha),
                    inline=True
                ),
                EmbedField(
                    name="__Role Relations__",
                    value=col1,
                    inline=True
                ),
                EmbedField(
                    name="** **",
                    value=col2,
                    inline=True
                ),
                EmbedField(
                    name="** **",
                    value=col3,
                    inline=True
                )
            ]
        )

################################################################################
    async def main_menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = VerificationManagerMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    async def add_relation(self, interaction: Interaction) -> None:
        
        if len(self.role_relations) >= self.MAX_ROLE_RELATIONS:
            error = MaxItemsReached("Role Relationships", self.MAX_ROLE_RELATIONS)
            await interaction.respond(embed=error)
            return
        
        new_relation = RoleRelation.new(self)
        self._relations.append(new_relation)
        
        await new_relation.menu(interaction)
    
################################################################################
    async def modify_relation(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Modify Role Relation__",
            description=(
                "Please select the role relation you would like to modify."
            )
        )
        view = FroggeSelectView(
            owner=interaction.user, 
            options=[r.select_option() for r in self.role_relations]
        )
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        relation = self[view.value]
        await relation.menu(interaction)
    
################################################################################
    async def remove_relation(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Role Relation__",
            description=(
                "Please select the role relation you would like to modify."
            )
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=[r.select_option() for r in self.role_relations]
        )
    
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
    
        if not view.complete or view.value is False:
            return
    
        relation = self[view.value]
        await relation.remove(interaction)
    
################################################################################
    async def toggle_logging(self, interaction: Interaction) -> None:
        
        await self._config.toggle_logging(interaction)
        
################################################################################
    async def toggle_captcha(self, interaction: Interaction) -> None:
        
        await self._config.toggle_captcha(interaction)
        
################################################################################
    async def toggle_change_name(self, interaction: Interaction) -> None:
        
        await self._config.toggle_change_name(interaction)
        
################################################################################
    async def verify(self, interaction: Interaction) -> None:

        # Step 1: Please verify you are human (Captcha)
        inter = None
        if self.require_captcha:
            inter = await self.verify_captcha(interaction)
            if inter is None:
                return

        interaction = inter or interaction

        # Step 2: Enter Name and World
        raw = await self.get_name_and_world(interaction)
        if raw is None:
            return
        
        print("Got name and world")
        forename, surname, world = raw

        character_id = await self.bot.lodestone.fetch_character_id(interaction, *raw)
        if character_id is None:
            return

        # Step 3: Change server nickname
        if self.change_name:
            print("Changing nickname")
            await self.set_server_nickname(interaction, character_id)

        # Step 4: Swap Roles
        message_str = ""
        member = await self.guild.get_or_fetch_member(interaction.user.id)
        
        for roles in self.role_relations:
            result = await roles.check_swap(interaction, member)
            if result is not None:
                message_str += (result + "\n")

        # Step 5: Log Verification
        if self.log_events:
            pass
            # await self.guild.log.verification_submitted(interaction.user, f"{forename} {surname}")
            
        await interaction.respond(message_str or f"Success! You are now verified.", ephemeral=True)
        
################################################################################
    async def verify_captcha(self, interaction: Interaction) -> Optional[Interaction]:

        code = str(random.randint(100000, 999999))
        fp = f"Files/{code}captcha.png"

        captcha = ImageCaptcha()
        captcha.write(code, fp)

        file = File(fp, filename="captcha.png")
        message = await self.captcha_void.send(file=file)
        image_url = message.attachments[0].url

        options = [SelectOption(label=code, value=code)]
        for i in range(1, 5):
            dummy_code = str(random.randint(100000, 999999))
            options.append(
                SelectOption(
                    label=dummy_code,
                    value=dummy_code
                )
            )
        random.shuffle(options)

        prompt = U.make_embed(
            title="__Human Verification__",
            description=(
                "Please verify you are human by selecting the following "
                "code from the drop-down.\n\n"

                f"If you are unable to see the image, [please click here]({image_url})."
            ),
            image_url=image_url
        )
        view = FroggeSelectView(interaction.user, options, return_interaction=True)

        inter = await interaction.respond(embed=prompt, view=view, ephemeral=True)
        await view.wait()

        if not view.complete or view.value is False:
            return

        resp, inter2 = view.value

        if resp != code:
            error = InvalidCaptcha()
            await interaction.respond(embed=error, ephemeral=True)
            return

        try:
            await inter.delete_original_response()
        except NotFound:
            pass

        try:
            os.remove(fp)
        except:
            pass

        return inter2

################################################################################
    async def get_name_and_world(self, interaction: Interaction) -> Optional[Tuple[str, str, World]]:

        modal = CharacterNameModal()

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        forename, surname = modal.value

        prompt = U.make_embed(
            title="__World Selection__",
            description="Please select the data center and world your character is on."
        )
        view = HomeWorldSelectView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        _, world = view.value

        character_id = await self.bot.lodestone.fetch_character_id(interaction, forename, surname, world)
        if character_id is None:
            return

        return forename, surname, world

################################################################################
    async def set_server_nickname(self, interaction: Interaction, character_id: int) -> bool:

        char_name = await self.bot.lodestone.fetch_character_name(interaction, character_id)
        member = await self._state.get_or_fetch_member(interaction.user.id)

        if char_name is None or member is None:
            error = UnableToVerify()
            await interaction.respond(embed=error, ephemeral=True)
            return False

        try:
            await member.edit(nick=char_name)
        except Forbidden:
            error = InsufficientPermissions(None, "Change Nicknames")
            await interaction.respond(embed=error, ephemeral=True)
            return False
        except:
            error = UnableToVerify()
            await interaction.respond(embed=error, ephemeral=True)
            return False
        else:
            return True

################################################################################
