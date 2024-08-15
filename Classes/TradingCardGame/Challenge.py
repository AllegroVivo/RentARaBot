from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from discord import User

if TYPE_CHECKING:
    from Classes import BattleManager
################################################################################

__all__ = ("Challenge", )

################################################################################
class Challenge:

    __slots__ = (
        "_mgr",
        "_player",
        "_opponent",
        "_dt",
    )
    
################################################################################
    def __init__(self, mgr: BattleManager, player: User, opponent: User) -> None:

        self._mgr: BattleManager = mgr
        
        self._player: User = player
        self._opponent: User = opponent
        self._dt: datetime = datetime.now()
    
################################################################################
