from Errors._Error import ErrorMessage
################################################################################

__all__ = ("InvalidCardName",)

################################################################################
class InvalidCardName(ErrorMessage):

    def __init__(self, invalid_name: str):
        super().__init__(
            title="Invalid Card Name",
            description=f"**Invalid Value:** `{invalid_name}`",
            message="The card name you provided is invalid.",
            solution="Please check your spelling and try again."
        )

################################################################################
