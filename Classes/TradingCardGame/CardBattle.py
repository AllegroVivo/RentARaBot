from __future__ import annotations

import random

from datetime import datetime, UTC
from typing import TYPE_CHECKING, List
from uuid import uuid4

from discord import Thread

from UI.Common import FroggeSelectView

if TYPE_CHECKING:
    from Classes import BattleManager, Challenge, TCGPlayer, CardDeck, TradingCard
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
        # self._mgr.challenges.remove(challenge)
    
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

        # Step 1: Roll a die and get matching cards
        card_select_roll = self.random6()
        await self.channel.send(f"Card Selection: `{card_select_roll}`")

        p1_matching_cards = await self.get_matching_cards(self.p1_deck, card_select_roll, "Player 1")
        p2_matching_cards = await self.get_matching_cards(self.p2_deck, card_select_roll, "Player 2")

        # Step 2: Let players select their cards
        p1_selected_card = await self.select_card(self._p1.user, p1_matching_cards, "Player 1", self.p1_deck)
        p2_selected_card = await self.select_card(self._p2.user, p2_matching_cards, "Player 2", self.p2_deck)

        await self.channel.send(
            f"Player 1 played `{p1_selected_card.name}`\n"
            f"Player 2 played `{p2_selected_card.name}`"
        )

        # Step 3: Start the best of three rounds
        await self.channel.send("Each round is now a best of three `/random 999` rolls!")
        await self.channel.send("Starting with the `BATTLE` stat!")

        winner = await self.best_of_three(p1_selected_card, p2_selected_card)

        if winner == "tie":
            await self.channel.send("It's a tie! Replaying the round...")
        else:
            await self.channel.send(f"{winner} wins the round!")

################################################################################
    @staticmethod
    def random999() -> int:

        return random.randint(0, 999)

################################################################################
    @staticmethod
    def random6() -> int:

        return random.randint(1, 6)

################################################################################
    async def get_matching_cards(self, deck, roll, player_name) -> list:

        matching_cards = deck.get_die_marker_matching(roll)
        addl = 1

        while not matching_cards:
            await self.channel.send(
                f"{player_name} has no matching cards. Falling back to an "
                f"additional span of +/-{addl}."
            )
            matching_cards.extend(deck.get_die_marker_matching(roll - addl))
            matching_cards.extend(deck.get_die_marker_matching(roll + addl))
            addl += 1

        return matching_cards

################################################################################
    async def select_card(self, user, matching_cards, player_name, player_deck) -> TradingCard:

        msg = (
            f"{player_name} has {len(matching_cards)} matching cards: "
            f"{', '.join([c.card.name for c in matching_cards])}\n\n"
            "Please select a card to play."
        )
        view = FroggeSelectView(user, [c.card.select_option() for c in matching_cards])

        await self.channel.send(content=msg, view=view)
        await view.wait()

        return player_deck.get_card_by_id(view.value)

################################################################################
    async def best_of_three(self, p1_card, p2_card) -> str:

        round_stats = ["BATTLE", "NSFW", "SFW"]

        p1_wins = 0
        p2_wins = 0

        for stat in round_stats:
            await self.channel.send(f"Comparing `{stat}` stats!")
            while True:
                roll_result = self.random999()
                await self.channel.send(f"Random Roll: `{roll_result}`")

                p1_bad_flag, p2_bad_flag = await self.compare_bad_stats(p1_card, p2_card, roll_result)

                if p1_bad_flag and p2_bad_flag:
                    await self.channel.send("Both players `BAD` stat matched! A tie! Rerolling...")
                elif p1_bad_flag:
                    p2_wins += 1
                    break
                elif p2_bad_flag:
                    p1_wins += 1
                    break
                else:
                    p1_absolute_value = p1_card.get_absolute_value(stat, roll_result)
                    p2_absolute_value = p2_card.get_absolute_value(stat, roll_result)

                    await self.channel.send(
                        f"Player 1 Absolute Distance: `{p1_absolute_value}`\n"
                        f"Player 2 Absolute Distance: `{p2_absolute_value}`"
                    )

                    if p1_absolute_value < p2_absolute_value:
                        p1_wins += 1
                        break
                    elif p2_absolute_value < p1_absolute_value:
                        p2_wins += 1
                        break
                    else:
                        await self.channel.send("Absolute values are equal! Rerolling...")

            if p1_wins == 2 or p2_wins == 2:
                break

        if p1_wins > p2_wins:
            return "Player 1"
        elif p2_wins > p1_wins:
            return "Player 2"
        else:
            return "tie"

################################################################################
    async def compare_bad_stats(self, p1_card, p2_card, roll_result) -> tuple:

        p1_bad_flag = False
        p2_bad_flag = False

        if p1_card.compare_bad(roll_result):
            await self.channel.send("Player 1 `BAD` stat MATCHED! They Lose!")
            p1_bad_flag = True
        if p2_card.compare_bad(roll_result):
            await self.channel.send("Player 2 `BAD` stat MATCHED! They Lose!")
            p2_bad_flag = True

        return p1_bad_flag, p2_bad_flag

################################################################################
