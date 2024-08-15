from Errors._Error import ErrorMessage
################################################################################

__all__ = ("DeckFull",)

################################################################################
class DeckFull(ErrorMessage):

    def __init__(self, max_cards: int):
        super().__init__(
            title="Maximum Cards Reached",
            message=(
                f"This deck is already at the maximum number of cards allowed. "
                f"(`{max_cards}`)"
            ),
            solution=f"Remove a card from the deck to make room for another."
        )

################################################################################
