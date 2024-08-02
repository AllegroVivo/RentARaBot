from Errors._Error import ErrorMessage
################################################################################

__all__ = ("ExceedsMaxLength",)

################################################################################
class ExceedsMaxLength(ErrorMessage):

    def __init__(self, embed_length: int, max_length: int):
        super().__init__(
            title="Profile Too Large!",
            description=f"Current Character Count: `{embed_length:,}`.",
            message=(
                f"Your profile is larger than Discord's mandatory {max_length:,}"
                f"-character limit for embedded messages."
            ),
            solution=(
                "The total number of characters in all your profile's sections "
                f"must not exceed {max_length:,}."
            )
        )

################################################################################
