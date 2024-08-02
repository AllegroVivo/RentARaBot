from Errors._Error import ErrorMessage
from Utilities.Constants import *
################################################################################

__all__ = ("TooManyImages",)

################################################################################
class TooManyImages(ErrorMessage):

    def __init__(self):
        super().__init__(
            title="Image Maximum Reached",
            message=(
                f"You already have the maximum of `{MAX_ADDITIONAL_IMAGES}` "
                f"additional images on your profile."
            ),
            solution="Sorry, I can't add any more because of formatting restrictions. :("
        )

################################################################################
