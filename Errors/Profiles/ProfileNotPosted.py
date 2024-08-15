from Errors._Error import ErrorMessage
################################################################################

__all__ = ("ProfileNotPosted",)

################################################################################
class ProfileNotPosted(ErrorMessage):

    def __init__(self):

        super().__init__(
            title="Profile Not Posted",
            message="You must post your profile before you can use this command.",
            solution=(
                "Use the `/profile` command and click the `Post/Update Profile` "
                "button to post your profile."
            )
        )

################################################################################
