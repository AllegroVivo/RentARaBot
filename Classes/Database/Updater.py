from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .Branch import DBWorkerBranch

if TYPE_CHECKING:
    from Classes import *
################################################################################

__all__ = ("DatabaseUpdater",)

################################################################################
class DatabaseUpdater(DBWorkerBranch):
    """A utility class for updating records in the database."""

    def _update_form_option(self, option: FormOption) -> None:
        
        self.execute(
            "UPDATE form_options SET label = %s, description = %s, value = %s, "
            "emoji = %s WHERE _id = %s",
            option.label, option.description, option.value, 
            str(option.emoji) if option.emoji else None, option.id
        )
        
################################################################################
    def _update_form_question(self, question: FormQuestion) -> None:
        
        self.execute(
            "UPDATE form_questions SET sort_order = %s, primary_text = %s, "
            "secondary_text = %s, ui_type = %s, required = %s WHERE _id = %s",
            question.order, question.primary_text, question.secondary_text, 
            question.ui_type.value, question.required, question.id
        )
    
################################################################################
    def _update_form(self, form: Form) -> None:
        
        self.execute(
            "UPDATE forms SET channel_id = %s, form_name = %s, to_notify = %s "
            "WHERE _id = %s",
            form.channel.id if form.channel else None, form.name, 
            [u.id for u in form._to_notify], form.id
        )
        
################################################################################
    def _update_question_prompt(self, prompt: QuestionPrompt) -> None:
        
        self.execute(
            "UPDATE form_question_prompts SET title = %s, description = %s, "
            "thumbnail = %s, show_after = %s, show_cancel = %s WHERE _id = %s",
            prompt.title, prompt.description, prompt.thumbnail, 
            prompt.show_after, prompt.show_cancel, prompt.id
        )
        
################################################################################
    def _update_form_prompt(self, prompt: FormPrompt) -> None:
        
        self.execute(
            "UPDATE form_prompts SET title = %s, description = %s, "
            "thumbnail = %s, show_after = %s, show_cancel = %s WHERE _id = %s",
            prompt.title, prompt.description, prompt.thumbnail, 
            prompt.show_after, prompt.show_cancel, prompt.id
        )
        
################################################################################
    def _update_profile_system(self, mgr: ProfileManager) -> None:
        
        self.execute(
            "UPDATE profile_systems SET staff_channels = %s, "
            "public_channels = %s, staff_roles = %s WHERE guild_id = %s",
            [ch.id for ch in mgr.staff_channels],
            [ch.id for ch in mgr.public_channels], [r.id for r in mgr.staff_roles], 
            mgr.guild.guild_id
        )
        
################################################################################
    def _update_card_details(self, details: TradingCardDetails) -> None:
        
        self.execute(
            "UPDATE trading_card_details SET name = %s, description = %s, "
            "character_group = %s, image_url = %s, rarity = %s, imgur_url = %s "
            "WHERE card_id = %s",
            details.name, details.description, 
            details.group.value if details.group else None, 
            details.image, details.rarity.value, details.permalink, 
            details._parent.id
        )
        
################################################################################
    def _update_card_stats(self, stats: TradingCardStats) -> None:
        
        self.execute(
            "UPDATE trading_card_stats SET bad = %s, battle = %s, "
            "nsfw = %s, sfw = %s, die_marker = %s WHERE card_id = %s",
            stats.bad_stat, stats.battle_stat, stats.nsfw_stat, 
            stats.sfw_stat, stats.die_marker, stats._parent.id
        )
        
################################################################################
    def _update_card_count(self, count: CardCount) -> None:
        
        self.execute(
            "UPDATE trading_card_counts SET card_qty = %s WHERE _id = %s",
            count.quantity, count.id
        )
        
################################################################################
    def _update_role_relation(self, relation: RoleRelation) -> None:
        
        self.execute(
            "UPDATE role_relations SET pending_id = %s, final_id = %s, "
            "message = %s WHERE _id = %s",
            relation.pending_role.id if relation.pending_role else None, 
            relation.final_role.id if relation.final_role else None, 
            relation.message, relation.id
        )
        
################################################################################
    def _update_verification_config(self, config: VerificationConfig) -> None:
        
        self.execute(
            "UPDATE verification_config SET log_events = %s, captcha = %s, "
            "change_name = %s WHERE guild_id = %s",
            config.log_events, config.require_captcha, config.change_name, 
            config.guild_id
        )
        
################################################################################
    def _update_profile_channel_group(self, group: ProfileChannelGroup) -> None:
        
        self.execute(
            "UPDATE profile_channel_groups SET channel_ids = %s, role_ids = %s, "
            "is_private = %s WHERE _id = %s",
            [c.id for c in group.channels], [r.id for r in group.roles], 
            group.is_private, group.id
        )
        
################################################################################
    def _update_profile_requirements(self, reqs: ProfileRequirements) -> None:

        self.execute(
            "UPDATE profile_requirements SET url = %s, color = %s, jobs = %s, "
            "rates = %s, gender = %s, race = %s, orientation = %s, height = %s, "
            "age = %s, mare = %s, world = %s, likes = %s, dislikes = %s, "
            "personality = %s, aboutme = %s, thumbnail = %s, main_image = %s "
            "WHERE guild_id = %s;",
            reqs.url, reqs.color, reqs.jobs, reqs.rates, reqs.gender,
            reqs.race, reqs.orientation, reqs.height, reqs.age, reqs.mare,
            reqs.world, reqs.likes, reqs.dislikes, reqs.personality, reqs.about_me,
            reqs.thumbnail, reqs.main_image, reqs.guild_id
        )

################################################################################
    def _update_preference_group(self, group: PreferenceGroup) -> None:
        
        self.execute(
            "UPDATE profile_preference_groups SET bedroom_pref = %s, "
            "preferences = %s, restrictions = %s WHERE _id = %s",
            group.bedroom_pref.value if group.bedroom_pref else None,
            [p.value for p in group.preferences], [r.value for r in group.restrictions],
            group.id
        )
        
################################################################################
    def _update_profile_preferences(self, prefs: ProfilePreferences) -> None:
        
        self.execute(
            "UPDATE profile_preferences SET activities = %s, music = %s, "
            "zodiac_self = %s, zodiac_partners = %s WHERE profile_id = %s",
            [a.value for a in prefs.activities], [m.value for m in prefs.music_prefs], 
            prefs.zodiac_self.value if prefs.zodiac_self else None,
            [z.value for z in prefs.zodiac_partners], prefs.profile_id
        )
        
################################################################################
    def _update_booster_pack_config(self, config: BoosterPackConfig) -> None:
        
        self.execute(
            "UPDATE tcg_booster_config SET slots = %s WHERE guild_id = %s",
            config.slots, config.guild_id
        )
        
################################################################################
    def _update_booster_card_config(self, config: BoosterCardConfig) -> None:
        
        self.execute(
            "UPDATE tcg_booster_card_config SET always_new = %s WHERE _id = %s",
            config.always_new, config.id
        )
        
################################################################################
    def _update_rarity_weight(self, weight: RarityWeight) -> None:
        
        self.execute(
            "UPDATE tcg_rarity_weights SET weight = %s WHERE _id = %s",
            weight.weight, weight.id
        )
        
################################################################################
    def _update_profile_details(self, details: ProfileDetails) -> None:
        
        self.execute(
            "UPDATE profile_details SET char_name = %s, url = %s, color = %s, "
            "jobs = %s, rates = %s where profile_id = %s",
            details.name, details.custom_url, 
            details.color.value if details.color else None, 
            details.jobs, details.rates, details.profile_id
        )
        
################################################################################
    def _update_profile_ataglance(self, aag: ProfileAtAGlance) -> None:
        
        self.execute(
            "UPDATE profile_ataglance SET world = %s, gender = %s, pronouns = %s, "
            "race = %s, clan = %s, orientation = %s, height = %s, age = %s, "
            "mare = %s WHERE profile_id = %s",
            aag.world.value if aag.world else None,
            aag.gender.value if aag.gender else None,
            [p.value for p in aag.pronouns], aag.race.value if aag.race else None,
            aag.clan.value if aag.clan else None,
            aag.orientation.value if aag.orientation else None,
            aag.height, aag.age, aag.mare, aag.profile_id
        )
        
################################################################################
    def _update_profile_personality(self, personality: ProfilePersonality) -> None:
        
        self.execute(
            "UPDATE profile_personality SET likes = %s, dislikes = %s, "
            "personality = %s, aboutme = %s WHERE profile_id = %s",
            personality.likes, personality.dislikes, personality.personality,
            personality.aboutme, personality.profile_id
        )
        
################################################################################
    def _update_profile_images(self, images: ProfileImages) -> None:
        
        self.execute(
            "UPDATE profile_images SET thumbnail = %s, main_image = %s "
            "WHERE profile_id = %s",
            images.thumbnail, images.main_image, images.profile_id
        )
        
################################################################################
    def _update_additional_image(self, image: AdditionalImage) -> None:
        
        self.execute(
            "UPDATE profile_addl_images SET url = %s, caption = %s WHERE _id = %s",
            image.url, image.caption, image.id
        )
        
################################################################################
    def _update_profile(self, profile: Profile) -> None:
        
        self.execute(
            "UPDATE profiles SET post_url = %s, is_public = %s where _id = %s",
            profile.post_url, profile.is_public, profile.id
        )
        
################################################################################
    def _update_card_collection(self, coll: CardCollection) -> None:
        
        self.execute(
            "UPDATE trading_card_collections SET boosters = %s WHERE _id = %s",
            coll.booster_packs, coll.id
        )
        
################################################################################
    def _update_trading_card(self, card: TradingCard) -> None:
        
        self.execute(
            "UPDATE trading_cards SET card_idx = %s WHERE _id = %s",
            card.index, card.id
        )
        
################################################################################
    def _update_card_deck(self, deck: CardDeck) -> None:
        
        self.execute(
            "UPDATE tcg_card_decks SET name = %s, image = %s WHERE _id = %s",
            deck.name, deck.image, deck.id
        )
        
################################################################################
    def _update_deck_card_slot(self, slot: DeckCardSlot) -> None:
        
        self.execute(
            "UPDATE tcg_deck_card_slots SET sort_order = %s, card_id = %s "
            "WHERE _id = %s",
            slot.order, slot.card.id, slot.id
        )
        
################################################################################
    
    form                    = _update_form
    form_option             = _update_form_option
    form_question           = _update_form_question
    question_prompt         = _update_question_prompt
    form_prompt             = _update_form_prompt
    profile_manager         = _update_profile_system
    trading_card_details    = _update_card_details
    trading_card_stats      = _update_card_stats
    card_count              = _update_card_count
    role_relation           = _update_role_relation
    verification_config     = _update_verification_config
    profile_channel_group   = _update_profile_channel_group
    profile_requirements     = _update_profile_requirements
    preference_group        = _update_preference_group
    profile_preferences     = _update_profile_preferences
    booster_pack_config     = _update_booster_pack_config
    booster_card_config     = _update_booster_card_config
    rarity_weight           = _update_rarity_weight
    profile_details         = _update_profile_details
    profile_ataglance       = _update_profile_ataglance
    profile_personality     = _update_profile_personality
    profile_images          = _update_profile_images
    additional_image        = _update_additional_image
    profile                 = _update_profile
    card_collection         = _update_card_collection
    trading_card            = _update_trading_card
    card_deck               = _update_card_deck
    deck_card_slot          = _update_deck_card_slot
    
################################################################################
