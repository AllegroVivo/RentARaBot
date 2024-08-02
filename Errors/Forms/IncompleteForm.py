from __future__ import annotations

from typing import List

from Errors._Error import ErrorMessage
################################################################################

__all__ = ("IncompleteForm",)

################################################################################
class IncompleteForm(ErrorMessage):

    def __init__(self, questions: List[int]) -> None:

        super().__init__(
            title="Form Incomplete",
            description=(
                "__Required Questions:__\n"
                + ", ".join(f"#{q}" for q in questions)
            ),
            message="One or more required questions have not been answered.",
            solution="Please answer all required questions before submitting your form."
        )

################################################################################
