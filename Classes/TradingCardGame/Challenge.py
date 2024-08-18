from __future__ import annotations

from uuid import uuid4
from datetime import datetime, UTC
from typing import TYPE_CHECKING, Type, TypeVar, Optional

from discord import User, Interaction, TextChannel, Thread, ChannelType, Forbidden

from Errors import InsufficientPermissions, NoDecksConfigured, NoOpponentDecksConfigured
from UI.Common import FroggeSelectView
from UI.TradingCardGame import ChallengeAcceptView
from .TCGPlayer import TCGPlayer
from Utilities import Utilities as U, FroggeColor

if TYPE_CHECKING:
    from Classes import BattleManager, CardDeck
################################################################################

__all__ = ("Challenge", )

C = TypeVar("C", bound="Challenge")

################################################################################
class Challenge:

    __slots__ = (
        "_id",
        "_mgr",
        "_player",
        "_opponent",
        "_dt",
        "_thread",
    )
    
################################################################################
    def __init__(self, mgr: BattleManager, player: TCGPlayer, opponent: TCGPlayer) -> None:

        self._id: str = str(uuid4())
        self._mgr: BattleManager = mgr
        
        self._player: TCGPlayer = player
        self._opponent: TCGPlayer = opponent
        self._dt: datetime = datetime.now(UTC)
        
        self._thread: Optional[Thread] = None
    
################################################################################
    def __eq__(self, other: Challenge) -> bool:
        
        return self._id == other._id
    
################################################################################
    @property
    def player(self) -> TCGPlayer:
        
        return self._player
    
################################################################################
    @property
    def opponent(self) -> TCGPlayer:
        
        return self._opponent
    
################################################################################
    @property
    def create_dt(self) -> datetime:
        
        return self._dt
    
################################################################################
    @property
    def thread(self) -> Optional[Thread]:
        
        return self._thread
    
################################################################################
    async def issue(self, interaction: Interaction) -> None:
        
        player_deck_options = [
            deck.select_option()
            for deck in self.player.collection.deck_manager.decks 
            if deck.is_full
        ]
        opponent_deck_options = [
            deck.select_option()
            for deck in self.opponent.collection.deck_manager.decks
            if deck.is_full
        ]
        
        error = None
        if not player_deck_options:
            error = NoDecksConfigured()
        elif not opponent_deck_options:
            error = NoOpponentDecksConfigured()
        if error:
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        prompt = U.make_embed(
            title="__Select Your Deck__",
            description=(
                f"As issuer of the challenge, you must be the first to select a "
                f"deck to use in the duel.\n\n"
                
                f"**The challenge will not be issued until you have selected a deck.**"
            )
        )
        view = FroggeSelectView(interaction.user, player_deck_options)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.player.current_deck = self.player.collection.deck_manager[view.value]

        try:
            self._thread = await interaction.channel.create_thread(
                name=f"{self.player.user.display_name} vs {self.opponent.user.display_name}",
                auto_archive_duration=60,
                type=ChannelType.public_thread,
            )
        except Forbidden:
            error = InsufficientPermissions(interaction.channel, "Create Threads")
            await interaction.respond(embed=error, ephemeral=True)
            return
        else:
            starter_msg = U.make_embed(
                title="__Duel Start__",
                description=(
                    f"Welcome to the duel between `{self.player.user.display_name}` and "
                    f"`{self.opponent.user.display_name}`!\n"
                    "The duel will begin shortly."
                ),
                color=FroggeColor.blue()
            )
            view = ChallengeAcceptView(self.opponent.user, self)
            mention_str = f"{self.player.user.mention} {self.opponent.user.mention}"
            await self._thread.send(content=mention_str, embed=starter_msg, view=view)

        prompt = U.make_embed(
            title="__Challenge Issued__",
            description=(
                f"`{self.player.user.display_name}` has challenged you to a duel!\n\n"

                f"[Click Here to Accept]({self._thread.jump_url})\n"
            ),
            color=FroggeColor.yellow()
        )
        try:
            await self.opponent.user.send(embed=prompt)
        except Forbidden:
            fallback = U.make_embed(
                title="__Challenge Issued__",
                description=(
                    f"`{self.player.user.display_name}` has challenged you to a duel!"
                ),
                color=FroggeColor.yellow()
            )
            await self._thread.send(content=self.opponent.user.mention, embed=fallback)
            
        await view.wait()

################################################################################
    async def accept(self, interaction: Interaction) -> None:

        opponent_deck_options = [
            deck.select_option()
            for deck in self.opponent.collection.deck_manager.decks
            if deck.is_full
        ]
        prompt = U.make_embed(
            title="__Select Your Deck__",
            description=(
                f"As the challenged party, you must select a deck to use in the duel.\n\n"
                
                f"**The challenge will not be accepted until you have selected a deck.**"
            )
        )
        view = FroggeSelectView(interaction.user, opponent_deck_options)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.opponent.current_deck = self.opponent.collection.deck_manager[view.value]
        await self.transition_to_battle()
    
################################################################################
    async def transition_to_battle(self) -> None:
        
        await self._mgr.start_battle(self)
        
################################################################################
