from __future__ import annotations

from typing import TYPE_CHECKING

from .Branch import DBWorkerBranch

if TYPE_CHECKING:
    from Classes import *
################################################################################

__all__ = ("DatabaseDeleter",)

################################################################################
class DatabaseDeleter(DBWorkerBranch):
    """A utility class for deleting data from the database."""
    
    def _delete_form(self, form: Form) -> None:
        
        self.execute(
            "DELETE FROM forms WHERE _id = %s;",
            form.id
        )
        self.execute(
            "DELETE FROM form_questions WHERE form_id = %s;",
            form.id
        )
        for question in form.questions:
            question.delete()
        
################################################################################
    def _delete_form_option(self, option: FormOption) -> None:
        
        self.execute(
            "DELETE FROM form_options WHERE _id = %s;",
            option.id
        )
        
################################################################################
    def _delete_form_question(self, question: FormQuestion) -> None:
        
        self.execute(
            "DELETE FROM form_questions WHERE _id = %s;",
            question.id
        )
        self.execute(
            "DELETE FROM form_options WHERE question_id = %s;",
            question.id
        )
        
################################################################################
    def _delete_form_response(self, question_id: str, user_id: int) -> None:
        
        self.execute(
            "DELETE FROM form_responses WHERE question_id = %s AND user_id = %s;",
            question_id, user_id
        )
        
################################################################################

    form_option         = _delete_form_option
    form_question       = _delete_form_question
    form                = _delete_form
    form_response       = _delete_form_response
    
################################################################################
