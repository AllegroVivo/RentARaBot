from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Type, TypeVar, Dict, Any, Union

from discord import (
    TextChannel,
    Embed,
    Role,
    Interaction,
    SelectOption,
    User, 
    CategoryChannel
)
from discord.ext.pages import Page

from Assets import BotEmojis
from Errors import MaxItemsReached, ChannelNotSet, IncompleteForm
from UI.Common import (
    BasicTextModal,
    FroggeSelectView,
    ConfirmCancelView,
    Frogginator
)
from UI.Forms import (
    FormStatusView,
    FormPromptsMenuView,
    FormNotificationsMenuView,
    FormChannelStatusView,
    FormNotificationPartyView
)
from Utilities import Utilities as U
from .FormQuestion import FormQuestion
from .FormResponseCollection import FormResponseCollection
from .FormPrompt import FormPrompt

if TYPE_CHECKING:
    from Classes import FormsManager, RentARaBot, GuildData
################################################################################

__all__ = ("Form", )

F = TypeVar("F", bound="Form")

################################################################################
class Form:

    __slots__ = (
        "_id",
        "_mgr",
        "_questions",
        "_responses",
        "_channel",
        "_name",
        "_pre_prompt",
        "_post_prompt",
        "_to_notify",
        "_create_channel",
        "_channel_roles",
        "_category",
    )
    
    MAX_QUESTIONS = 20
    MAX_TO_NOTIFY = 10
    
################################################################################
    def __init__(self, mgr: FormsManager, _id: str, **kwargs) -> None:

        self._id: str = _id
        self._mgr: FormsManager = mgr
        self._name: Optional[str] = kwargs.get("name")
        
        self._questions: List[FormQuestion] = kwargs.get("questions", [])
        self._responses: List[FormResponseCollection] = kwargs.get("responses", [])
        self._channel: Optional[TextChannel] = kwargs.get("channel")
        
        self._pre_prompt: Optional[FormPrompt] = kwargs.get("pre_prompt")
        self._post_prompt: Optional[FormPrompt] = kwargs.get("post_prompt")
        
        self._to_notify: List[Union[User, Role]] = kwargs.get("to_notify", [])
        self._create_channel: bool = kwargs.get("create_channel", False)
        self._channel_roles: List[Role] = kwargs.get("channel_roles", [])
        self._category: Optional[CategoryChannel] = kwargs.get("category")
    
################################################################################
    @classmethod
    def new(cls: Type[F], mgr: FormsManager, name: str) -> F:
        
        new_id = mgr.bot.database.insert.form(mgr.guild_id, name)
        return cls(mgr, new_id, name=name)
    
################################################################################
    @classmethod
    async def load(cls: Type[F], mgr: FormsManager, data: Dict[str, Any]) -> F:
        
        fdata = data["form"]
        
        self: F = cls.__new__(cls)
        
        self._id = fdata[0]
        self._mgr = mgr
        self._channel = await mgr.guild.get_or_fetch_channel(fdata[2])
        self._name = fdata[3]
        
        self._questions = [await FormQuestion.load(self, q) for q in data["questions"]]       
        self._responses = [
            await FormResponseCollection.load(self, r) 
            for r in data["responses"]
        ]
        
        self._pre_prompt = (
            FormPrompt.load(self, data["pre_prompt"])
            if data["pre_prompt"] is not None
            else None
        )
        self._post_prompt = (
            FormPrompt.load(self, data["post_prompt"])
            if data["post_prompt"] is not None
            else None
        )
        
        possible_notifications = [
            await self._fetch_user_or_role(mgr.guild, notif)
            for notif in fdata[4]
        ]

        self._to_notify = [n for n in possible_notifications if n is not None]
        self._create_channel = fdata[5]
        self._channel_roles = [
            await mgr.guild.get_or_fetch_role(r)
            for r in fdata[6]
        ]
        self._category = await mgr.guild.get_or_fetch_channel(fdata[7])
        
        return self
    
################################################################################
    @staticmethod
    async def _fetch_user_or_role(guild: GuildData, _id: int) -> Union[User, Role]:

        ret = await guild.get_or_fetch_role(_id)
        if ret is not None:
            return ret

        return await guild.get_or_fetch_member_or_user(_id)

################################################################################
    def __eq__(self, other: Form) -> bool:
        
        return self.id == other.id
    
################################################################################
    def __getitem__(self, question_id: str) -> Optional[FormQuestion]:
        
        return next((q for q in self._questions if q.id == question_id), None)
    
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
    def questions(self) -> List[FormQuestion]:
        
        self._questions.sort(key=lambda q: q.order)
        return self._questions
    
################################################################################
    @property
    def responses(self) -> List[FormResponseCollection]:
        
        return self._responses
    
################################################################################
    @property
    def channel(self) -> Optional[TextChannel]:
        
        return self._channel
    
    @channel.setter
    def channel(self, value: TextChannel) -> None:
        
        self._channel = value
        self.update()
        
################################################################################
    @property
    def name(self) -> Optional[str]:
        
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        
        self._name = value
        self.update()
        
################################################################################
    @property
    def create_channel(self) -> bool:
        
        return self._create_channel
    
    @create_channel.setter
    def create_channel(self, value: bool) -> None:
        
        self._create_channel = value
        self.update()
       
################################################################################
    @property
    def channel_roles(self) -> List[Union[User, Role]]:
        
        return self._channel_roles
    
################################################################################
    @property
    def category_channel(self) -> Optional[CategoryChannel]:
        
        return self._category
    
    @category_channel.setter
    def category_channel(self, value: CategoryChannel) -> None:
        
        self._category = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.form(self)
        
################################################################################
    def delete(self) -> None:
        
        self.bot.database.delete.form(self)
        self._mgr.forms.remove(self)

################################################################################
    def status(self) -> Embed:
        
        desc = (
            f"**Questions:** [{len(self._questions)}]\n"
            f"**Form Log Channel:** "
            f"{self.channel.mention if self.channel else '`Not Set`'}\n"
            f"**Create Channel Upon Submission:** "
            f"{str(BotEmojis.CheckGreen if self.create_channel else BotEmojis.Cross)}\n\n"
        )
        if self.create_channel:
            desc += (
                "__**Creation Category**__\n"
                f"{self._category.mention if self._category else '`Not Set`'}\n\n"
                
                "__**Roles With Access to Created Channel**__\n" +
                ("\n".join(
                    f"* {r.mention}"
                    for r in self.channel_roles
                ) if self.channel_roles else "`Not Set`") + "\n\n"
            )
        desc += (
            "__**Parties to Notify Upon Submission**__\n" + (
                "\n".join(
                    f"* {notif.mention} ({notif.name})"
                    for notif in self._to_notify
                )
                if self._to_notify
                else "`No users to notify.`"
            ) + "\n\n" +

                "Press a button below to modify the form."
        )
        
        return U.make_embed(
            title=f"__Form Status for: `{self.name}`__",
            description=desc,
        )
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = FormStatusView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    async def add_question(self, interaction: Interaction) -> None:

        if len(self._questions) >= self.MAX_QUESTIONS:
            error = MaxItemsReached("Question", self.MAX_QUESTIONS)
            await interaction.respond(embed=error, ephemeral=True)
            return

        modal = BasicTextModal(
            title="Enter Question Text",
            attribute="Value",
            example="eg. 'What is the airspeed velocity of an unladen swallow?'",
            max_length=80,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        question = FormQuestion.new(self, modal.value)
        self._questions.append(question)

        await question.menu(interaction)
    
################################################################################
    async def modify_question(self, interaction: Interaction) -> None:
        
        options = [
            SelectOption(
                label=question.primary_text,
                value=question.id
            )
            for question in self.questions
        ]
        
        prompt = U.make_embed(
            title="__Modify Question__",
            description="Pick a question from the list below to modify."
        )
        view = FroggeSelectView(interaction.user, options)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        question = self[view.value]
        await question.menu(interaction)
    
################################################################################
    async def remove_question(self, interaction: Interaction) -> None:

        options = [
            SelectOption(
                label=question.primary_text,
                value=question.id
            )
            for question in self.questions
        ]

        prompt = U.make_embed(
            title="__Remove Question__",
            description="Pick a question from the list below to remove."
        )
        view = FroggeSelectView(interaction.user, options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return
        
        question = self[view.value]
        await question.remove(interaction)
    
################################################################################
    async def set_channel(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Set Form Log Channel__",
            description="Mention the channel where form responses should be logged."
        )
        channel = await U.listen_for(interaction, prompt, U.MentionableType.Channel)
        if channel is None:
            return
        
        self.channel = channel
    
################################################################################
    async def paginate_responses(self, interaction: Interaction) -> None:

        pages = [
            Page(embeds=[response.compile()])
            for response
            in self._responses
        ]
        frogginator = Frogginator(pages, self)
        await frogginator.respond(interaction)
    
################################################################################
    async def remove(self, interaction: Interaction) -> None:

        confirm = U.make_embed(
            title="__Confirm Removal__",
            description=(
                f"Are you sure you want to remove the form: "
                f"`{self.name or 'Unnamed Form'}`?\n\n"

                "__**WARNING:** This action is dangerous and irreversible.__\n"
                "*(All questions and options will be deleted.)*"
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.delete()
    
################################################################################
    def select_option(self) -> SelectOption:
        
        return SelectOption(
            label=self.name or "Unnamed Form",
            value=self.id
        )
    
################################################################################
    async def user_menu(self, interaction: Interaction) -> None:
        
        if self._pre_prompt is not None and self._pre_prompt.is_filled_out:
            if not await self._pre_prompt.send(interaction):
                return

        pages = [
            q.page(interaction.user)
            for q
            in self.questions
        ]
        frogginator = Frogginator(pages, self)
        await frogginator.respond(interaction)
    
################################################################################
    def is_complete(self, user: User) -> bool:

        for q in self.questions:
            if q.required and not q.is_complete(user):
                return False

        return True

################################################################################
    async def submit(self, interaction: Interaction) -> bool:

        if self.channel is None:
            error = ChannelNotSet("Form Channel")
            await interaction.respond(embed=error, ephemeral=True)
            return False

        if not self.is_complete(interaction.user):
            error = IncompleteForm(
                [
                    q.order 
                    for q in self.questions 
                    if not q.is_complete(interaction.user)
                    and q.required
                ]
            )
            await interaction.respond(embed=error, ephemeral=True)
            return False
        
        if self._post_prompt is not None and self._post_prompt.is_filled_out:
            if not await self._post_prompt.send(interaction):
                return False

        inter = await interaction.respond("Processing application... Please wait...")

        questions = [q.primary_text for q in self.questions]
        responses = [
            "\n".join(q[interaction.user.id])
            if q[interaction.user.id]
            else "`No Response`"
            for q in self.questions
        ]

        new_collection = FormResponseCollection.new(
            self, interaction.user, questions, responses
        )
        self._responses.append(new_collection)

        for q in self.questions:
            q.delete_response(interaction.user)

        roles = []
        users = []
        for notif in self._to_notify:
            if isinstance(notif, Role):
                roles.append(notif)
            elif isinstance(notif, User):
                users.append(notif)

        role_str = ", ".join(r.mention for r in roles)

        await inter.delete()
        msg = await self.channel.send(content=role_str or None, embed=new_collection.compile())
        
        if self._to_notify:
            confirm = U.make_embed(
                title="__Form Submitted__",
                description=(
                    f"A form has been successfully submitted.\n"
                    f"**Form Name:** `{self.name or 'Unnamed Form'}`\n\n"
                    
                    f"You can view the form response here: {msg.jump_url}"
                )
            )

            for user in users:
                try:
                    await user.send(embed=confirm)
                except:
                    pass
                
        if self.create_channel:
            await self._create_form_channel(interaction.user, new_collection)
        
        return True

################################################################################
    def prompts_status(self) -> Embed:
        
        return U.make_embed(
            title=f"__Form Prompt Status for: `{self.name}`__",
            description=(
                f"**[`Pre-Prompt Set`]:** "
                f"{BotEmojis.Check if self._pre_prompt is not None else BotEmojis.Cross}\n"
                f"**[`Post-Prompt Set`]:** "
                f"{BotEmojis.Check if self._post_prompt is not None else BotEmojis.Cross}\n\n"
            ),
            # fields=[
            #     EmbedField(
            #         name="__Pre-Prompt__",
            #         value=(
            #             "__Title__:\n"
            #             f"`{self._pre_prompt.title or 'No Title'}`\n\n"
            #             
            #             "__Description__:\n"
            #             f"```{self._pre_prompt.description or 'No Description'}```"
            #         ) if self._pre_prompt is not None else "`Not Set`",
            #         inline=False
            #     ),
            #     EmbedField(
            #         name="__Post-Prompt__",
            #         value=(
            #             "__Title__:\n"
            #             f"`{self._post_prompt.title or 'No Title'}`\n\n"
            #             
            #             "__Description__:\n"
            #             f"```{self._post_prompt.description or 'No Description'}```"
            #         ) if self._post_prompt is not None else "`Not Set`",
            #         inline=False
            #     )
            # ]
        )
    
################################################################################
    async def prompts_menu(self, interaction: Interaction) -> None:
        
        embed = self.prompts_status()
        view = FormPromptsMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
    async def pre_prompt_menu(self, interaction: Interaction) -> None:

        if self._pre_prompt is None:
            self._pre_prompt = FormPrompt.new(self, False)
        await self._pre_prompt.menu(interaction)
        
################################################################################
    async def post_prompt_menu(self, interaction: Interaction) -> None:

        if self._post_prompt is None:
            self._post_prompt = FormPrompt.new(self, True)
        await self._post_prompt.menu(interaction)
        
################################################################################
    def notifications_status(self) -> Embed:
        
        return U.make_embed(
            title=f"__Form Status for: `{self.name}`__",
            description=(
                "__**Notification Parties**__\n" + (
                    "\n".join(
                        f"* {notif.mention} ({notif.name})"
                        for notif in self._to_notify
                    )
                    if self._to_notify
                    else "`No users to notify.`"
                )
            )
        )
    
################################################################################
    async def notifications_menu(self, interaction: Interaction) -> None:

        embed = self.notifications_status()
        view = FormNotificationsMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
    async def add_notification(self, interaction: Interaction) -> None:
        
        if len(self._to_notify) >= self.MAX_TO_NOTIFY:
            error = MaxItemsReached("Users to Notify", self.MAX_TO_NOTIFY)
            await interaction.respond(embed=error, ephemeral=True)
            return

        prompt = U.make_embed(
            title="__Add User or Role?__",
            description="Would you like to notify a user or a role?"
        )
        view = FormNotificationPartyView(interaction.user, self)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete:
            return

        if view.value is False:
            await self.add_notification_role(interaction)
        else:
            await self.add_notification_user(interaction)

################################################################################
    async def remove_notification(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove User or Role?__",
            description="Would you like to remove a user or a role?"
        )
        view = FormNotificationPartyView(interaction.user, self)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete:
            return

        if view.value is False:
            await self.remove_notification_role(interaction)
        else:
            await self.remove_notification_user(interaction)

################################################################################
    async def add_notification_user(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Add User to Notify__",
            description="Mention the user you want to notify upon form submission."
        )
        user = await U.listen_for(interaction, prompt, U.MentionableType.User)
        if user is None:
            return
        
        self._to_notify.append(user)
        self.update()
    
################################################################################
    async def add_notification_role(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Add Role to Notify__",
            description="Mention the role you want to notify upon form submission."
        )
        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return

        self._to_notify.append(role)
        self.update()

################################################################################
    async def remove_notification_user(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove User to Notify__",
            description="Mention the user you want to remove from the notification list."
        )
        user = await U.listen_for(interaction, prompt, U.MentionableType.User)
        if user is None:
            return
        
        if user not in self._to_notify:
            await interaction.respond("User is not in the notification list.")
            return
        
        self._to_notify.remove(user)
        self.update()
    
################################################################################
    async def remove_notification_role(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Role to Notify__",
            description="Mention the role you want to remove from the notification list."
        )
        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return

        if role not in self._to_notify:
            await interaction.respond("Role is not in the notification list.")
            return

        self._to_notify.remove(role)
        self.update()

################################################################################
    async def _create_form_channel(self, user: User, response: FormResponseCollection) -> None:
        
        guild = self._mgr.guild.parent
        member = await self._mgr.guild.get_or_fetch_member(user.id)
        
        if self._category is not None:
            channel = await self._category.create_text_channel(member.display_name)
        else:
            channel = await guild.create_text_channel(member.display_name)
        
        await channel.set_permissions(guild.default_role, view_channel=False)
        await channel.set_permissions(member, view_channel=True)
        for role in self.channel_roles:
            await channel.set_permissions(role, view_channel=True)
        
        await channel.send(embed=response.compile())
    
################################################################################
    async def toggle_create_channel(self, interaction: Interaction) -> None:
        
        self.create_channel = not self.create_channel
        await interaction.respond("** **", delete_after=0.1)
        
################################################################################
    def channel_status(self) -> Embed:
        
        return U.make_embed(
            title=f"__Channel Roles for: `{self.name}`__",
            description=(
                "__**Creation Category**__\n"
                f"{self._category.mention if self._category else '`Not Set`'}\n\n"
                
                "__**Roles With Access to Created Channel**__\n" +
                ("\n".join(
                    f"* {r.mention} ({r.name})"
                    for r in self.channel_roles
                ) if self.channel_roles else "`Not Set`"
                )
            )
        )
    
################################################################################
    async def manage_channel(self, interaction: Interaction) -> None:
        
        embed = self.channel_status()
        view = FormChannelStatusView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    async def add_channel_role(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Add Channel Role__",
            description="Mention the role you want to have access to the created channel."
        )
        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return
        
        self._channel_roles.append(role)
        self.update()
        
################################################################################
    async def remove_channel_role(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Channel Role__",
            description="Mention the role you want to remove from the channel roles list."
        )
        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return
        
        if role not in self._channel_roles:
            await interaction.respond("Role is not in the channel roles list.")
            return
        
        self._channel_roles.remove(role)
        self.update()
        
################################################################################
    async def set_category(self, interaction: Interaction) -> None:
        
        options = [
            SelectOption(
                label=category.name,
                value=str(category.id)
            )
            for category in self._mgr.guild.parent.categories
        ]
        
        prompt = U.make_embed(
            title="__Set Creation Category__",
            description="Please select the category where created channels should be placed."
        )
        view = FroggeSelectView(interaction.user, options)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.category_channel = self.bot.get_channel(int(view.value))
        
################################################################################
