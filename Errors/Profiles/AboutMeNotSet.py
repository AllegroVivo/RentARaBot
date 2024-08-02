from Errors._Error import ErrorMessage
################################################################################

__all__ = ("AboutMeNotSet",)

################################################################################
class AboutMeNotSet(ErrorMessage):

    def __init__(self):

        super().__init__(
            title="About Me Not Set",
            message="You can't view an empty About Me section.",
            solution=(
                "Use the `/profile personality` command to set it before "
                "trying again."
            )
        )

################################################################################
