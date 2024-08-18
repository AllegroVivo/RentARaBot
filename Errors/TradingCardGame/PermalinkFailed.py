from Errors._Error import ErrorMessage
################################################################################

__all__ = ("PermalinkFailed",)

################################################################################
class PermalinkFailed(ErrorMessage):

    def __init__(self, card_name: str):
        super().__init__(
            title="Permalink Failed",
            description="**`DON'T WORRY, YOU DIDN'T DO ANYTHING WRONG~!`**",
            message=(
                f"The permalink reference for `{card_name}`'s image could not "
                "properly be fetched or decoded.\n\n"
                
                "This could be due to a number of reasons, such as the remote image "
                "being deleted, the URL being invalid, or the data being corrupted.\n\n"
                
                "It has been set to `NULL`."
            ),
            solution=(
                "**Please contact a server admin and provide a screenshot "
                "of this error to report this issue.**\n\n"
                
                "If you are a server admin, please edit the card's "
                "configuration to provide a new Direct URL permalink to "
                "the card's image asset."
            ),
        )

################################################################################
