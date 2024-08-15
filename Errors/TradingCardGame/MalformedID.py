from Errors._Error import ErrorMessage
################################################################################

__all__ = ("MalformedID",)

################################################################################
class MalformedID(ErrorMessage):

    def __init__(self, invalid_id: str):
        super().__init__(
            title="Malformed ID",
            description=f"**Invalid Value:** `{invalid_id}`",
            message=(
                "The value provided is not a valid ID. "
                "Please ensure the ID is correct and try again"
            ),
            solution=(
                "IDs are typically a string of numeric characters mediated by a hyphen, "
                "in the format of `<Series #>-<Card ID>`.\n\n"
                
                "__**Example:**__ `1-032`"
            )
        )

################################################################################
