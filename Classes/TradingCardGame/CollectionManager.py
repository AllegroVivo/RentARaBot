from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Any, Dict

from discord import Embed, EmbedField, Interaction

from .CardCollection import CardCollection
from Utilities import Utilities as U
from UI.TradingCardGame import CollectionManagerMenuView

if TYPE_CHECKING:
    from Classes import TCGManager, RentARaBot, GuildData, CardManager
################################################################################

__all__ = ("CollectionManager", )

################################################################################
class CollectionManager:

    __slots__ = (
        "_mgr",
        "_collections",
    )
    
################################################################################
    def __init__(self, mgr: TCGManager) -> None:

        self._mgr: TCGManager = mgr
        self._collections: List[CardCollection] = []
    
################################################################################
    async def load_all(self, data: List[Dict[str, Any]]) -> None:
        
        self._collections = [await CardCollection.load(self, d) for d in data]
            
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
    async def main_menu(self, interaction: Interaction) -> None:
        
        embed = U.make_embed(
            title="__Collection Management Menu__",
            description="Select an option below to manage user collections.",
        )
        view = CollectionManagerMenuView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    async def modify_collection(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="__Modify Collection__",
            description="Enter a user to modify their collection.",
        )
        user = await U.listen_for(interaction, prompt, U.MentionableType.User)
        if user is None:
            return
        
        collection = self[user.id]
        if collection is None:
            collection = CardCollection.new(self, user)
            self._collections.append(collection)
            
        await collection.menu(interaction)
    
################################################################################
    async def view_collection(self, interaction: Interaction) -> None:
        
        pass
    
################################################################################
