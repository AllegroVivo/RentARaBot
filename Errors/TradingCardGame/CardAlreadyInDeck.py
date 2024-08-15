from Errors._Error import ErrorMessage
################################################################################

__all__ = ("CardAlreadyInDeck",)

################################################################################
class CardAlreadyInDeck(ErrorMessage):

    def __init__(self, existing_card: str):
        super().__init__(
            title="Card Already In Deck",
            description=f"**Card:** `{existing_card}`",
            message="The card you selected is already in this deck.",
            solution="Please select a different card or modify the existing card."
        )

################################################################################
