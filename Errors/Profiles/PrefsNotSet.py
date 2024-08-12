from Errors._Error import ErrorMessage
################################################################################

__all__ = ("PrefsNotSet",)

################################################################################
class PrefsNotSet(ErrorMessage):

    def __init__(self):

        super().__init__(
            title="Preferences Me Not Set",
            message="You can't view an empty Preferences/Activities section.",
            solution=(
                "Use the `Personality/Preferences` button to set it them "
                "trying again."
            )
        )

################################################################################
