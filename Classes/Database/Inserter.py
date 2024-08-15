from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List, Any

from .Branch import DBWorkerBranch

if TYPE_CHECKING:
    from Classes import *
################################################################################

__all__ = ("DatabaseInserter",)

################################################################################
class DatabaseInserter(DBWorkerBranch):
    """A utility class for inserting new records into the database."""

    def _insert(self, table: str, columns: List[str], values: List[Any]) -> str:

        placeholders = ", ".join(["%s"] * len(values))
        columns_str = ", ".join(columns)
    
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) RETURNING _id;"
        self.execute(query, *values)
    
        return self.fetchone()[0]

################################################################################
    def _insert_no_return(self, table: str, columns: List[str], values: List[Any]) -> None:
    
        placeholders = ", ".join(["%s"] * len(values))
        columns_str = ", ".join(columns)
    
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders});"
        self.execute(query, *values)
    
################################################################################
    def _insert_guild(self, guild_id: int) -> None:

        self.execute(
            "INSERT INTO profile_requirements (guild_id) VALUES (%s) ON CONFLICT DO NOTHING;"
            "INSERT INTO verification_config (guild_id) VALUES (%s) ON CONFLICT DO NOTHING;"
            "INSERT INTO tcg_booster_config (guild_id) VALUES (%s) ON CONFLICT DO NOTHING;",
            guild_id, guild_id, guild_id
        )
        
################################################################################
    def _insert_form(self, guild_id: int, name: str) -> str:
        
        return self._insert(
            "forms", 
            ["_id", "guild_id", "form_name"], 
            [self.generate_id(), guild_id, name]
        )
    
################################################################################
    def _insert_form_option(self, question_id: str) -> str:
        
        return self._insert(
            "form_options",
            ["_id", "question_id"],
            [self.generate_id(), question_id]
        )
        
################################################################################
    def _insert_form_question(self, form_id: str, order: int, primary_text: str) -> str:
        
        return self._insert(
            "form_questions",
            ["_id", "form_id", "sort_order", "primary_text"],
            [self.generate_id(), form_id, order, primary_text]
        )
    
################################################################################
    def _insert_form_response_collection(
        self, 
        form_id: str,
        user_id: int,
        questions: List[str],
        responses: List[str]
    ) -> str:
        
        return self._insert(
            "form_response_collections",
            ["_id", "form_id", "user_id", "questions", "responses"],
            [self.generate_id(), form_id, user_id, questions, responses]
        )
    
################################################################################
    def _insert_form_response(self, question_id: str, user_id: int, responses: List[str]) -> None:
        
        self._insert_no_return(
            "form_responses",
            ["question_id", "user_id", "values"],
            [question_id, user_id, responses]
        )
        
################################################################################
    def _insert_question_prompt(self, question_id: str) -> str:
        
        return self._insert(
            "form_question_prompts",
            ["_id", "question_id"],
            [self.generate_id(), question_id]
        )
        
################################################################################
    def _insert_form_prompt(self, form_id: str, post_prompt: bool) -> str:
        
        return self._insert(
            "form_prompts",
            ["_id", "form_id", "post_prompt"],
            [self.generate_id(), form_id, post_prompt]
        )
    
################################################################################
    def _insert_profile(self, guild_id: int, user_id: int) -> str:
        
        new_id = self.generate_id()
        
        self.execute(
            "INSERT INTO profiles (_id, guild_id, user_id) VALUES (%s, %s, %s);"
            "INSERT INTO profile_ataglance (profile_id) VALUES (%s);"
            "INSERT INTO profile_details (profile_id) VALUES (%s);"
            "INSERT INTO profile_personality (profile_id) VALUES (%s);"
            "INSERT INTO profile_images (profile_id) VALUES (%s);"
            "INSERT INTO profile_preferences (profile_id) VALUES (%s);",
            new_id, guild_id, user_id, new_id, new_id, new_id, new_id,
            new_id
        )
        
        return new_id
        
################################################################################
    def _insert_trading_card(self, series_id: str, idx: str) -> str:
        
        new_id = self.generate_id()
        
        self.execute(
            "INSERT INTO trading_cards (_id, series_id, card_idx) VALUES (%s, %s, %s);"
            "INSERT INTO trading_card_details (card_id) VALUES (%s);"
            "INSERT INTO trading_card_stats (card_id) VALUES (%s);",
            new_id, series_id, idx, new_id, new_id
        )#
        
        return new_id
    
################################################################################
    def _insert_trading_card_series(self, guild_id: int, order: int, name: str) -> str:
        
        return self._insert(
            "trading_card_series",
            ["_id", "guild_id", "sort_order", "name"],
            [self.generate_id(), guild_id, order, name]
        )
    
################################################################################
    def _insert_card_collection(self, guild_id: int, user_id: int) -> str:
        
        return self._insert(
            "trading_card_collections",
            ["_id", "guild_id", "user_id"],
            [self.generate_id(), guild_id, user_id]
        )
    
################################################################################
    def _insert_card_count(self, collection_id: str, card_id: str, count: int) -> str:
        
        return self._insert(
            "trading_card_counts",
            ["_id", "collection_id", "card_id", "card_qty"],
            [self.generate_id(), collection_id, card_id, count]
        )
        
################################################################################
    def _insert_role_relation(self, guild_id: int) -> str:
        
        return self._insert(
            "role_relations",
            ["_id", "guild_id"],
            [self.generate_id(), guild_id]
        )
    
################################################################################
    def _insert_profile_channel_group(self, guild_id: int) -> str:
        
        return self._insert(
            "profile_channel_groups",
            ["_id", "guild_id"],
            [self.generate_id(), guild_id]
        )
    
################################################################################
    def _insert_preference_group(self, profile_id: str, gender: int) -> str:
        
        return self._insert(
            "profile_preference_groups",
            ["_id", "profile_id", "gender"],
            [self.generate_id(), profile_id, gender]
        )
    
################################################################################
    def _insert_rarity_weight(self, parent_id: str, rarity: int) -> str:
        
        return self._insert(
            "tcg_rarity_weights",
            ["_id", "parent_id", "rarity"],
            [self.generate_id(), parent_id, rarity]
        )
    
################################################################################
    def _insert_additional_image(self, parent_id: str, url: str) -> str:
        
        return self._insert(
            "profile_addl_images",
            ["_id", "profile_id", "url"],
            [self.generate_id(), parent_id, url]
        )
    
################################################################################
    def _insert_booster_card_config(self, guild_id: int, order: int) -> str:
        
        return self._insert(
            "tcg_booster_card_config",
            ["_id", "guild_id", "sort_order"],
            [self.generate_id(), guild_id, order]
        )
    
################################################################################
    def _insert_deck_card_slot(self, deck_id: str, order: int, card_id: str) -> str:
        
        return self._insert(
            "tcg_deck_card_slots",
            ["_id", "deck_id", "sort_order", "card_id"],
            [self.generate_id(), deck_id, order, card_id]
        )
    
################################################################################
    def _insert_card_deck(self, coll_id: str, name: str) -> str:
        
        return self._insert(
            "tcg_card_decks",
            ["_id", "collection_id", "name"],
            [self.generate_id(), coll_id, name]
        )
    
################################################################################

    guild                   = _insert_guild
    form                    = _insert_form
    form_option             = _insert_form_option
    form_question           = _insert_form_question
    form_response_coll      = _insert_form_response_collection
    form_response           = _insert_form_response
    question_prompt         = _insert_question_prompt
    form_prompt             = _insert_form_prompt
    profile                 = _insert_profile
    trading_card            = _insert_trading_card
    card_series             = _insert_trading_card_series
    card_collection         = _insert_card_collection
    card_count              = _insert_card_count
    role_relation           = _insert_role_relation
    profile_channel_group   = _insert_profile_channel_group
    preference_group        = _insert_preference_group
    rarity_weight           = _insert_rarity_weight
    additional_image        = _insert_additional_image
    booster_card_config     = _insert_booster_card_config
    deck_card_slot          = _insert_deck_card_slot
    card_deck               = _insert_card_deck
    
################################################################################
    