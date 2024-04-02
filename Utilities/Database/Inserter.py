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

    pass
    
################################################################################

################################################################################
    