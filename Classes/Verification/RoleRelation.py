from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar, Tuple, Any

from discord import (
    Role,
    Embed,
    EmbedField,
    Interaction, 
    SelectOption,
    Member,
    Forbidden
)
from Utilities import Utilities as U
from Errors import InsufficientPermissions
from UI.Verification import RoleRelationStatusView
from UI.Common import ConfirmCancelView, BasicTextModal

if TYPE_CHECKING:
    from Classes import VerificationManager, RentARaBot
################################################################################

__all__ = ("RoleRelation", )

RR = TypeVar("RR", bound="RoleRelation")

################################################################################
class RoleRelation:

    __slots__ = (
        "_id",
        "_mgr",
        "_pending",
        "_final",
        "_message",
    )
    
################################################################################
    def __init__(self, mgr: VerificationManager, _id: str, **kwargs) -> None:

        self._id: str = _id
        self._mgr: VerificationManager = mgr
        
        self._pending: Optional[Role] = kwargs.get("pending")
        self._final: Optional[Role] = kwargs.get("final")
        
        self._message: Optional[str] = kwargs.get("message")
    
################################################################################
    @classmethod
    def new(cls: Type[RR], mgr: VerificationManager) -> RR:
        
        new_id = mgr.bot.database.insert.role_relation(mgr.guild_id)
        return cls(mgr, new_id)
    
################################################################################
    @classmethod
    async def load(cls: Type[RR], mgr: VerificationManager, data: Tuple[Any, ...]) -> RR:
        
        return cls(
            mgr=mgr,
            _id=data[0],
            pending=await mgr.guild.get_or_fetch_role(data[2]),
            final=await mgr.guild.get_or_fetch_role(data[3]),
            message=data[4],
        )
    
################################################################################
    def __eq__(self, other: RoleRelation) -> bool:
        
        return self.id == other.id
    
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
    def pending_role(self) -> Optional[Role]:
        
        return self._pending
    
    @pending_role.setter
    def pending_role(self, role: Optional[Role]) -> None:
        
        self._pending = role
        self.update()
        
################################################################################
    @property
    def final_role(self) -> Optional[Role]:
        
        return self._final
    
    @final_role.setter
    def final_role(self, role: Optional[Role]) -> None:
        
        self._final = role
        self.update()
        
################################################################################
    @property
    def message(self) -> Optional[str]:
        
        return self._message
    
    @message.setter
    def message(self, message: Optional[str]) -> None:
        
        self._message = message
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.role_relation(self)
        
################################################################################
    def delete(self) -> None:
        
        self.bot.database.delete.role_relation(self)
        self._mgr.role_relations.remove(self)
        
################################################################################
    def status(self) -> Embed:
        
        pending_value = (
            self.pending_role.mention 
            if self.pending_role is not None 
            else "`Not Set`"
        )
        final_value = (
            self.final_role.mention 
            if self.final_role is not None 
            else "`Not Set`"
        )
        
        return U.make_embed(
            title="__Role Relation Status__",
            description=(
                "__**Welcome Message**__\n"
                f"{self.message or '`Not Set`'}"
            ),
            fields=[
                EmbedField(
                    name="__Pending Role__",
                    value=(
                        f"{pending_value}\n"
                        "*(Role that the user will\n"
                        "have prior to verification)*"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Final Role__",
                    value=(
                        f"{final_value}\n"
                        "*(Role that the user will\n"
                        "be given after verification)*"
                    ),
                    inline=True
                )
            ]
        )
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = RoleRelationStatusView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    async def set_pending(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Set Pending Role__",
            description=(
                "Please mention the role that you would like to set as the pending role.\n"
                "*(Role that the user will have prior to verification)*"
            )
        )
        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return
        
        self.pending_role = role
        
################################################################################
    async def set_final(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Set Future Role__",
            description=(
                "Please mention the role that you would like to set as the future role.\n"
                "*(Role that the user will be given after successful verification)*"
            )
        )
        role = await U.listen_for(interaction, prompt, U.MentionableType.Role)
        if role is None:
            return
        
        self.final_role = role
        
################################################################################
    def select_option(self) -> SelectOption:
        
        pending_value = (
            self.pending_role.name 
            if self.pending_role is not None 
            else "Pending Not Set"
        )
        final_value = (
            self.final_role.name 
            if self.final_role is not None 
            else "uFinal Not Set"
        )
        
        return SelectOption(
            label=U.string_clamp(f"{pending_value} -> {final_value}", 95),
            value=self.id
        )
    
################################################################################
    async def remove(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Role Relation__",
            description=(
                "Are you sure you want to remove this role relation?\n"
                "*(This action cannot be undone)*"
            )
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.delete()

################################################################################
    async def check_swap(self, interaction: Interaction, member: Member) -> Optional[str]:
        
        if self.pending_role is None or self.final_role is None:
            return
        
        if self.pending_role not in member.roles:
            return
        
        try:
            await member.remove_roles(self.pending_role)
            await member.add_roles(self.final_role)
        except Forbidden:
            error = InsufficientPermissions(None, "Manage Roles")
            await interaction.respond(embed=error, ephemeral=True)
        else:
            return self.message

################################################################################
    async def set_message(self, interaction: Interaction) -> None:
        
        modal = BasicTextModal(
            title="Set Welcome Message Text",
            attribute="Text",
            cur_val=self.message,
            max_length=2000,
            required=False,
            multiline=True
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        self.message = modal.value
        
################################################################################
