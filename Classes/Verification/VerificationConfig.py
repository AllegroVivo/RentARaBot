from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar, Any, Tuple

from discord import Interaction

if TYPE_CHECKING:
    from Classes import VerificationManager, FroggeBot
################################################################################

__all__ = ("VerificationConfig", )

VC = TypeVar("VC", bound="VerificationConfig")

################################################################################
class VerificationConfig:

    __slots__ = (
        "_mgr",
        "_log_events",
        "_require_captcha",
        "_change_name",
    )
    
################################################################################
    def __init__(self, mgr: VerificationManager, **kwargs) -> None:

        self._mgr: VerificationManager = mgr
        
        self._log_events: bool = kwargs.get("log_events", True)
        self._require_captcha: bool = kwargs.get("require_capcha", True)
        self._change_name: bool = kwargs.get("change_name", True)
    
################################################################################
    @classmethod
    async def load(cls: Type[VC], mgr: VerificationManager, data: Tuple[Any, ...]) -> VC:
        
        return cls(
            mgr=mgr,
            log_events=data[1],
            require_capcha=data[2],
            change_name=data[3],
        )
    
################################################################################
    @property
    def bot(self) -> FroggeBot:
        
        return self._mgr.bot
    
################################################################################
    @property
    def guild_id(self) -> int:
        
        return self._mgr.guild_id
    
################################################################################
    @property
    def log_events(self) -> bool:
        
        return self._log_events
    
    @log_events.setter
    def log_events(self, value: bool) -> None:
        
        self._log_events = value
        self.update()
        
################################################################################
    @property
    def require_captcha(self) -> bool:
        
        return self._require_captcha
    
    @require_captcha.setter
    def require_captcha(self, value: bool) -> None:
        
        self._require_captcha = value
        self.update()
        
################################################################################
    @property
    def change_name(self) -> bool:
        
        return self._change_name
    
    @change_name.setter
    def change_name(self, value: bool) -> None:
        
        self._change_name = value
        self.update()
        
################################################################################
    def update(self) -> None:
        
        self.bot.database.update.verification_config(self)
        
################################################################################
    async def toggle_logging(self, interaction: Interaction) -> None:
        
        self.log_events = not self.log_events
        await interaction.respond("** **", delete_after=0.1)
        
################################################################################
    async def toggle_captcha(self, interaction: Interaction) -> None:
        
        self.require_captcha = not self.require_captcha
        await interaction.respond("** **", delete_after=0.1)
        
################################################################################
    async def toggle_change_name(self, interaction: Interaction) -> None:
        
        self.change_name = not self.change_name
        await interaction.respond("** **", delete_after=0.1)
        
################################################################################
        