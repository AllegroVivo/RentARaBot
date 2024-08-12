from Errors._Error import ErrorMessage
################################################################################

__all__ = ("ProfileRoleNotOwned",)

################################################################################
class ProfileRoleNotOwned(ErrorMessage):

    def __init__(self):

        super().__init__(
            title="Profile Role Not Owned",
            message="You don't own at least one of the roles required to use this command.",
            solution=(
                "Please contact a server administrator to have them assign "
                "you the appropriate role(s)."
            )
        )

################################################################################
