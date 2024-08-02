from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any, List

if TYPE_CHECKING:
    from Classes import ProfileSection
################################################################################

__all__ = ("ProfileItem", )

################################################################################
class ProfileItem:

    __slots__ = (
        "_parent",
        "_response",
        "_types",
        "_required",
    )
    
################################################################################
    def __init__(self, parent: ProfileSection, **kwargs) -> None:

        self._parent: ProfileSection = parent
        
        self._types: List[type] = kwargs.pop("types")
        self._required: bool = kwargs.get("required", False)
        
        self._response: Optional[Any] = kwargs.get("value")
    
################################################################################
