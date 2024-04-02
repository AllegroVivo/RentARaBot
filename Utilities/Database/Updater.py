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

    pass
    
################################################################################
    
################################################################################
    