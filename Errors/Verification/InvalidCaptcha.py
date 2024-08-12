from Errors._Error import ErrorMessage
################################################################################
__all__ = ("InvalidCaptcha",)
################################################################################
class InvalidCaptcha(ErrorMessage):

    def __init__(self) -> None:

        super().__init__(
            title="Invalid Captcha Entry",
            message="The captcha entry you selected was invalid. Please try again.",
            solution="Please try again. If you continue to have issues, please contact a staff member."
        )

################################################################################
