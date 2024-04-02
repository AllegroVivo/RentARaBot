from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .Branch import DBWorkerBranch

if TYPE_CHECKING:
    from Classes import *
################################################################################

__all__ = ("DatabaseInserter",)

################################################################################
class DatabaseInserter(DBWorkerBranch):
    """A utility class for inserting new records into the database."""

    def _insert_dating_request(self, requestor_id: int, guild_id: int) -> str:
        
        new_id = self.generate_id()
        
        self.execute(
            "INSERT INTO dating_requests (_id, requestor_id, guild_id) "
            "VALUES (%s, %s, %s);",
            new_id, requestor_id, guild_id
        )
        
        return new_id
    
################################################################################

    dating_request = _insert_dating_request
    
################################################################################
    