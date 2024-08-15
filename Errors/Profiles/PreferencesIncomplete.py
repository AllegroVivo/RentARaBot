from __future__ import annotations

from typing import List, TYPE_CHECKING

from Errors._Error import ErrorMessage

if TYPE_CHECKING:
    from Classes import Profile
################################################################################

__all__ = ("PreferencesIncomplete",)

################################################################################
class PreferencesIncomplete(ErrorMessage):

    def __init__(self, profile: Profile):
        
        final_requirements = []
        prefs = profile.preferences
        
        if not prefs.activities:
            final_requirements.append("Activities")
        if not prefs.music_prefs:
            final_requirements.append("Music Preferences")
        if not prefs.zodiac_self or not prefs.zodiac_partners:
            final_requirements.append("Zodiac Signs")
        
        addl_str = ""
        if not (
            prefs.male_prefs.is_complete or
            prefs.female_prefs.is_complete or
            prefs.nb_prefs.is_complete
        ):
            addl_str = (
                "**Additionally, you must fill out a minimum of one Gender/Racial "
                "Preference section.**"
            )
        
        requirement_string = "\n".join([f"- {r}" for r in final_requirements])
        super().__init__(
            title="Preferences Incomplete",
            message="Your profile preferences section is incomplete and cannot be matched.",
            solution=(
                "Please ensure that all of the following required fields are "
                "filled out and try again:\n"
                f"{requirement_string}\n"
                f"{addl_str}"
            )
        )

################################################################################
