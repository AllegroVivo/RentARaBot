from Errors._Error import ErrorMessage
################################################################################

__all__ = ("CardNotInCollection",)

################################################################################
class CardNotInCollection(ErrorMessage):

    def __init__(self, invalid_card: str):
        super().__init__(
            title="Card Not In Collection",
            description=f"**Invalid Card:** `{invalid_card}`",
            message="The card name you selected could not be found in your collection.",
            solution="Please select a card you own."
        )

################################################################################
