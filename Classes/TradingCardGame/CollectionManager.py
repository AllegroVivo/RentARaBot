from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Any, Dict

from discord import Embed, EmbedField, Interaction, User

from .CardCollection import CardCollection
from Utilities import Utilities as U
from UI.TradingCardGame import CollectionManagerMenuView
from .BoosterPackConfig import BoosterPackConfig

if TYPE_CHECKING:
    from Classes import TCGManager, RentARaBot, GuildData, CardManager
################################################################################

__all__ = ("CollectionManager", )

################################################################################
class CollectionManager:

    __slots__ = (
        "_mgr",
        "_collections",
        "_booster_config",
    )
    
################################################################################
    def __init__(self, mgr: TCGManager) -> None:

        self._mgr: TCGManager = mgr
        
        self._collections: List[CardCollection] = []
        self._booster_config: BoosterPackConfig = BoosterPackConfig(self)
    
################################################################################
    async def load_all(self, coll_data: List[Dict[str, Any]], booster_data: Dict[str, Any]) -> None:
        
        self._collections = [await CardCollection.load(self, d) for d in coll_data]
        self._booster_config.load_all(booster_data)
            
################################################################################
    def __getitem__(self, user_id: int) -> Optional[CardCollection]:
        
        return next((c for c in self._collections if c.user.id == user_id), None)
    
################################################################################
    @property
    def bot(self) -> RentARaBot:
        
        return self._mgr.bot
    
################################################################################
    @property
    def guild(self) -> GuildData:
        
        return self._mgr._state
    
################################################################################
    @property
    def guild_id(self) -> int:
        
        return self.guild.guild_id
    
################################################################################
    @property
    def card_manager(self) -> CardManager:
        
        return self._mgr.card_manager
    
################################################################################
    @property
    def booster_config(self) -> BoosterPackConfig:
        
        return self._booster_config
    
################################################################################
    async def main_menu(self, interaction: Interaction) -> None:
        
        embed = U.make_embed(
            title="__Collection Management Menu__",
            description="Select an option below to manage user collections.",
        )
        view = CollectionManagerMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    def _get_collection(self, user: User) -> CardCollection:

        collection = self[user.id]
        if collection is None:
            collection = CardCollection.new(self, user)
            self._collections.append(collection)
            
        return collection
    
################################################################################
    async def modify_collection(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Modify Collection__",
            description="Enter a user to modify their collection.",
        )
        user = await U.listen_for(interaction, prompt, U.MentionableType.User)
        if user is None:
            return
        
        collection = self._get_collection(user)
        await collection.admin_menu(interaction)
    
################################################################################
    async def view_collection(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="__Modify Collection__",
            description="Enter a user to modify their collection.",
        )
        user = await U.listen_for(interaction, prompt, U.MentionableType.User)
        if user is None:
            return

        collection = self._get_collection(user)
        await collection.view(interaction)

################################################################################
    async def booster_management(self, interaction: Interaction) -> None:
        
        await self._booster_config.main_menu(interaction)
                    
################################################################################
    async def admin_ctx_menu(self, interaction: Interaction, user: User) -> None:

        collection = self._get_collection(user)
        await collection.admin_menu(interaction)

################################################################################
    async def open_booster(self, interaction: Interaction) -> None:

        collection = self._get_collection(interaction.user)
        await collection.open_booster(interaction)

################################################################################
    async def user_menu(self, interaction: Interaction) -> None:

        collection = self._get_collection(interaction.user)
        await collection.user_menu(interaction)
        
################################################################################
