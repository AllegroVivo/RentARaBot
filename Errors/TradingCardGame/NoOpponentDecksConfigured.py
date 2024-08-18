from Errors._Error import ErrorMessage
################################################################################

__all__ = ("NoOpponentDecksConfigured",)

################################################################################
class NoOpponentDecksConfigured(ErrorMessage):

    def __init__(self):
        super().__init__(
            title="No Decks Available",
            message="Your selected opponent does not have any available decks to play with.",
            solution="Please ask your opponent to create a deck before challenging them."
        )

################################################################################
