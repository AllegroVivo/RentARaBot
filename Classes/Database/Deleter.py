from __future__ import annotations

from typing import TYPE_CHECKING

from .Branch import DBWorkerBranch

if TYPE_CHECKING:
    from Classes import *
################################################################################

__all__ = ("DatabaseDeleter",)

################################################################################
class DatabaseDeleter(DBWorkerBranch):
    """A utility class for deleting data from the database."""
    
    def _delete_form(self, form: Form) -> None:
        
        self.execute(
            "DELETE FROM forms WHERE _id = %s;",
            form.id
        )
        self.execute(
            "DELETE FROM form_questions WHERE form_id = %s;",
            form.id
        )
        for question in form.questions:
            question.delete()
        
################################################################################
    def _delete_form_option(self, option: FormOption) -> None:
        
        self.execute(
            "DELETE FROM form_options WHERE _id = %s;",
            option.id
        )
        
################################################################################
    def _delete_form_question(self, question: FormQuestion) -> None:
        
        self.execute(
            "DELETE FROM form_questions WHERE _id = %s;",
            question.id
        )
        self.execute(
            "DELETE FROM form_options WHERE question_id = %s;",
            question.id
        )
        
################################################################################
    def _delete_form_response(self, question_id: str, user_id: int) -> None:
        
        self.execute(
            "DELETE FROM form_responses WHERE question_id = %s AND user_id = %s;",
            question_id, user_id
        )
        
################################################################################
    def _delete_question_prompt(self, prompt: QuestionPrompt) -> None:
        
        self.execute(
            "DELETE FROM form_question_prompts WHERE _id = %s;",
            prompt.id
        )
        
################################################################################
    def _delete_form_prompt(self, prompt: FormPrompt) -> None:
        
        self.execute(
            "DELETE FROM form_prompts WHERE _id = %s;",
            prompt.id
        )
        
################################################################################
    def _delete_trading_card(self, card: TradingCard) -> None:
        
        self.execute(
            "DELETE FROM trading_cards WHERE _id = %s;"
            "DELETE FROM trading_card_details WHERE card_id = %s;"
            "DELETE FROM trading_card_stats WHERE card_id = %s;",
            card.id, card.id, card.id
        )
        
################################################################################
    def _delete_card_count(self, count: CardCount) -> None:
        
        self.execute(
            "DELETE FROM trading_card_counts WHERE _id = %s;",
            count.id
        )
        
################################################################################
    def _delete_role_relation(self, relation: RoleRelation) -> None:
        
        self.execute(
            "DELETE FROM role_relations WHERE _id = %s;",
            relation.id
        )
        
################################################################################
    def _delete_profile_channel_group(self, group: ProfileChannelGroup) -> None:
        
        self.execute(
            "DELETE FROM profile_channel_groups WHERE _id = %s;",
            group.id
        )
        
################################################################################
    def _delete_additional_image(self, image: AdditionalImage) -> None:
        
        self.execute(
            "DELETE FROM profile_addl_images WHERE _id = %s;",
            image.id
        )
        
################################################################################
    def _delete_profile(self, profile: Profile) -> None:
        
        self.execute(
            "DELETE FROM profiles WHERE _id = %s;"
            "DELETE FROM profile_details WHERE profile_id = %s;"
            "DELETE FROM profile_ataglance WHERE profile_id = %s;"
            "DELETE FROM profile_personality WHERE profile_id = %s;"
            "DELETE FROM profile_images WHERE profile_id = %s;"
            "DELETE FROM profile_addl_images WHERE profile_id = %s;"
            "DELETE FROM profile_preferences WHERE profile_id = %s;",
            profile.id, profile.id, profile.id, profile.id, profile.id,
            profile.id, profile.id
        )

################################################################################
    def _delete_rarity_weight(self, weight: RarityWeight) -> None:
        
        self.execute(
            "DELETE FROM tcg_rarity_weights WHERE _id = %s;",
            weight.id
        )
        
################################################################################
    def _delete_booster_card_config(self, config: BoosterCardConfig) -> None:
        
        self.execute(
            "DELETE FROM tcg_booster_card_config WHERE _id = %s;",
            config.id
        )
        self.execute(
            "DELETE FROM tcg_rarity_weights WHERE parent_id = %s;",
            config.id
        )
        for weight in config.weights:
            weight.delete()
            
################################################################################
    def _delete_deck_card_slot(self, slot: DeckCardSlot) -> None:
        
        self.execute(
            "DELETE FROM tcg_deck_card_slots WHERE _id = %s;",
            slot.id
        )
        
################################################################################

    form_option             = _delete_form_option
    form_question           = _delete_form_question
    form                    = _delete_form
    form_response           = _delete_form_response
    question_prompt         = _delete_question_prompt
    form_prompt             = _delete_form_prompt
    trading_card            = _delete_trading_card
    card_count              = _delete_card_count
    role_relation           = _delete_role_relation
    profile_channel_group   = _delete_profile_channel_group
    additional_image        = _delete_additional_image
    profile                 = _delete_profile
    rarity_weight           = _delete_rarity_weight
    booster_card_config     = _delete_booster_card_config
    deck_card_slot          = _delete_deck_card_slot
    
################################################################################
