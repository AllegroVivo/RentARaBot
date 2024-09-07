from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Tuple, Any

from discord import Embed, Interaction

from Assets import BotEmojis
from UI.Common import BasicTextModal, ConfirmCancelView, ConfirmView
from UI.Forms import FormPromptStatusView
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import Form, RentARaBot
################################################################################

__all__ = ("FormPrompt",)

QP = TypeVar("QP", bound="QuestionPrompt")

################################################################################
class FormPrompt:

    __slots__ = (
        "_id",
        "_parent",
        "_title",
        "_description",
        "_thumbnail",
        "_after",
        "_show_cancel"
    )

################################################################################
    def __init__(self, parent: Form, _id: str, **kwargs) -> None:

        self._id: str = _id
        self._parent: Form = parent

        self._title: Optional[str] = kwargs.get("title")
        self._description: Optional[str] = kwargs.get("description")
        self._thumbnail: Optional[str] = kwargs.get("thumbnail")
        self._after: bool = kwargs.get("after", True)
        self._show_cancel: bool = kwargs.get("show_cancel", False)

################################################################################
    @classmethod
    def new(cls: Type[QP], parent: Form, post: bool) -> QP:

        new_id = parent.bot.database.insert.form_prompt(parent.id, post)
        return cls(parent, new_id, after=post)

################################################################################
    @classmethod
    def load(cls: Type[QP], parent: Form, data: Tuple[Any, ...]) -> QP:

        return cls(
            parent=parent,
            _id=data[0],
            title=data[2],
            description=data[3],
            thumbnail=data[4],
            show_cancel=data[5],
            after=data[6]
        )

################################################################################
    @property
    def bot(self) -> RentARaBot:

        return self._parent.bot

################################################################################
    @property
    def id(self) -> str:

        return self._id

################################################################################
    @property
    def title(self) -> Optional[str]:

        return self._title

    @title.setter
    def title(self, value: str) -> None:

        self._title = value
        self.update()

################################################################################
    @property
    def description(self) -> Optional[str]:

        return self._description

    @description.setter
    def description(self, value: str) -> None:

        self._description = value
        self.update()

################################################################################
    @property
    def thumbnail(self) -> Optional[str]:

        return self._thumbnail

    @thumbnail.setter
    def thumbnail(self, value: Optional[str]) -> None:

        self._thumbnail = value
        self.update()

################################################################################
    @property
    def show_after(self) -> bool:

        return self._after

    @show_after.setter
    def show_after(self, value: bool) -> None:

        self._after = value
        self.update()

################################################################################
    @property
    def show_cancel(self) -> bool:
            
        return self._show_cancel
    
    @show_cancel.setter
    def show_cancel(self, value: bool) -> None:
        
        self._show_cancel = value
        self.update()
        
################################################################################
    @property
    def is_filled_out(self) -> bool:
        
        return all([
            self.title is not None,
            self.description is not None,
        ])
    
################################################################################
    def update(self) -> None:

        self.bot.database.update.form_prompt(self)

################################################################################
    def delete(self) -> None:

        self.bot.database.delete.form_prompt(self)
        
        if self.show_after:
            self._parent._post_prompt = None
        else:
            self._parent._pre_prompt = None

################################################################################
    def status(self) -> Embed:

        return U.make_embed(
            title="__Form Prompt Status__",
            description=(
                f"**[`Display Cancel Button`]:** "
                f"{BotEmojis.Check if self.show_cancel else BotEmojis.Cross}\n"
                f"**[`Title`]:**"
                f"\n`{self.title or 'No Title'}`\n\n"

                f"**[`Description`]:**\n"
                f"```{self.description or 'No Description'}```\n"
            ),
            thumbnail_url=self.thumbnail
        )

################################################################################
    def compile(self) -> Embed:
        
        return U.make_embed(
            title=self.title,
            description=self.description,
            thumbnail_url=self.thumbnail
        )
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:

        embed = self.status()
        view = FormPromptStatusView(interaction.user, self)

        await interaction.respond(embed=embed, view=view)
        await view.wait()

################################################################################
    async def set_title(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Question Prompt Title",
            attribute="Title",
            cur_val=self.title,
            example="e.g. 'Be Aware!'",
            max_length=80,
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.title = modal.value

################################################################################
    async def set_description(self, interaction: Interaction) -> None:

        modal = BasicTextModal(
            title="Set Question Prompt Description",
            attribute="Description",
            cur_val=self.description,
            example="e.g. 'This question is very important!'",
            max_length=200,
            multiline=True
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.complete:
            return

        self.description = modal.value

################################################################################
    async def set_thumbnail(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Question Prompt Thumbnail__",
            description=(
                "Please provide an image that you would like to use as the thumbnail.\n\n"

                "This image will be displayed alongside the prompt."
            )
        )
        image_url = await U.wait_for_image(interaction, prompt)
        if image_url is None:
            return

        self.thumbnail = image_url

################################################################################
    async def remove(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Question Prompt__",
            description=(
                "Are you sure you want to remove this question prompt?"
            )
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.delete()

################################################################################
    async def send(self, interaction: Interaction) -> bool:
        
        embed = self.compile()
        if not self._show_cancel:
            view = ConfirmView(interaction.user)
        else:
            view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
        if not view.complete:
            return False
        
        return view.value
        
################################################################################
    async def toggle_cancel_button(self, interaction: Interaction) -> None:
        
        self.show_cancel = not self.show_cancel
        await interaction.respond("** **", delete_after=0.1)
        
################################################################################
