from Errors._Error import ErrorMessage
################################################################################
__all__ = ("MissingProfile",)
################################################################################
class MissingProfile(ErrorMessage):

    def __init__(self, invalid_id: int) -> None:

        super().__init__(
            title="Character Profile Missing",
            description=f"Invalid Character ID: {invalid_id}",
            message="The character profile you are trying to access does not exist.",
            solution="Please ensure the name and world are correct and try again."
        )

################################################################################
