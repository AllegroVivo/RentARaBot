from __future__ import annotations

from typing import TYPE_CHECKING, List

from discord import Interaction, User

from Errors import InvalidUserChallenge
from .CardBattle import CardBattle
from .Challenge import Challenge
from .TCGPlayer import TCGPlayer

if TYPE_CHECKING:
    from Classes import TCGManager, RentARaBot
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
    @property
    def bot(self) -> RentARaBot:
        
        return self._mgr.bot
    
################################################################################
    @property
    def guild_id(self) -> int:
        
        return self._mgr.guild_id
    
################################################################################
    @property
    def challenges(self) -> List[Challenge]:
        
        return self._challenges
    
################################################################################
    async def challenge_user(self, interaction: Interaction, user: User) -> None:
        
        error = None
        # if interaction.user == user:
        #     error = InvalidUserChallenge()
        if _ := self.get_challenge(interaction.user):
            error = InvalidUserChallenge()
        elif _ := self.get_challenge(user):
            error = InvalidUserChallenge()
        if error:
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        player = self.get_player(interaction.user)
        opponent = self.get_player(user)
        
        new_challenge = Challenge(self, player, opponent)
        self._challenges.append(new_challenge)
        
        await new_challenge.issue(interaction)
    
################################################################################
    def get_challenge(self, user: User) -> Challenge:
        
        for challenge in self._challenges:
            if challenge.player.user == user or challenge.opponent.user == user:
                return challenge
    
################################################################################
    def get_player(self, user: User) -> TCGPlayer:
        
        for player in self._players:
            if player.user == user:
                return player
            
        player = TCGPlayer.new(self, user)
        self._players.append(player)
        
        return player
            
################################################################################
    async def start_battle(self, challenge: Challenge) -> None:
        
        battle = CardBattle(self, challenge)
        self._battles.append(battle)
        
        await battle.start()
        
################################################################################
