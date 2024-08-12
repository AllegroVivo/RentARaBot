from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Type, TypeVar, Any, Tuple

from Enums import Gender, BedroomPreference, Race
from discord import Embed, EmbedField, Interaction

from Utilities import Utilities as U
from UI.Common import FroggeSelectView
from UI.Profiles import PreferenceGroupStatusView

if TYPE_CHECKING:
    from Classes import ProfilePreferences, RentARaBot
################################################################################

__all__ = ("PreferenceGroup", )

PG = TypeVar("PG", bound="PreferenceGroup")

################################################################################
class PreferenceGroup:

    __slots__ = (
        "_id",
        "_parent",
        "_gender",
        "_bedroom",
        "_preferences",
        "_restrictions",
    )
    
################################################################################
    def __init__(self, parent: ProfilePreferences, _id: str, gender: Gender, **kwargs) -> None:

        self._id: str = _id
        self._parent: ProfilePreferences = parent
        self._gender: Gender = gender
        
        self._bedroom: Optional[BedroomPreference] = kwargs.get("bedroom")
        self._preferences: List[Race] = kwargs.get("preferences", [])
        self._restrictions: List[Race] = kwargs.get("restrictions", [Race.Lalafell])
    
################################################################################
    @classmethod
    def new(cls: Type[PG], parent: ProfilePreferences, gender: Gender) -> PG:
        
        new_id = parent.bot.database.insert.preference_group(parent.profile_id, gender.value)
        return cls(parent, new_id, gender)
    
################################################################################
    @classmethod
    def load(cls: Type[PG], parent: ProfilePreferences, data: Tuple[Any, ...]) -> PG:
        
        return cls(
            parent=parent,
            _id=data[0],
            gender=Gender(data[2]),
            bedroom=BedroomPreference(data[3]) if data[3] else None,
            preferences=[Race(r) for r in data[4]],
            restrictions=[Race(r) for r in data[5]]
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
    def gender(self) -> Gender:
        
        return self._gender
    
################################################################################
    @property
    def bedroom_pref(self) -> Optional[BedroomPreference]:
        
        return self._bedroom
    
    @bedroom_pref.setter
    def bedroom_pref(self, value: Optional[BedroomPreference]) -> None:
        
        self._bedroom = value
        self.update()
    
################################################################################
    @property
    def preferences(self) -> List[Race]:
        
        self._preferences.sort(key=lambda r: r.name)
        return self._preferences
    
    @preferences.setter
    def preferences(self, value: List[Race]) -> None:
        
        self._preferences = value
        self.update()
    
################################################################################
    @property
    def restrictions(self) -> List[Race]:
        
        self._restrictions.sort(key=lambda r: r.name)
        return self._restrictions
    
    @restrictions.setter
    def restrictions(self, value: List[Race]) -> None:
        
        self._restrictions = value
        self.update()
        
################################################################################
    @property
    def is_complete(self) -> bool:
        
        return all([
            self._bedroom is not None,
            self._preferences,
            self._restrictions
        ]) 
    
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.preference_group(self)
        
################################################################################
    def status(self) -> Embed:

        prefs = U.split_lines([p.proper_name for p in self.preferences], 20)
        rests = U.split_lines([p.proper_name for p in self.restrictions], 20)

        return U.make_embed(
            title=f"__{self.gender.proper_name} Preference Settings__",
            fields=[
                EmbedField(
                    name="__Bedroom Preference__",
                    value=f"`{self.bedroom_pref.proper_name}`" if self.bedroom_pref else "`Not Set`",
                    inline=False
                ),
                EmbedField(
                    name="__Preferences__",
                    value=prefs or "`Not Set`",
                    inline=True
                ),
                EmbedField(
                    name="__Restrictions__",
                    value=rests or "`Not Set`",
                    inline=True
                )
            ]
        )
    
################################################################################
    def compile(self, force_return: bool = False) -> Optional[List[EmbedField]]:
        
        if not self.bedroom_pref and not force_return:
            return
        
        prefs = U.split_lines([p.proper_name for p in self.preferences], 20)
        rests = U.split_lines([p.proper_name for p in self.restrictions], 20)
        
        return [
            EmbedField(
                name=f"__With {self.gender.short_name}'s I'm__",
                value=f"`{self.bedroom_pref.proper_name}`" if self.bedroom_pref else "`Not Set`",
                inline=True
            ),
            EmbedField(
                name=f"__{self.gender.short_name} Preferences__",
                value=prefs or "`None`",
                inline=True
            ),
            EmbedField(
                name=f"__{self.gender.short_name} Restrictions__",
                value=rests or "`None`",
                inline=True
            )
        ]
        
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = PreferenceGroupStatusView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
    async def set_bedroom_pref(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Set Bedroom Preference__",
            description=(
                "Please select the bedroom preference you would like to set for "
                f"{self.gender.proper_name} individuals.\n\n"
                
                "Select `Not Applicable` to remove the current preference."
            )
        )
        view = FroggeSelectView(interaction.user, BedroomPreference.select_options())
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        pref = BedroomPreference(int(view.value))
        self.bedroom_pref = pref if pref != BedroomPreference.NA else None
    
################################################################################
    async def set_preferences(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Set Racial Preference(s)__",
            description=(
                "Please select the race(s) you would be looking for in a "
                f"`{self.gender.proper_name}` partner.\n\n"
            )
        )
        options = [r.select_option for r in Race if r not in self.restrictions and r != Race.Custom]
        view = FroggeSelectView(interaction.user, options, multi_select=True)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.preferences = [Race(int(v)) for v in view.value]
        
################################################################################
    async def set_restrictions(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Set Racial Restriction(s)__",
            description=(
                "Please select the race(s) you are explicitly **NOT** "
                f"looking for in a `{self.gender.proper_name}` partner.\n\n"
            )
        )
        options = [
            r.select_option 
            for r in Race 
            if r not in self.preferences and r not in (Race.Custom, Race.Lalafell)
        ]
        view = FroggeSelectView(interaction.user, options, multi_select=True)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.restrictions = [Race(int(v)) for v in view.value] + [Race.Lalafell]
        
################################################################################
