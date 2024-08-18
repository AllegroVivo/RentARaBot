from Errors._Error import ErrorMessage
################################################################################

__all__ = ("InvalidUserChallenge",)

################################################################################
class InvalidUserChallenge(ErrorMessage):

    def __init__(self):
        super().__init__(
            title="Invalid User Challenge",
            message="The challenge you are trying to issue is invalid.",
            solution="Please ensure that the user you are trying to challenge does not have any active challenges or battles.",
        )

################################################################################
