from __future__ import annotations

from typing import TYPE_CHECKING, List, Any, Dict

from discord import Embed, Interaction, User

from .BattleManager import BattleManager
from .CardManager import CardManager
from .CollectionManager import CollectionManager
from UI.TradingCardGame import (
    TradingCardMainMenuView,
)
from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import GuildData, RentARaBot
################################################################################

__all__ = ("TCGManager", )

################################################################################
class TCGManager:

    __slots__ = (
        "_state",
        "_cards",
        "_collections",
        "_battles",
    )
    
################################################################################
    def __init__(self, state: GuildData) -> None:

        self._state: GuildData = state
        
        self._cards: CardManager = CardManager(self)
        self._collections: CollectionManager = CollectionManager(self)
        self._battles: BattleManager = BattleManager(self)
    
################################################################################
    async def load_all(self, payload: Dict[str, Any]) -> None:
        
        self._cards.load_all(payload["cards"])
        await self._collections.load_all(payload["collections"], payload["booster_data"])
        
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._state.bot
    
################################################################################
    @property
    def guild_id(self) -> int:

        return self._state.guild_id

################################################################################
    @property
    def card_manager(self) -> CardManager:
        
        return self._cards
    
################################################################################
    async def main_menu(self, interaction: Interaction) -> None:
        
        embed = U.make_embed(
            title="__Trading Card Game Module__",
            description=(
                "Welcome to the Trading Card Game module!\n"
                "Select an option below to get started."
            ),
        )
        view = TradingCardMainMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
        
################################################################################
    async def trading_cards_menu(self, interaction: Interaction) -> None:
        
        await self._cards.main_menu(interaction)
    
################################################################################
    async def collections_menu(self, interaction: Interaction) -> None:
        
        await self._collections.main_menu(interaction)
    
################################################################################
    async def battle_configuration_menu(self, interaction: Interaction) -> None:
        
        await self._battles.admin_menu(interaction)
    
################################################################################
    async def admin_ctx_menu(self, interaction: Interaction, user: User) -> None:
        
        await self._collections.admin_ctx_menu(interaction, user)
        
################################################################################
    async def booster_management_menu(self, interaction: Interaction) -> None:
        
        await self._collections.booster_management(interaction)

################################################################################
    async def open_booster(self, interaction: Interaction) -> None:
        
        await self._collections.open_booster(interaction)

################################################################################
    async def user_collection_menu(self, interaction: Interaction) -> None:
        
        await self._collections.user_menu(interaction)
        
################################################################################
