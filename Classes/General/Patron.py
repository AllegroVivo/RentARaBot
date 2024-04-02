from __future__ import annotations

from typing import TYPE_CHECKING
from discord import User

if TYPE_CHECKING:
    pass
################################################################################

__all__ = ("Patron",)

################################################################################
class Patron:
    
    __slots__ = (
        "_user",
    )
    
################################################################################
    def __init__(self, user: User):
        
        self._user: User = user
        
################################################################################
    @classmethod
    def new(cls, user: User) -> Patron:
        
        return cls(user)
    
################################################################################
    @property
    def user(self) -> User:
        
        return self._user
    
################################################################################
