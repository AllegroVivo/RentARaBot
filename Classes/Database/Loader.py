from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Tuple

from .Branch import DBWorkerBranch

if TYPE_CHECKING:
    pass
################################################################################

__all__ = ("DatabaseLoader",)

################################################################################
class DatabaseLoader(DBWorkerBranch):
    """A utility class for loading data from the database."""

    def load_all(self) -> Dict[int, Dict[str, Any]]:
        """Performs all sub-loaders and returns a dictionary of their results."""

        print("Database", "Performing database load_all.")

        return self._parse_all(self._get_payload())

################################################################################
    def _load_data_from_table(self, table_name: str) -> Tuple[Tuple[Any, ...]]:
        """Load data from a specific table."""

        self.execute(f"SELECT * FROM {table_name};")
        return self.fetchall()
    
################################################################################
    def _get_payload(self) -> Dict[str, Any]:

        table_list = [
            "form_options",
            "form_questions",
            "form_response_collections",
            "forms",
            "form_responses",
            "form_prompts",
            "form_question_prompts",
            "profile_requirements",
            "profiles",
            "profile_details",
            "profile_ataglance",
            "profile_personality",
            "profile_images",
            "profile_addl_images",
            "profile_channel_groups",
            "profile_preference_groups",
            "profile_preferences",
            "trading_card_details",
            "trading_card_stats",
            "trading_cards",
            "trading_card_series",
            "trading_card_collections",
            "trading_card_counts",
            "role_relations",
            "verification_config",
            "tcg_booster_card_config",
            "tcg_booster_config",
            "tcg_rarity_weights",
            "tcg_card_decks",
            "tcg_deck_card_slots",
        ]

        ret = {}
        for table in table_list:
            ret[table] = self._load_data_from_table(table)
            
        return ret
        
################################################################################
    def _parse_all(self, payload: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
        
        ret = {
            g.id: {
                "forms": [],
                "profiles": {
                    "requirements": None,
                    "profiles": [],
                    "channels": [],
                },
                "trading_card_game": {
                    "cards": [],
                    "collections": [],
                    "booster_data": {
                        "booster_config": None,
                        "card_configs": [],
                    },
                },
                "verification": {
                    "config": None,
                    "roles": []
                }
            }
            for g in self.bot.guilds
        }
        
        # Forms
        for form in payload["forms"]:
            ret[form[1]]["forms"].append({
                "form": form,
                "questions": [],
                "responses": [
                    response 
                    for response in payload["form_response_collections"]
                    if response[1] == form[0]
                ],
                "pre_prompt": next((
                    prompt
                    for prompt in payload["form_prompts"]
                    if prompt[1] == form[0]
                    and prompt[6] is False
                ), None),
                "post_prompt": next((
                    prompt
                    for prompt in payload["form_prompts"]
                    if prompt[1] == form[0]
                    and prompt[6] is True
                ), None),
            })
            for question in payload["form_questions"]:
                if question[1] == form[0]:
                    ret[form[1]]["forms"][-1]["questions"].append({
                        "question": question,
                        "options": [
                            option
                            for option in payload["form_options"]
                            if option[1] == question[0]
                        ],
                        "responses": [
                            response
                            for response in payload["form_responses"]
                            if response[0] == question[0]
                        ],
                        "prompt": next((
                            prompt
                            for prompt in payload["form_question_prompts"]
                            if prompt[1] == question[0]
                        ), None)
                    })
                    
        # Profiles
        for req in payload["profile_requirements"]:
            ret[req[0]]["profiles"]["requirements"] = req
        for profile in payload["profiles"]:
            ret[profile[1]]["profiles"]["profiles"].append({
                "profile": profile,
                "details": next((
                    detail
                    for detail in payload["profile_details"]
                    if detail[0] == profile[0]
                ), None),
                "aag": next((
                    ataglance
                    for ataglance in payload["profile_ataglance"]
                    if ataglance[0] == profile[0]
                ), None),
                "personality": next((
                    personality
                    for personality in payload["profile_personality"]
                    if personality[0] == profile[0]
                ), None),
                "images": {
                    "images": next((
                        image
                        for image in payload["profile_images"]
                        if image[0] == profile[0]
                    ), None),
                    "additional": [
                        addl_image
                        for addl_image in payload["profile_addl_images"]
                        if addl_image[1] == profile[0]
                    ],
                },
                "preferences": {
                    "groups": [
                        group
                        for group in payload["profile_preference_groups"]
                        if group[1] == profile[0]
                    ],
                    "preferences": next((
                        pref
                        for pref in payload["profile_preferences"]
                        if pref[0] == profile[0]
                    ), None),
                }
            })
        for group in payload["profile_channel_groups"]:
            ret[group[1]]["profiles"]["channels"].append(group)
            
        # Trading Cards
        for series in payload["trading_card_series"]:
            ret[series[1]]["trading_card_game"]["cards"].append({
                "series": series,
                "cards": [],
            })
            for card in payload["trading_cards"]:
                if card[1] == series[0]:
                    ret[series[1]]["trading_card_game"]["cards"][-1]["cards"].append({
                        "card": card,
                        "details": next((
                            details
                            for details in payload["trading_card_details"]
                            if details[0] == card[0]
                        ), None),
                        "stats": next((
                            stats
                            for stats in payload["trading_card_stats"]
                            if stats[0] == card[0]
                        ), None),
                    })
        for collection in payload["trading_card_collections"]:
            ret[collection[1]]["trading_card_game"]["collections"].append({
                "collection": collection,
                "cards": [
                    card
                    for card in payload["trading_card_counts"]
                    if card[1] == collection[0]
                ],
                "decks": [{
                    "deck": deck,
                    "cards": [
                        card
                        for card in payload["tcg_deck_card_slots"]
                        if card[1] == deck[0]
                    ],
                } for deck in payload["tcg_card_decks"] if deck[1] == collection[0]],
            })
        for booster in payload["tcg_booster_config"]:
            ret[booster[0]]["trading_card_game"]["booster_data"]["booster_config"] = booster
        for config in payload["tcg_booster_card_config"]:
            ret[config[1]]["trading_card_game"]["booster_data"]["card_configs"].append({
                "config": config,
                "weights": [
                    weight
                    for weight in payload["tcg_rarity_weights"]
                    if weight[1] == config[0]
                ],
            })
            
        # Verification
        for config in payload["verification_config"]:
            ret[config[0]]["verification"]["config"] = config
        for role in payload["role_relations"]:
            ret[role[1]]["verification"]["roles"].append(role)
            
        return ret
    
################################################################################
