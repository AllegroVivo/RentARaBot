from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    pass
################################################################################

__all__ = ("Identifiable", )

I = TypeVar("I", bound="Identifiable")

################################################################################
class Identifiable:

    __slots__ = (
        "_id",
    )
    
################################################################################
    def __init__(self, _id: str) -> None:

        self._id: str = _id

################################################################################
    def __hash__(self) -> int:
        
        return hash(self.id)

################################################################################
    def __eq__(self, other: Identifiable) -> bool:
        
        return self.id == other.id
    
################################################################################
    @property
    def id(self) -> str:
        
        return self._id
    
################################################################################
    