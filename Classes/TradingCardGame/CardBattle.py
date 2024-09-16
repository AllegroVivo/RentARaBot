from __future__ import annotations

import asyncio
import os
import random
from datetime import datetime, UTC
from io import BytesIO
from typing import TYPE_CHECKING, List, Optional, Tuple
from uuid import uuid4

import requests
from PIL import Image, UnidentifiedImageError
from discord import Thread, File, Interaction

from Assets import BotImages
from Errors import PermalinkFailed
from UI.Common import FroggeSelectView
from UI.TradingCardGame import CardBattleRollView
from Utilities import Utilities as U, FroggeColor

if TYPE_CHECKING:
    from Classes import BattleManager, Challenge, TCGPlayer, CardDeck, TradingCard, DeckCardSlot
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

    P1_COLOR = FroggeColor(0x00FF00)
    P2_COLOR = FroggeColor(0xFF0000)
    SYSTEM_COLOR = FroggeColor(0x0000FF)
    
################################################################################
    def __init__(self, mgr: BattleManager, challenge: Challenge) -> None:

        self._id: str = uuid4().hex
        self._mgr: BattleManager = mgr

        self._p1: TCGPlayer = challenge.player
        self._p2: TCGPlayer = challenge.opponent

        assert self._p1.current_deck is not None, "Player 1 has no deck"
        assert self._p2.current_deck is not None, "Player 2 has no deck"
        assert challenge.thread is not None, "Challenge thread is None"
        
        self._thread: Thread = challenge.thread
        self._last_ts: datetime = datetime.now(UTC)
        
        # We can delete the challenge now
        try:
            self._mgr.challenges.remove(challenge)
        except ValueError:
            pass
    
################################################################################
    def __eq__(self, other: CardBattle) -> bool:

        return self._id == other._id

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
    @staticmethod
    async def wait_for(seconds: int) -> None:

        await asyncio.sleep(seconds)

################################################################################
    async def start(self) -> None:

        win_counts = {"Player 1": 0, "Player 2": 0}
        round_idx = 1

        prompt = U.make_embed(
            color=self.SYSTEM_COLOR,
            title="__Trading Card Battle__",
            description=(
                f"**Player 1:** {self._p1.user.mention}\n"
                f"**Player 2:** {self._p2.user.mention}\n\n"
                
                "The battle will be a best of 3 rounds. Each round, players "
                "will roll a 6-sided die to determine the card they can play. "
                "The card with the best stats wins the round. The first "
                "player to win 3 rounds wins the battle!\n\n"
                
                "The battle will begin shortly..."
            )
        )
        await self.channel.send(embed=prompt)
        await self.wait_for(3)

        while max(win_counts.values()) < 3:
            round_name, image = self.get_round_info(round_idx)
            await self.channel.send(embed=U.make_embed(color=self.SYSTEM_COLOR, image_url=image))
            await self.wait_for(3)

            while True:
                roller = self._p1 if round_idx % 2 == 1 else self._p2
                roll = await self.random_roll(1, 6, roller)
                if not roll:
                    return

                await self.channel.send(embed=U.make_embed(
                    image_url=self._select_die_image(roll),
                    color=self.SYSTEM_COLOR
                ))
                await self.wait_for(2)
    
                p1_matching_cards = await self.get_matching_cards(self.p1_deck, roll, self._p1.user.display_name)
                p2_matching_cards = await self.get_matching_cards(self.p2_deck, roll, self._p2.user.display_name)
    
                p1_selected_card = await self.select_card(self._p1.user, p1_matching_cards, self.p1_deck)
                if p1_selected_card is None:
                    return
                
                p2_selected_card = await self.select_card(self._p2.user, p2_matching_cards, self.p2_deck)
                if p2_selected_card is None:
                    return

                if p1_selected_card != p2_selected_card:
                    break
                    
                prompt = U.make_embed(
                    color=self.SYSTEM_COLOR,
                    title="__Same Cards Selected__",
                    description=(
                        "You've both selected the same card as your opponent.\n\n"
                
                        "**Please roll again and select different cards.**"
                    )
                )
                await self.channel.send(embed=prompt)
                await self.wait_for(2)
                
            versus_url = await self.draw_versus(self.channel, p1_selected_card, p2_selected_card)
            await self.channel.send(embed=U.make_embed(color=self.SYSTEM_COLOR, image_url=versus_url))

            await self.wait_for(5)

            winner = await self.best_of_three(p1_selected_card, p2_selected_card)
            if winner == "None":
                return
            elif winner == "tie":
                await self.channel.send(embed=U.make_embed(
                    color=self.SYSTEM_COLOR,
                    title="__Tie Breaker__",
                    description="It's a tie! Replaying the round..."
                ))
            else:
                win_counts[winner] += 1
                winner_name = (
                    self._p1.user.display_name
                    if winner == "Player 1"
                    else self._p2.user.display_name
                )
                await self.channel.send(embed=U.make_embed(
                    color=(
                        self.P1_COLOR
                        if winner == "Player 1"
                        else self.P2_COLOR
                    ),
                    title=f"__{winner_name} Wins!__",
                    description=f"`{winner_name}` wins the round!"
                ))

            self.p1_deck.add_override(p1_selected_card)
            self.p2_deck.add_override(p2_selected_card)
            round_idx += 1

        await self._announce_winner(win_counts)
                
################################################################################
    async def random_roll(self, low: int, high: int, roller: TCGPlayer) -> Optional[int]:
        
        view = CardBattleRollView(roller.user)
        
        prompt = U.make_embed(
            color=(
                self.P1_COLOR
                if roller == self._p1
                else self.P2_COLOR
            ),
            title="__Card Battle Roll__",
            description=(
                f"`{roller.user.display_name}`, please roll a {high}-sided dice!"
            )
        )
        await self.channel.send(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete:
            return
        
        return random.randint(low, high)

################################################################################
    async def get_matching_cards(self, deck: CardDeck, roll: int, player_name: str) -> List[DeckCardSlot]:

        matching_cards = deck.get_die_marker_matching(roll)
        addl = 1

        while not matching_cards:
            prompt = U.make_embed(
                color=(
                    self.P1_COLOR
                    if deck == self.p1_deck
                    else self.P2_COLOR
                ),
                title="__No Matching Cards__",
                description=(
                    f"{player_name} has no cards matching the roll of `{roll}`.\n\n"
                    f"Expanding search to an additional span of +/-{addl}."
                )
            )
            await self.channel.send(embed=prompt)
            matching_cards.extend(deck.get_die_marker_matching(roll - addl))
            matching_cards.extend(deck.get_die_marker_matching(roll + addl))
            addl += 1

        return matching_cards

################################################################################
    async def select_card(self, user, matching_cards, player_deck) -> TradingCard:

        await player_deck.generate_image(None)

        player_name = user.display_name
        prompt = U.make_embed(
            color=(
                self.P1_COLOR
                if player_deck == self.p1_deck
                else self.P2_COLOR
            ),
            title=f"__{player_name} Card Selection__",
            description=(
                f"{player_name} has {len(matching_cards)} matching cards: "
                f"{', '.join([c.card.name for c in matching_cards])}\n\n"
                "Please select a card to play."
            ),
            image_url=player_deck.image
        )
        view = FroggeSelectView(user, [c.card.select_option() for c in matching_cards])

        await self.channel.send(embed=prompt, view=view)
        await view.wait()

        return player_deck.get_card_by_id(view.value)

################################################################################
    async def best_of_three(self, p1_card, p2_card) -> str:

        round_stats = ["CUTE", "CUDDLE", "CRUSH"]
        p1_wins, p2_wins = 0, 0
        roller = self._p1 if random.choice([True, False]) else self._p2
        player_color = self.P1_COLOR if roller == self._p1 else self.P2_COLOR

        prompt = U.make_embed(
            color=player_color,
            title="__RANDOM!__",
            description=f"**`{roller.user.display_name}`** will roll first!",
            thumbnail_url=roller.user.display_avatar.url
        )
        await self.channel.send(embed=prompt)

        await self.wait_for(2)

        for stat in round_stats:
            prompt = U.make_embed(
                color=self.SYSTEM_COLOR,
                title="__Stat Comparison__",
                description=f"Comparing `{stat}` stats!",
                image_url=self.get_stat_image(stat)
            )
            await self.channel.send(embed=prompt)
            await self.wait_for(2)

            while True:
                roll_result = await self.random_roll(0, 999, roller)
                if not roll_result:
                    return "None"

                await self.channel.send(embed=U.make_embed(
                    color=player_color,
                    description=(
                        f"{roller.user.display_name} rolled a __**`{roll_result}`**__!"
                    )
                ))
                await self.wait_for(2)

                p1_bad_flag, p2_bad_flag = await self.compare_bad_stats(p1_card, p2_card, roll_result)
                await self.wait_for(2)

                if p1_bad_flag and p2_bad_flag:
                    await self.channel.send(embed=U.make_embed(
                        color=self.SYSTEM_COLOR,
                        title="__Tie Breaker__",
                        description=(
                            "Both players `BAD` stat matched! A tie! Rerolling..."
                        )
                    ))
                    await self.wait_for(2)
                elif p1_bad_flag:
                    p2_wins += 1
                    break
                elif p2_bad_flag:
                    p1_wins += 1
                    break
                else:
                    p1_absolute_value = p1_card.get_absolute_value(stat, roll_result)
                    p2_absolute_value = p2_card.get_absolute_value(stat, roll_result)

                    description = f"{self._p1.user.display_name} Absolute Distance: `{p1_absolute_value}`"
                    if p1_absolute_value < p2_absolute_value:
                        description += " *(WINNER)*"
                    description += "\n"
                    description += f"{self._p2.user.display_name} Absolute Distance: `{p2_absolute_value}`"
                    if p2_absolute_value < p1_absolute_value:
                        description += " *(WINNER)*"

                    await self.channel.send(embed=U.make_embed(color=self.SYSTEM_COLOR, description=description))
                    await self.wait_for(1)

                    if p1_absolute_value < p2_absolute_value:
                        p1_wins += 1
                        break
                    elif p2_absolute_value < p1_absolute_value:
                        p2_wins += 1
                        break
                    else:
                        prompt = U.make_embed(
                            color=self.SYSTEM_COLOR,
                            title="__Oops!__",
                            description=(
                                "Both players have the same absolute value! Re-rolling..."
                            )
                        )
                        await self.channel.send(embed=prompt)
                        await self.wait_for(3)

            if p1_wins == 2 or p2_wins == 2:
                break

            roller = self._p1 if roller == self._p2 else self._p2
            player_color = self.P1_COLOR if roller == self._p1 else self.P2_COLOR

            await self.wait_for(2)

        if p1_wins > p2_wins:
            return "Player 1"
        elif p2_wins > p1_wins:
            return "Player 2"
        else:
            return "tie"

################################################################################
    @staticmethod
    def get_stat_image(stat_name: str) -> str:

        match stat_name:
            case "CUTE":
                return BotImages.Cute
            case "CUDDLE":
                return BotImages.Cuddle
            case "CRUSH":
                return BotImages.Crush
            case _:
                raise ValueError(f"Invalid stat name: {stat_name}")

################################################################################
    async def compare_bad_stats(self, p1_card, p2_card, roll_result) -> tuple:

        p1_bad_flag = False
        p2_bad_flag = False

        if p1_result := p1_card.compare_bad(roll_result):
            p1_bad_list = p1_card.int_to_list(p1_card.bad)
            stats = []
            for i, number in enumerate(p1_bad_list):
                if i == p1_result[0]:
                    stat = f"**[{number}]**"
                else:
                    stat = f"{number}"
                stats.append(stat)
            p1_bad_str = "-".join(stats)
            prompt = U.make_embed(
                color=self.P1_COLOR,
                description=(
                    f"Player 1 `BAD` stat MATCHED {p1_bad_str}! They Lose!"
                )
            )
            await self.channel.send(embed=prompt)
            p1_bad_flag = True
        if p2_result := p2_card.compare_bad(roll_result):
            p2_bad_list = p2_card.int_to_list(p2_card.bad)
            stats = []
            for i, number in enumerate(p2_bad_list):
                if i == p2_result[0]:
                    stat = f"**[{number}]**"
                else:
                    stat = f"{number}"
                stats.append(stat)
            p2_bad_str = "-".join(stats)
            prompt = U.make_embed(
                color=self.P2_COLOR,
                description=(
                    f"Player 2 `BAD` stat MATCHED {p2_bad_str}! They Lose!"
                )
            )
            await self.channel.send(embed=prompt)
            p2_bad_flag = True

        return p1_bad_flag, p2_bad_flag

################################################################################
    async def _announce_winner(self, win_counts: dict) -> None:
        
        if win_counts["Player 1"] > win_counts["Player 2"]:
            message = f"{self._p1.user.display_name} wins the battle!"
        elif win_counts["Player 2"] > win_counts["Player 1"]:
            message = f"{self._p2.user.display_name} wins the battle!"
        else:
            message = "The battle is a tie!"

        prompt = U.make_embed(
            color=self.SYSTEM_COLOR,
            title="__Battle Concluded__",
            description=message,
            image_url=BotImages.Winner
        )
        await self.channel.send(embed=prompt)

        self._mgr._battles.remove(self)
        
################################################################################
    @staticmethod
    def get_round_info(round_idx: int) -> Tuple[str, str]:
        
        match round_idx:
            case 1:
                return "First", BotImages.Round1
            case 2:
                return "Second", BotImages.Round2
            case 3:
                return "Third", BotImages.Round3
            case 4:
                return "Fourth", BotImages.Round4
            case 5:
                return "Fifth", BotImages.Round5
            case _:
                raise ValueError(f"Invalid round index: {round_idx}")
            
################################################################################
    async def draw_versus(self, channel: Thread, card1: TradingCard, card2: TradingCard) -> str:

        slot_width = 150
        slot_height = 210

        overlay = Image.open("Assets/Versus.png")
        canvas_width = overlay.width
        canvas_height = overlay.height
        
        # (Padding of 10 hardcoded in)
        card1_loc = (0, 10)
        card2_loc = (canvas_width - slot_width, 10)
        
        canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))  # Transparent background
        
        # Draw the player 1 card
        try:
            card1_image = Image.open(BytesIO(requests.get(card1.permalink).content))
        except UnidentifiedImageError:
            card1.permalink = None
            await channel.send(embed=PermalinkFailed(card1.name))
        else:
            card1_image = card1_image.resize((slot_width, slot_height))
            canvas.paste(card1_image, card1_loc, card1_image)
            
        # Draw the player 2 card
        try:
            card2_image = Image.open(BytesIO(requests.get(card2.permalink).content))
        except UnidentifiedImageError:
            card2.permalink = None
            await channel.send(embed=PermalinkFailed(card2.name))
        else:
            card2_image = card2_image.resize((slot_width, slot_height))
            canvas.paste(card2_image, card2_loc, card2_image)
            
        # Draw the overlay
        overlay = Image.open("Assets/Versus.png")
        canvas.paste(overlay, (0, 0), overlay)

        filepath = f"Files/Versus-{self._id}.png"
        canvas.save(filepath)

        file = File(filepath)
        dump = await self._mgr.bot._img_dump.send(file=file)

        try:
            os.remove(filepath)
        except FileNotFoundError:
            pass

        return dump.attachments[0].url

################################################################################
    @staticmethod
    def _select_die_image(roll: int) -> str:

        match roll:
            case 1:
                return BotImages.Die1
            case 2:
                return BotImages.Die2
            case 3:
                return BotImages.Die3
            case 4:
                return BotImages.Die4
            case 5:
                return BotImages.Die5
            case 6:
                return BotImages.Die6
            case _:
                raise ValueError(f"Invalid die roll: {roll}")

################################################################################

