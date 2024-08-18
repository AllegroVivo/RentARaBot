from Errors._Error import ErrorMessage
################################################################################

__all__ = ("ImgurError",)

################################################################################
class ImgurError(ErrorMessage):

    def __init__(self):

        super().__init__(
            title="An Error Occurred",
            message="An error occurred while trying to upload the image to Imgur.",
            solution=(
                "Please try again later. If the problem persists, please "
                "contact the application administrator."
            )
        )

################################################################################
