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

    def _update_dating_request(self, request: DatingRequest) -> None:
        
        self.execute(
            "UPDATE dating_requests SET sfw = %s, escort = %s, dt = %s, "
            "selection = %s, length = %s, sfw_plan = %s, location = %s "
            "WHERE _id = %s",
            request.sfw, request.escort, request.desired_time, request.selection,
            request.length, request.sfw_plan, request.location, request.id
            
        )
    
################################################################################
    
    dating_request      = _update_dating_request
    
################################################################################
    