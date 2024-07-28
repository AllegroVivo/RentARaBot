from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Any

from .Branch import DBWorkerBranch

if TYPE_CHECKING:
    from Classes import *
################################################################################

__all__ = ("DatabaseInserter",)

################################################################################
class DatabaseInserter(DBWorkerBranch):
    """A utility class for inserting new records into the database."""

    def _insert(self, table: str, columns: List[str], values: List[Any]) -> str:

        placeholders = ", ".join(["%s"] * len(values))
        columns_str = ", ".join(columns)
    
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) RETURNING _id;"
        self.execute(query, *values)
    
        return self.fetchone()[0]

################################################################################
    def _insert_no_return(self, table: str, columns: List[str], values: List[Any]) -> None:
    
        placeholders = ", ".join(["%s"] * len(values))
        columns_str = ", ".join(columns)
    
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING;"
        self.execute(query, *values)
    
################################################################################
    def _insert_guild(self, guild_id: int) -> None:
        
        pass
        
################################################################################
    def _insert_form(self, guild_id: int, name: str) -> str:
        
        return self._insert(
            "forms", 
            ["_id", "guild_id", "form_name"], 
            [self.generate_id(), guild_id, name]
        )
    
################################################################################
    def _insert_form_option(self, question_id: str) -> str:
        
        return self._insert(
            "form_options",
            ["_id", "question_id"],
            [self.generate_id(), question_id]
        )
        
################################################################################
    def _insert_form_question(self, form_id: str, order: int, primary_text: str) -> str:
        
        return self._insert(
            "form_questions",
            ["_id", "form_id", "sort_order", "primary_text"],
            [self.generate_id(), form_id, order, primary_text]
        )
    
################################################################################
    def _insert_form_response_collection(
        self, 
        form_id: str,
        user_id: int,
        questions: List[str],
        responses: List[str]
    ) -> str:
        
        return self._insert(
            "form_response_collections",
            ["_id", "form_id", "user_id", "questions", "responses"],
            [self.generate_id(), form_id, user_id, questions, responses]
        )
    
################################################################################
    def _insert_form_response(self, question_id: str, user_id: int, responses: List[str]) -> None:
        
        self._insert_no_return(
            "form_responses",
            ["question_id", "user_id", "values"],
            [question_id, user_id, responses]
        )
        
################################################################################

    guild               = _insert_guild
    form                = _insert_form
    form_option         = _insert_form_option
    form_question       = _insert_form_question
    form_response_coll  = _insert_form_response_collection
    form_response       = _insert_form_response
    
################################################################################
    