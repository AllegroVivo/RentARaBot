from __future__ import annotations

from typing import TYPE_CHECKING, List, Type, TypeVar, Any, Tuple, Dict, Optional

from discord import Embed, EmbedField, Interaction, User

from Enums import Gender, FFXIVActivity, MusicGenre, ZodiacSign, Race
from UI.Common import FroggeSelectView
from .ProfileSection import ProfileSection
from .PreferenceGroup import PreferenceGroup
from Utilities import Utilities as U
from UI.Profiles import ProfilePreferencesMenuView
if TYPE_CHECKING:
    from Classes import Profile
################################################################################

__all__ = ("ProfilePreferences", )

PP = TypeVar("PP", bound="ProfilePreferences")

################################################################################
class ProfilePreferences(ProfileSection):

    __slots__ = (
        "_groups",
        "_activities",
        "_music",
        "_zodiac_self",
        "_zodiac_partners",
    )
    
################################################################################
    def __init__(self, parent: Profile, **kwargs) -> None:

        super().__init__(parent)
        
        self._groups: List[PreferenceGroup] = kwargs.get("groups", None) or [
            PreferenceGroup.new(self, Gender.Male),
            PreferenceGroup.new(self, Gender.Female),
            PreferenceGroup.new(self, Gender.NonBinary),
        ]
        
        self._activities: List[FFXIVActivity] = kwargs.get("activities", [])
        self._music: List[MusicGenre] = kwargs.get("music", [])
        self._zodiac_self: Optional[ZodiacSign] = kwargs.get("zodiac_self", None)
        self._zodiac_partners: List[ZodiacSign] = kwargs.get("zodiac_partner", [])
    
################################################################################
    @classmethod
    def load(cls: Type[PP], parent: Profile, data: Dict[str, Any]) -> PP:
        
        pdata = data["preferences"]
        
        self: PP = cls.__new__(cls)
        
        self._parent = parent
        
        self._groups = [PreferenceGroup.load(self, d) for d in data["groups"]]
        
        self._activities = [FFXIVActivity(a) for a in pdata[1]]
        self._music = [MusicGenre(m) for m in pdata[2]]
        
        self._zodiac_self = ZodiacSign(pdata[3]) if pdata[3] else None
        self._zodiac_partners = [ZodiacSign(z) for z in pdata[4]]
        
        return self
    
################################################################################
    @property
    def preference_groups(self) -> List[PreferenceGroup]:
        
        self._groups.sort(key=lambda g: g.gender)
        return self._groups
    
################################################################################
    @property
    def activities(self) -> List[FFXIVActivity]:
        
        return self._activities
    
    @activities.setter
    def activities(self, value: List[FFXIVActivity]) -> None:
        
        self._activities = value
        self.update()
        
################################################################################
    @property
    def music_prefs(self) -> List[MusicGenre]:
        
        return self._music
    
    @music_prefs.setter
    def music_prefs(self, value: List[MusicGenre]) -> None:
        
        self._music = value
        self.update()
        
################################################################################
    @property
    def zodiac_self(self) -> Optional[ZodiacSign]:
        
        return self._zodiac_self
    
    @zodiac_self.setter
    def zodiac_self(self, value: ZodiacSign) -> None:
        
        self._zodiac_self = value
        self.update()
        
################################################################################
    @property
    def zodiac_partners(self) -> List[ZodiacSign]:
        
        return self._zodiac_partners
    
    @zodiac_partners.setter
    def zodiac_partners(self, value: List[ZodiacSign]) -> None:
        
        self._zodiac_partners = value
        self.update()
        
################################################################################
    @property
    def male_prefs(self) -> PreferenceGroup:
        
        return self.get_preference(Gender.Male)
    
################################################################################
    @property
    def female_prefs(self) -> PreferenceGroup:

        return self.get_preference(Gender.Female)
    
################################################################################
    @property
    def nb_prefs(self) -> PreferenceGroup:

        return self.get_preference(Gender.NonBinary)
    
################################################################################
    def is_matchable(self) -> bool:
        
        return all([
            self.parent.ataglance.gender,
            self.parent.ataglance.race,
            self.activities,
            self.music_prefs,
            self.zodiac_self,
            self.zodiac_partners,
            (
                self.male_prefs.is_complete or
                self.female_prefs.is_complete or
                self.nb_prefs.is_complete
            )
        ])
        
################################################################################
    def status(self) -> Embed:
        
        fields = self.male_prefs.compile(True)
        fields.extend(self.female_prefs.compile(True))
        fields.extend(self.nb_prefs.compile(True))
        fields.extend([
            EmbedField(
                name=U.draw_line(extra=40),
                value="** **",
                inline=False
            )
        ])

        activities = [a.proper_name for a in self.activities]
        if activities:
            col1, col2 = U.list_to_columns(activities, 2)
        else:
            col1 = "`Not Set`"
            col2 = "** **"
            
        fields.extend([
            EmbedField(name="__Favorite In-Game Activities__", value=col1, inline=True),
            EmbedField(name="** **", value=col2, inline=True),
            EmbedField("** **", "** **", inline=False)
        ])

        music = [m.proper_name for m in self.music_prefs]
        if music:
            col1, col2 = U.list_to_columns(music, 2)
        else:
            col1 = "`Not Set`"
            col2 = "** **"

        fields.extend([
            EmbedField(name="__Music Genre Preferences__", value=col1, inline=True),
            EmbedField(name="** **", value=col2, inline=True),
        ])
        
        if self.zodiac_self:
            zodiac_self = self.zodiac_self.proper_name
            self_emoji = self.zodiac_self.emoji
        else:
            zodiac_self = "Not Set"
            self_emoji = ""
            
        if self.zodiac_partners:
            partners = [f"{z.emoji} {z.proper_name}" for z in self.zodiac_partners]
        else:
            partners = ["`Not Set`"]
        
        return U.make_embed(
            color=self.parent.color,
            title="__Racial Preferences and Favorite Activities__",
            description=(
                f"**My Zodiac Sign Is:** {str(self_emoji)} `{zodiac_self}`\n"
                f"**My Ideal Partner Is:** {', '.join(partners)}"
            ),
            fields=fields,  # type: ignore
        )
    
################################################################################
    def compile(self) -> Optional[Embed]:

        male_group = self.male_prefs.compile()
        female_group = self.female_prefs.compile()
        nb_group = self.nb_prefs.compile()
        
        fields = []
        if male_group is not None:
            fields.extend(male_group)
        if female_group is not None:
            fields.extend(female_group)
        if nb_group is not None:
            fields.extend(nb_group)
            
        # Divider
        if fields:
            fields.append(
                EmbedField(
                    name=U.draw_line(extra=40),
                    value="** **",
                    inline=False
                )
            )
        
        if self.activities:
            activities = [a.proper_name for a in self.activities]
            col1, col2 = U.list_to_columns(activities, 2)
            fields.extend([
                EmbedField(name="__Favorite In-Game Activities__", value=col1, inline=True),
                EmbedField(name="** **", value=col2, inline=True),
                EmbedField("** **", "", inline=False)
            ])

        if self.music_prefs:
            music = [m.proper_name for m in self.music_prefs]
            col1, col2 = U.list_to_columns(music, 2)
            fields.extend([
                EmbedField(name="__Music Genre Preferences__", value=col1, inline=True),
                EmbedField(name="** **", value=col2, inline=True),
            ])
            
        if not fields and not any([self.zodiac_self, self.zodiac_partners]):
            return

        if self.zodiac_self:
            zodiac_self = self.zodiac_self.proper_name
            self_emoji = self.zodiac_self.emoji
        else:
            zodiac_self = "Not Set"
            self_emoji = ""

        if self.zodiac_partners:
            partners = [f"{z.emoji} {z.proper_name}" for z in self.zodiac_partners]
        else:
            partners = ["`Not Set`"]
        
        return U.make_embed(
            color=self.parent.color,
            title="__Racial Preferences and Favorite Activities__",
            description=(
                f"**My Zodiac Sign Is:** {str(self_emoji)} `{zodiac_self}`\n"
                f"**My Ideal Partner Is:** {', '.join(partners)}\n"
                f"{U.draw_line(extra=40)}"
            ),
            fields=fields,
        )
    
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.profile_preferences(self)
        
################################################################################
    async def menu(self, interaction: Interaction) -> None:
    
        embed = self.status()
        view = ProfilePreferencesMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    def get_preference(self, gender: Gender) -> PreferenceGroup:
        
        return next((g for g in self._groups if g.gender == gender), None)
    
################################################################################
    async def set_male_prefs(self, interaction: Interaction) -> None:
        
        await self.male_prefs.menu(interaction)
        
################################################################################
    async def set_female_prefs(self, interaction: Interaction) -> None:

        await self.female_prefs.menu(interaction)
        
################################################################################
    async def set_nb_prefs(self, interaction: Interaction) -> None:

        await self.nb_prefs.menu(interaction)
        
################################################################################
    async def set_activities(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Favorite In-Game Activities__",
            description=(
                "Please select your favorite in-game activities from the selector below."
            ),
        )
        view = FroggeSelectView(interaction.user, FFXIVActivity.select_options(), multi_select=True)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.activities = [FFXIVActivity(int(a)) for a in view.value]
        
################################################################################
    async def set_music_prefs(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Music Genre Preferences__",
            description=(
                "Please select your favorite music genres from the selector below."
            ),
        )
        view = FroggeSelectView(interaction.user, MusicGenre.select_options(), multi_select=True)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.music_prefs = [MusicGenre(int(m)) for m in view.value]
        
################################################################################
    async def set_zodiac_self(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Set Zodiac Sign__",
            description=(
                "Please select your astrological sign from the selector below."
            ),
        )
        view = FroggeSelectView(interaction.user, ZodiacSign.select_options())
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.zodiac_self = ZodiacSign(int(view.value))
        
################################################################################
    async def set_zodiac_partners(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Set Preferred Zodiac Signs__",
            description=(
                "Please select the astrological signs you are most compatible with."
            ),
        )
        view = FroggeSelectView(
            owner=interaction.user,
            options=ZodiacSign.select_options(),
            multi_select=True
        )
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.zodiac_partners = [ZodiacSign(int(z)) for z in view.value]
        
################################################################################
    def progress(self) -> str:

        em_male = self.progress_emoji(self.male_prefs.is_complete)
        em_female = self.progress_emoji(self.female_prefs.is_complete)
        em_nonbin = self.progress_emoji(self.nb_prefs.is_complete)
        em_activities = self.progress_emoji(self.activities)
        em_music = self.progress_emoji(self.music_prefs)
        em_zodiac_self = self.progress_emoji(self.zodiac_self)
        em_zodiac_partners = self.progress_emoji(self.zodiac_partners)

        return (
            f"{U.draw_line(extra=15)}\n"
            "__**Preferences and Activities**__\n"
            f"{em_zodiac_self} -- Zodiac Sign\n"
            f"{em_zodiac_partners} -- Preferred Zodiac Signs\n"
            f"{em_male} -- Male Preferences\n"
            f"{em_female} -- Female Preferences\n"
            f"{em_nonbin} -- NB Preferences\n"
            f"{em_activities} -- FFXIV Activities\n"
            f"{em_music} -- Music Preferences\n"
        )

################################################################################
    def match(self, profile: Profile) -> Optional[Tuple[Profile, int]]:

        preferences = profile.preferences

        match_value = 0
        match_max = 0

        self_gender = self.parent.ataglance.gender
        self_race = self.parent.ataglance.race
        if isinstance(self_race, Race):
            match_max += 1
            if self_race in preferences.get_preference(self_gender).preferences:
                match_value += 1
            if self_race in preferences.get_preference(self_gender).restrictions:
                match_value -= 1

        if isinstance(self_gender, Gender):
            match_max += 1
            if preferences.get_preference(self_gender).is_complete:
                match_value += 1

        if self.zodiac_self and self.zodiac_partners:
            match_max += 2
            if preferences.zodiac_self in self.zodiac_partners:
                match_value += 1
            if self.zodiac_self in preferences.zodiac_partners:
                match_value += 1

        for activity in preferences.activities:
            match_max += 1
            if activity in self.activities:
                match_value += 1
        for music in preferences.music_prefs:
            match_max += 1
            if music in self.music_prefs:
                match_value += 1

        return profile, int((match_value / match_max) * 100)

################################################################################
