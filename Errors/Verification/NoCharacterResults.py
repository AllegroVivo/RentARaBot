from Errors._Error import ErrorMessage
################################################################################
__all__ = ("NoCharacterResults",)
################################################################################
class NoCharacterResults(ErrorMessage):

    def __init__(self, forename: str, surname: str, world: str) -> None:

        super().__init__(
            title="No Character Results Found",
            message=(
                f"No character results were found for the name '{forename} {surname}' "
                f"on the world '{world}'."
            ),
            solution=(
                "Please ensure the name and world are spelled correctly and "
                "try again."
            )
        )

################################################################################
