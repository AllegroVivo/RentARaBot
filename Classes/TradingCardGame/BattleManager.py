from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Classes import TCGManager
################################################################################

__all__ = ("BattleManager", )

################################################################################
class BattleManager:

    __slots__ = (
        "_mgr",
        "_battles",
    )
    
################################################################################
    def __init__(self, mgr: TCGManager) -> None:

        self._mgr: TCGManager = mgr
        self._battles: dict[int, Battle] = {}
    
################################################################################
