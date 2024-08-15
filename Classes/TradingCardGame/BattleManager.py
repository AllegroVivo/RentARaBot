from __future__ import annotations

from typing import TYPE_CHECKING, List

from .CardBattle import CardBattle
from .Challenge import Challenge
from .TCGPlayer import TCGPlayer

if TYPE_CHECKING:
    from Classes import TCGManager
################################################################################

__all__ = ("BattleManager", )

################################################################################
class BattleManager:

    __slots__ = (
        "_mgr",
        "_battles",
        "_challenges",
        "_players",
    )
    
################################################################################
    def __init__(self, mgr: TCGManager) -> None:

        self._mgr: TCGManager = mgr
        
        self._battles: List[CardBattle] = []
        self._challenges: List[Challenge] = []
        self._players: List[TCGPlayer] = []
    
################################################################################
