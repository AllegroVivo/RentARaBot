from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Type, TypeVar, Dict, Any

from discord import TextChannel, Embed, EmbedField, Interaction, SelectOption, User

from .FormQuestion import FormQuestion
from .FormResponseCollection import FormResponseCollection
from Errors import MaxItemsReached, ChannelNotSet, IncompleteForm
from UI.Common import BasicTextModal, FroggeSelectView, ConfirmCancelView, Frogginator
from UI.Forms import FormStatusView
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import FormsManager, RentARaBot
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
    )
    
    MAX_QUESTIONS = 20
    
################################################################################
    def __init__(self, mgr: FormsManager, _id: str, **kwargs) -> None:

        self._id: str = _id
        self._mgr: FormsManager = mgr
        self._name: Optional[str] = kwargs.get("name")
        
        self._questions: List[FormQuestion] = kwargs.get("questions", [])
        self._responses: List[FormResponseCollection] = kwargs.get("responses", [])
        self._channel: Optional[TextChannel] = kwargs.get("channel")
    
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
        
        return self
    
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
    def update(self) -> None:
        
        self.bot.database.update.form(self)
        
################################################################################
    def delete(self) -> None:
        
        self.bot.database.delete.form(self)
        self._mgr.forms.remove(self)

################################################################################
    def status(self) -> Embed:
        
        return U.make_embed(
            title=f"__Form Status for: `{self.name}`__",
            description=(
                f"**Questions:** [{len(self._questions)}]\n"
                f"**Form Log Channel:** "
                f"{self.channel.mention if self.channel else '`Not Set`'}\n\n"

                "Press a button below to modify the form."
            )
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
        
        pass
    
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
            error = ChannelNotSet("Staff Applications")
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

        await inter.delete_original_response()
        await self.channel.send(embed=new_collection.compile())
        
        return True

################################################################################
