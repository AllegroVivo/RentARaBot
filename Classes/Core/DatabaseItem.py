from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type, TypeVar

if TYPE_CHECKING:
    pass
################################################################################

__all__ = ("DatabaseItem", )

T = TypeVar("T")

################################################################################
class DatabaseItem(ABC):

    @classmethod
    @abstractmethod
    def new(cls: Type[T], **kwargs) -> T:
        
        pass
    
################################################################################
    @classmethod
    @abstractmethod
    def load(cls: Type[T], **kwargs) -> T:
        
        pass
    
################################################################################
    @abstractmethod
    def update(self) -> None:
        
        pass
    
################################################################################
    @abstractmethod
    def delete(self) -> None:
        
        pass
    
################################################################################
