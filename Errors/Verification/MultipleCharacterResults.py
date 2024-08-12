from Errors._Error import ErrorMessage
################################################################################
__all__ = ("MultipleCharacterResults",)
################################################################################
class MultipleCharacterResults(ErrorMessage):

    def __init__(self, forename: str, surname: str, world: str) -> None:

        super().__init__(
            title="Multiple Character Results Found",
            message=(
                f"Multiple character results were found for the name '{forename} {surname}' "
                f"on the world '{world}'."
            ),
            solution=(
                "Please refine your search criteria to find the specific "
                "character you are looking for."
            )
        )

################################################################################
