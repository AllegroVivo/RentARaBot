from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .Branch import DBWorkerBranch

if TYPE_CHECKING:
    from Classes import *
################################################################################

__all__ = ("DatabaseUpdater",)

################################################################################
class DatabaseUpdater(DBWorkerBranch):
    """A utility class for updating records in the database."""

    def _update_form_option(self, option: FormOption) -> None:
        
        self.execute(
            "UPDATE form_options SET label = %s, description = %s, value = %s, "
            "emoji = %s WHERE _id = %s",
            option.label, option.description, option.value, 
            str(option.emoji) if option.emoji else None, option.id
        )
        
################################################################################
    def _update_form_question(self, question: FormQuestion) -> None:
        
        self.execute(
            "UPDATE form_questions SET sort_order = %s, primary_text = %s, "
            "secondary_text = %s, ui_type = %s, required = %s WHERE _id = %s",
            question.order, question.primary_text, question.secondary_text, 
            question.ui_type.value, question.required, question.id
        )
    
################################################################################
    def _update_form(self, form: Form) -> None:
        
        self.execute(
            "UPDATE forms SET channel_id = %s, form_name = %s WHERE _id = %s",
            form.channel.id if form.channel else None, form.name, form.id
        )
        
################################################################################
    
    form            = _update_form
    form_option     = _update_form_option
    form_question   = _update_form_question
    
################################################################################
