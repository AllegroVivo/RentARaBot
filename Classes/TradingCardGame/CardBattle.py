from __future__ import annotations

import random

from datetime import datetime, UTC
from typing import TYPE_CHECKING, List
from uuid import uuid4

from discord import Thread

from UI.Common import FroggeSelectView

if TYPE_CHECKING:
    from Classes import BattleManager, Challenge, TCGPlayer, CardDeck
################################################################################

__all__ = ("CardBattle", )

################################################################################
class CardBattle:

    __slots__ = (
        "_id",
        "_mgr",
        "_p1",
        "_p2",
        "_thread",
        "_last_ts",
    )
    
################################################################################
    def __init__(self, mgr: BattleManager, challenge: Challenge) -> None:

        self._id: str = str(uuid4())
        self._mgr: BattleManager = mgr

        self._p1: TCGPlayer = challenge.player
        self._p2: TCGPlayer = challenge.opponent

        assert self._p1.current_deck is not None, "Player 1 has no deck"
        assert self._p2.current_deck is not None, "Player 2 has no deck"
        assert challenge.thread is not None, "Challenge thread is None"
        
        self._thread: Thread = challenge.thread
        self._last_ts: datetime = datetime.now(UTC)
        
        # We can delete the challenge now
        self._mgr.challenges.remove(challenge)
    
################################################################################
    @property
    def channel(self) -> Thread:
        
        return self._thread
    
################################################################################
    @property
    def p1_deck(self) -> CardDeck:
        
        return self._p1.current_deck
    
    @property
    def p2_deck(self) -> CardDeck:
        
        return self._p2.current_deck
    
################################################################################
    async def start(self) -> None:
        
        await self.channel.send("Battle started!")
        await self.channel.send("First Round Rolling...")
        
        card_select_roll = random.randint(1, 6)
        await self.channel.send(f"Card Selection: `{card_select_roll}`")
            
        p1_matching_cards = self.p1_deck.get_die_marker_matching(card_select_roll)
        addl = 1
        while not p1_matching_cards:
            await self.channel.send(
                f"Player 1 has no matching cards. Falling back to an "
                f"additional span of +/-{addl}."
            )
            p1_matching_cards.extend(self.p1_deck.get_die_marker_matching(card_select_roll - addl))
            p1_matching_cards.extend(self.p1_deck.get_die_marker_matching(card_select_roll + addl))
            addl += 1
            
        p2_matching_cards = self.p2_deck.get_die_marker_matching(card_select_roll)
        addl = 1
        while not p2_matching_cards:
            await self.channel.send(
                f"Player 2 has no matching cards. Falling back to an "
                f"additional span of +/-{addl}."
            )
            p2_matching_cards.extend(self.p2_deck.get_die_marker_matching(card_select_roll - addl))
            p2_matching_cards.extend(self.p2_deck.get_die_marker_matching(card_select_roll + addl))
            addl += 1
            
        msg = (
            f"Player 1 has {len(p1_matching_cards)} matching cards: "
            f"{', '.join([c.card.name for c in p1_matching_cards])}\n\n"

            "Please select a card to play."
        )
        view = FroggeSelectView(self._p1.user, [c.card.select_option() for c in p1_matching_cards])
        
        await self.channel.send(content=msg, view=view)
        await view.wait()
        
        p1_selected_card = self.p1_deck.get_card_by_id(view.value)
        
        msg = (
            f"Player 2 has {len(p2_matching_cards)} matching cards: "
            f"{', '.join([c.card.name for c in p2_matching_cards])}\n\n"

            "Please select a card to play."
        )
        view = FroggeSelectView(self._p2.user, [c.card.select_option() for c in p2_matching_cards])
        
        await self.channel.send(content=msg, view=view)
        await view.wait()
        
        p2_selected_card = self.p2_deck.get_card_by_id(view.value)
        
        await self.channel.send(
            f"Player 1 played `{p1_selected_card.name}`\n"
            f"Player 2 played `{p2_selected_card.name}`"
        )

        await self.channel.send("Each round is now a best of three `/random 999` rolls!")
        await self.channel.send("Starting with the `SFW` stat!")

        rand = self.random999()
        await self.channel.send(f"Random Roll: `{rand}`")
        
        await self.channel.send("Comparing `BAD` stats!")
        if p1_selected_card.compare_bad(rand):
            await self.channel.send("Player 1 `BAD` stat MATCHED! They Lose!")
        elif p2_selected_card.compare_bad(rand):
            await self.channel.send("Player 2 `BAD` stat MATCHED! They Lose!")
        else:
            await self.channel.send("No `BAD` stat match!")
        
################################################################################
    @staticmethod
    def random999() -> int:

        return random.randint(0, 999)

################################################################################
