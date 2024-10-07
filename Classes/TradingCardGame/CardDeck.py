from __future__ import annotations

import os

from io import BytesIO
from typing import TYPE_CHECKING, List, Type, TypeVar, Any, Dict, Optional

import requests
from PIL import Image, UnidentifiedImageError, ImageOps
from discord import Embed, Interaction, SelectOption, File

from Errors import (
    DeckFull,
    MalformedID,
    InvalidCardName,
    CardNotInCollection,
    CardAlreadyInDeck,
    PermalinkFailed,
)
from UI.Common import BasicTextModal, FroggeSelectView
from UI.TradingCardGame import CardDeckStatusView, CardAddMethodView, CardSelectView
from Utilities import Utilities as U
from .DeckCardSlot import DeckCardSlot

if TYPE_CHECKING:
    from Classes import DeckManager, CardManager, RentARaBot, TradingCard, CardCollection
################################################################################

__all__ = ("CardDeck", )

CD = TypeVar("CD", bound="CardDeck")

################################################################################
class CardDeck:

    __slots__ = (
        "_id",
        "_mgr",
        "_cards",
        "_name",
        "_image",
        "_overrides",
    )
    
    MAX_DECK_SIZE = 6
    
################################################################################
    def __init__(self, mgr: DeckManager, _id: str, name: str, **kwargs) -> None:

        self._id: str = _id
        self._mgr: DeckManager = mgr
        
        self._name: str = name
        self._cards: List[DeckCardSlot] = kwargs.get("cards", [])
        self._image: Optional[str] = kwargs.get("image", None)
        
        self._overrides: List[str] = []
    
################################################################################
    @classmethod
    def new(cls: Type[CD], mgr: DeckManager, name: str) -> CD:

        new_id = mgr.bot.database.insert.card_deck(mgr.collection_id, name)
        return cls(mgr, new_id, name)
    
################################################################################
    @classmethod
    def load(cls: Type[CD], mgr: DeckManager, data: Dict[str, Any]) -> CD:

        ddata = data["deck"]
        
        self: CD = cls.__new__(cls)
        
        self._id = ddata[0]
        self._mgr = mgr
        
        self._name = ddata[2]
        self._cards = [DeckCardSlot.load(self, card) for card in data["cards"]]
        self._image = ddata[3]
        
        self._overrides = []
        
        return self
    
################################################################################
    def __eq__(self, other: CardDeck) -> bool:

        return self.id == other.id

################################################################################
    def __len__(self) -> int:
        
        return len(self._cards)
    
################################################################################
    def __contains__(self, item: TradingCard) -> bool:
        
        return any(slot.card == item for slot in self._cards)
    
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._mgr.bot
    
################################################################################
    @property
    def card_manager(self) -> CardManager:
        
        return self._mgr.card_manager
    
################################################################################
    @property
    def parent_collection(self) -> CardCollection:
        
        return self._mgr._parent
    
################################################################################
    @property
    def id(self) -> str:
        
        return self._id
    
################################################################################
    @property
    def name(self) -> str:
        
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        
        self._name = value
        self.update()
        
################################################################################
    @property
    def image(self) -> Optional[str]:
        
        return self._image
    
    @image.setter
    def image(self, value: Optional[str]) -> None:
        
        self._image = value
        self.update()
        
################################################################################
    @property
    def is_full(self) -> bool:
        
        return len(self) >= self.MAX_DECK_SIZE
    
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.card_deck(self)
        
################################################################################
    def status(self) -> Embed:
        
        card_list = "\n".join([
            f"{slot.order}. {slot.card.name}"
            for slot in self._cards
        ])
        
        return U.make_embed(
            title=f"__Deck Status: {self.name}__",
            description=(
                f"**[`{len(self)}/6`] Cards Selected**\n"
                f"{U.draw_line(extra=20)}\n"
                f"{card_list}"
            ),
            image_url=self.image
        )
    
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = CardDeckStatusView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
    async def add_card(self, interaction: Interaction) -> None:
        
        if len(self) >= self.MAX_DECK_SIZE:
            error = DeckFull(self.MAX_DECK_SIZE)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        prompt = U.make_embed(
            title="__Add Card to Deck__",
            description=(
                "Please select the method you want to use to add a card to your deck.\n\n"
                
                "1. **By ID Number**\n"
                "2. **By Card Name**\n"
                "3. **Via Select Menu**\n"
            ),
        )
        view = CardAddMethodView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False or view.value is None:
            return
        
        method, inter = view.value
        
        match method:
            case 1:
                card = await self.try_get_card_by_id(inter)
            case 2:
                card = await self.try_get_card_by_name(inter)
            case 3:
                card = await self.try_get_card_by_select(inter)
            case _:
                raise ValueError("Invalid selection.")
        
        if card is None:
            return
        
        slot = DeckCardSlot.new(self, card)
        self._cards.append(slot)
        
        await self.generate_image(interaction)
        
################################################################################
    async def try_get_card_by_id(self, interaction: Interaction) -> Optional[TradingCard]:
        
        modal = BasicTextModal(
            title="Enter Card ID",
            attribute="ID",
            example="eg. '1-042'",
            max_length=7
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        raw_index = modal.value
        
        async def malformed_id() -> None:
            e = MalformedID(raw_index)
            await interaction.respond(embed=e, ephemeral=True)

        try:
            series_str, index = raw_index.split("-")
            series_number = int(series_str) - 1
        except (ValueError, TypeError):
            print("ValueError")
            return await malformed_id()
        
        series = self.card_manager.get_series_by_order(series_number)
        if series is None:
            print("Series is None")
            return await malformed_id()
        
        card = series.get_card_by_index(index)
        if card is None:
            print("Card is None")
            return await malformed_id()
        
        if card not in self.parent_collection:
            error = CardNotInCollection(card.name)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        if card in self:
            error = CardAlreadyInDeck(card.name)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        return card
        
################################################################################
    async def try_get_card_by_name(self, interaction: Interaction) -> Optional[TradingCard]:
        
        modal = BasicTextModal(
            title="Enter Card Name",
            attribute="Name",
            example="eg. 'Sifu Komodo'",
            max_length=50
        )
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return

        cards = self.card_manager.get_cards_by_name(modal.value)
        if not cards:
            error = InvalidCardName(modal.value)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        if len(cards) == 1:
            return cards[0]
            
        prompt = U.make_embed(
            title="__Select Card__",
            description="Multiple cards found. Please select one."
        )
        view = FroggeSelectView(interaction.user, [c.select_option() for c in cards])
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        card = self.card_manager.get_card(view.value)
        if card is None:
            error = InvalidCardName(view.value)
            await interaction.respond(embed=error, ephemeral=True)
            return

        if card not in self.parent_collection:
            error = CardNotInCollection(card.name)
            await interaction.respond(embed=error, ephemeral=True)
            return

        if card in self:
            error = CardAlreadyInDeck(card.name)
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        return card

################################################################################
    async def try_get_card_by_select(self, interaction: Interaction) -> Optional[TradingCard]:

        series_options = []
        for series in self.card_manager.series_list:
            num_owned_cards = len(self.parent_collection.get_cards_by_series(series))
            series_options.append(
                SelectOption(
                    label=series.name, 
                    value=series.id,
                    description=f"({num_owned_cards} owned cards)"
                )
            )

        prompt = U.make_embed(
            title="__Select Series__",
            description="Please select the series of the card you wish to add."
        )
        view = FroggeSelectView(interaction.user, series_options)

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return
        
        series = self.card_manager[view.value]
        series_cards = self.parent_collection.get_cards_by_series(series)
        for card in series_cards:
            if card in self:
                series_cards.remove(card)
                
        prompt = U.make_embed(
            title="__Select Card__",
            description="Please select the card you wish to add."
        )
        view = CardSelectView(interaction.user, [c.select_option() for c in series_cards])

        await interaction.respond(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        card = self.card_manager.get_card(view.value)
        
        return card
    
################################################################################
    async def remove_card(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Remove Card__",
            description=(
                "Please select the card you want to remove."
            ),
        )
        card = await self.select_card(interaction, prompt)
        if card is None:
            return
        
        slot = self.get_slot_by_card(card)
        missing_idx = slot.order
        
        await slot.remove(interaction)
        
        for slot in self._cards:
            if slot.order > missing_idx:
                slot.order -= 1

        await self.generate_image(interaction)
        
################################################################################
    async def select_card(self, interaction: Interaction, prompt: Embed) -> Optional[TradingCard]:
        
        cards = [slot.card for slot in self._cards]
        view = FroggeSelectView(interaction.user, [c.select_option() for c in cards])
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        return self.get_card_by_id(view.value)
    
################################################################################
    def get_card_by_id(self, card_id: str) -> Optional[TradingCard]:
        
        return next((slot.card for slot in self._cards if slot.card.id == card_id), None)
    
################################################################################
    def get_slot_by_card(self, card: TradingCard) -> Optional[DeckCardSlot]:
        
        return next((slot for slot in self._cards if slot.card == card), None)
    
################################################################################
    def select_option(self) -> SelectOption:
            
        return SelectOption(
            label=self.name,
            value=self.id,
            description=f"({len(self)} cards)",
        )
    
################################################################################
    async def generate_image(self, interaction: Optional[Interaction]) -> None:
        
        slot_width = 150
        slot_height = 210

        canvas_width = slot_width * 6
        canvas_height = slot_height
        canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))  # Transparent background

        for i, slot in enumerate(self._cards):
            if not slot.card.permalink:
                continue
                
            try:
                # Download the card image from the URL
                response = requests.get(slot.card.permalink)
                card_image = Image.open(BytesIO(response.content))
            except UnidentifiedImageError:
                slot.card.permalink = None
                if interaction:
                    await interaction.respond(embed=PermalinkFailed(slot.card.name), ephemeral=True)
                    # card_image = Image.open(f"Files/DefaultCard.png")
                    continue
            else:
                # Resize the card image to fit within the slot
                card_image = card_image.resize((slot_width, slot_height))

            # Check if the card id is in the overrides list
            if slot.card.id in self._overrides:
                # Apply grayscale filter to the image
                card_image = ImageOps.grayscale(card_image)
                # Convert to RGBA
                card_image = card_image.convert("RGBA")
                # Apply a gray tint by reducing the alpha (transparency)
                alpha = Image.new('L', card_image.size, color=128)  # 128 is for 50% transparency
                card_image.putalpha(alpha)

            # Calculate the position to paste the card on the canvas
            position = (i * slot_width, 0)
            canvas.paste(card_image, position, card_image)

        filepath = f"Files/Deck-{self.id}.png"
        canvas.save(filepath)

        file = File(filepath)
        dump = await self.bot._img_dump.send(file=file)

        self.image = dump.attachments[0].url
        
        try:
            os.remove(filepath)
        except FileNotFoundError:
            pass
        
################################################################################
    def get_die_marker_matching(self, roll: int) -> List[DeckCardSlot]:
        
        return [
            slot 
            for slot in self._cards 
            if slot.card.die_marker == roll 
            and slot.card.id not in self._overrides
        ]
    
################################################################################
    def add_override(self, card: TradingCard) -> None:
        
        self._overrides.append(card.id)
        
################################################################################
    def reset_overrides(self) -> None:

        self._overrides.clear()
        self.generate_image(None)

################################################################################
