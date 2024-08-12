from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Any, Dict

from discord import Embed, Interaction, SelectOption

from .Form import Form
from Errors import MaxItemsReached
from UI.Common import BasicTextModal, FroggeSelectView, ConfirmCancelView
from UI.Forms import FormsManagerMenuView
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import GuildData, RentARaBot
################################################################################

__all__ = ("FormsManager",)

################################################################################
class FormsManager:

    __slots__ = (
        "_state",
        "_forms",
        "_dating",
        "_battle",
    )
    
    MAX_FORMS = 20
    
################################################################################
    def __init__(self, state: GuildData) -> None:

        self._state: GuildData = state
        self._forms: List[Form] = []
    
################################################################################
    async def load_all(self, payload: List[Dict[str, Any]]) -> None:
        
        self._forms = [await Form.load(self, f) for f in payload]
    
################################################################################
    def __getitem__(self, form_id: str) -> Optional[Form]:
        
        return next((f for f in self._forms if f.id == form_id), None)
    
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
    def forms(self) -> List[Form]:
        
        return self._forms
    
################################################################################
    def status(self) -> Embed:
        
        forms_string = "\n".join(
            f"* **{f.name}**"
            for f in self.forms
        )
        if not forms_string:
            forms_string = "`No forms configured.`"
        
        return U.make_embed(
            title="__Forms Management__",
            description=(
                f"**[`Total Forms`]:** `{len(self._forms)}`\n\n"
                
                f"**[`Forms`]:**\n"
                f"{forms_string}"
            )
        )
    
################################################################################
    async def main_menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = FormsManagerMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    async def add_form(self, interaction: Interaction) -> None:
        
        if len(self.forms) >= self.MAX_FORMS:
            error = MaxItemsReached("Form", self.MAX_FORMS)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        modal = BasicTextModal(
            title="Enter Form Name",
            attribute="Name",
            example='e.g. "Staff Application Form"',
            max_length=80
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        form = Form.new(self, modal.value)
        self._forms.append(form)
        
        await form.menu(interaction)
        
################################################################################
    async def modify_form(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Form__",
            description="Pick a form from the list below to modify."
        )
        view = FroggeSelectView(interaction.user, self.form_select_options())
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        form = self[view.value]
        await form.menu(interaction)
    
################################################################################
    async def remove_form(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Remove Form__",
            description="Pick a form from the list below to remove."
        )
        view = FroggeSelectView(interaction.user, self.form_select_options())

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        form = self[view.value]
        await form.remove(interaction)
    
################################################################################
    async def user_menu(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Complete a Form__",
            description="Select a form type below to continue."
        )
        view = FroggeSelectView(interaction.user, self.form_select_options())
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        form = self[view.value]
        await form.user_menu(interaction)
        
################################################################################
    def form_select_options(self) -> List[SelectOption]:

        options = [f.select_option() for f in self.forms]
        if not options:
            options.append(
                SelectOption(
                    label="No forms available",
                    value="-1",
                    description="No forms have been configured yet."
                )
            )
            
        return options
    
################################################################################
