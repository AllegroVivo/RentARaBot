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
            "character_group = %s, series = %s, image_url = %s, rarity = %s "
            "WHERE card_id = %s",
            details.name, details.description, 
            details.group.value if details.group else None, 
            details.series.value if details.series else None, 
            details.image, details.rarity.value, details._parent.id
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
    
    form                    = _update_form
    form_option             = _update_form_option
    form_question           = _update_form_question
    question_prompt         = _update_question_prompt
    form_prompt             = _update_form_prompt
    profile_manager         = _update_profile_system
    trading_card_details    = _update_card_details
    trading_card_stats      = _update_card_stats
    card_count              = _update_card_count
    
################################################################################
