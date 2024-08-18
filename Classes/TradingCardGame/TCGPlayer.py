from __future__ import annotations

from uuid import uuid4

from typing import TYPE_CHECKING, Type, TypeVar, Any, Dict, Optional

from discord import User

if TYPE_CHECKING:
    from Classes import BattleManager, CardCollection, CardDeck
################################################################################

__all__ = ("TCGPlayer", )

P = TypeVar("P", bound="TCGPlayer")

################################################################################
class TCGPlayer:

    __slots__ = (
        "_id",
        "_mgr",
        "_user",
        "_stats",
        "_current_deck",
    )
    
################################################################################
    def __init__(self, mgr: BattleManager, _id: str, user: User, **kwargs) -> None:

        self._id: str = _id
        self._mgr: BattleManager = mgr
        
        self._user: User = user
        self._stats: Dict[str, Any] = kwargs
        
        self._current_deck: Optional[CardDeck] = None
    
################################################################################
    @classmethod
    def new(cls: Type[P], mgr: BattleManager, user: User) -> P:
        
        # new_id = mgr.bot.database.insert.tcg_player(mgr.guild_id, user.id)
        new_id = str(uuid4())
        return cls(mgr, new_id, user)
    
################################################################################
    @classmethod
    def load(cls: Type[P], mgr: BattleManager, data: Dict[str, Any]) -> P:
        
        pass
    
################################################################################
    @property
    def user(self) -> User:
        
        return self._user
    
################################################################################
    @property
    def collection(self) -> CardCollection:
        
        # Eww, gross, don't look at this.
        return self._mgr._mgr._collections[self.user.id]
    
################################################################################
    @property
    def current_deck(self) -> Optional[CardDeck]:
        
        return self._current_deck
    
    @current_deck.setter
    def current_deck(self, deck: CardDeck) -> None:
        
        self._current_deck = deck
        
################################################################################
