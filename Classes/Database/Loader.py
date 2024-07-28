from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Tuple

from .Branch import DBWorkerBranch

if TYPE_CHECKING:
    pass
################################################################################

__all__ = ("DatabaseLoader",)

################################################################################
class DatabaseLoader(DBWorkerBranch):
    """A utility class for loading data from the database."""

    def load_all(self) -> Dict[int, Dict[str, Any]]:
        """Performs all sub-loaders and returns a dictionary of their results."""

        print("Database", "Performing database load_all.")

        return self._parse_all(self._get_payload())

################################################################################
    def _load_data_from_table(self, table_name: str) -> Tuple[Tuple[Any, ...]]:
        """Load data from a specific table."""

        self.execute(f"SELECT * FROM {table_name};")
        return self.fetchall()
    
################################################################################
    def _get_payload(self) -> Dict[str, Any]:

        table_list = [
            "form_options",
            "form_questions",
            "form_response_collections",
            "forms",
            "form_responses",
        ]

        ret = {}
        for table in table_list:
            ret[table] = self._load_data_from_table(table)
            
        return ret
        
################################################################################
    def _parse_all(self, payload: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
        
        ret = {
            g.id: {
                "forms": [],
            }
            for g in self.bot.guilds
        }
        
        # Forms
        for form in payload["forms"]:
            ret[form[1]]["forms"].append({
                "form": form,
                "questions": [],
                "responses": [
                    response 
                    for response in payload["form_response_collections"]
                    if response[1] == form[0]
                ],
            })
            for question in payload["form_questions"]:
                if question[1] == form[0]:
                    ret[form[1]]["forms"][-1]["questions"].append({
                        "question": question,
                        "options": [
                            option
                            for option in payload["form_options"]
                            if option[1] == question[0]
                        ],
                        "responses": [
                            response
                            for response in payload["form_responses"]
                            if response[0] == question[0]
                        ]
                    })
            
        return ret
    
################################################################################
