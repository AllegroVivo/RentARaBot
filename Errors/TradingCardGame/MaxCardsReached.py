from Errors._Error import ErrorMessage
################################################################################

__all__ = ("MaxCardsReached",)

################################################################################
class MaxCardsReached(ErrorMessage):

    def __init__(self, max_cards: int):
        super().__init__(
            title="Series Card Maximum Reached",
            message=(
                f"You already have the maximum of `{max_cards}` cards in "
                f"the current series."
            ),
            solution=(
                "You must remove a card from the series before adding "
                "another. Or add to a different series."
            )
        )

################################################################################
