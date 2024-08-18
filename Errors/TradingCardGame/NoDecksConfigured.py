from Errors._Error import ErrorMessage
################################################################################

__all__ = ("NoDecksConfigured",)

################################################################################
class NoDecksConfigured(ErrorMessage):

    def __init__(self):
        super().__init__(
            title="No Decks Available",
            message="You have no available decks to challenge with. ",
            solution="Please create a deck before challenging another player."
        )

################################################################################
