from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Type, TypeVar

from discord import User, Embed, EmbedField, Interaction

from Assets import BotEmojis
from Utilities import (
    Utilities as U,
    DateHours,
    FroggeEnum
)

if TYPE_CHECKING:
    from Classes import DatingManager, RentARaBot, Patron
################################################################################

__all__ = ("DatingRequest",)

DR = TypeVar("DR", bound="DatingRequest")

################################################################################
class DatingRequest:
    
    __slots__ = (
        "_id",
        "_mgr",
        "_requester",
        "_sfw",
        "_escort",
        "_dt",
        "_selection",
        "_length",
        "_sfw_plan",
        "_location"
    )
    
################################################################################
    def __init__(self, mgr: DatingManager, **kwargs):
        
        self._id: str = kwargs.pop("_id")
        self._mgr: DatingManager = mgr
        self._requester: Patron = kwargs.pop("requester")
        
        self._sfw: bool = kwargs.get("sfw", True)
        self._escort: bool = kwargs.get("escort", False)
        self._dt: Optional[datetime] = kwargs.get("dt")
        self._selection: Optional = kwargs.get("selection")
        self._length: DateHours = kwargs.get("length", DateHours.DontKnow)
        self._sfw_plan: Optional[bool] = kwargs.get("sfw_plan")
        self._location: Optional[str] = kwargs.get("location")
        
################################################################################
    @classmethod
    def new(cls: Type[DR], mgr: DatingManager, patron: Patron) -> DR:
        
        new_id = mgr.bot.database.insert.dating_request(patron.user.id, mgr.guild_id)
        return cls(mgr, _id=new_id, requester=patron)
    
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
    def requester(self) -> Patron:
        
        return self._requester
    
################################################################################
    @property
    def sfw(self) -> bool:
        
        return self._sfw
    
    @sfw.setter
    def sfw(self, value: bool) -> None:
        
        self._sfw = value
        self.update()
        
################################################################################
    @property
    def escort(self) -> bool:
        
        return self._escort
    
    @escort.setter
    def escort(self, value: bool) -> None:
        
        self._escort = value
        self.update()
        
################################################################################
    @property
    def desired_time(self) -> Optional[datetime]:
        
        return self._dt
    
    @desired_time.setter
    def desired_time(self, value: Optional[datetime]) -> None:
        
        self._dt = value
        self.update()
        
################################################################################
    @property
    def selection(self) -> Optional:
        
        return self._selection
    
    @selection.setter
    def selection(self, value: Optional) -> None:
        
        self._selection = value
        self.update()
        
################################################################################
    @property
    def length(self) -> DateHours:
        
        return self._length
    
    @length.setter
    def length(self, value: DateHours) -> None:
        
        self._length = value
        self.update()
        
################################################################################
    @property
    def sfw_plan(self) -> Optional[bool]:
        
        return self._sfw_plan
    
    @sfw_plan.setter
    def sfw_plan(self, value: Optional[bool]) -> None:
        
        self._sfw_plan = value
        self.update()
        
################################################################################
    @property
    def location(self) -> Optional[str]:
        
        return self._location
    
    @location.setter
    def location(self, value: Optional[str]) -> None:
        
        self._location = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self._mgr.bot.database.update.dating_request(self)
        
################################################################################
    def status(self) -> Embed:
        
        date_plan_value = (
            f"{str(BotEmojis.Check)} __**Yes!**__ {str(BotEmojis.Check)}\n*"
            f"\"I would like help planning the SFW date.*\""
            if self._sfw_plan
            else f"{str(BotEmojis.Cross)} __**No~**__ {str(BotEmojis.Cross)}\n"
                 f"*\"I will plan the date myself.*\""
        ) if self._sfw_plan is not None else "`Not Applicable - NSFW Date`"
        
        return U.make_embed(
            title="Dating Request",
            description=(
                f"Requester: {self._requester.user.mention}\n"
                f"{U.draw_line(extra=25)}"
            ),
            fields=[
                EmbedField(
                    name="__SFW Date?__", 
                    value=(
                        str(BotEmojis.Check) if self.sfw
                        else str(BotEmojis.Cross)
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Escort Date?__", 
                    value=(
                        str(BotEmojis.Check) if self.escort
                        else str(BotEmojis.Cross)
                    ),
                    inline=True
                ),
                EmbedField("** **", "** **", inline=False),
                EmbedField(
                    name="__Desired Time__", 
                    value=(
                        U.format_dt(self.desired_time, 'f') if self.desired_time
                        else "`Not Set`"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Meeting Location__",
                    value=self.location if self.location is not None else "`Not Set`",
                    inline=True
                ),
                EmbedField(
                    name="__Staff Selection__",
                    value="`Not Implemented`",
                    inline=False
                ),
                EmbedField(
                    name="__Date Length__", 
                    value=(
                        f"`{self.length.proper_name} Hours`"
                        if self.length is not DateHours.DontKnow
                        else "`I Don't Know`"
                    ),
                    inline=True
                ),
                EmbedField(
                    name="__Date Planning Service__", 
                    value=date_plan_value,
                    inline=True
                ),
            ]
        )
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        # view = 
        
        await interaction.respond(embed=embed)
        # await view.wait()
        
################################################################################
        