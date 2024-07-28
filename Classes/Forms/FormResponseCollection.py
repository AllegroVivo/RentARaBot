from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Type, TypeVar, Tuple, Any

from discord import User, Embed, EmbedField

from Utilities import Utilities as U

if TYPE_CHECKING:
    from Classes import Form
################################################################################

__all__ = ("FormResponseCollection", )

FRC = TypeVar("FRC", bound="FormResponseCollection")

################################################################################
class FormResponseCollection:

    __slots__ = (
        "_id",
        "_parent",
        "_user",
        "_questions",
        "_responses"
    )
    
################################################################################
    def __init__(self, parent: Form, _id: str, **kwargs) -> None:

        self._id: str = _id
        self._parent: Form = parent
        self._user: User = kwargs.pop("user")
        
        self._questions: List[str] = kwargs.get("questions", [])
        self._responses: List[str] = kwargs.get("responses", [])
    
################################################################################
    @classmethod
    def new(cls: Type[FRC], parent: Form, user: User, q: List[str], r: List[str]) -> FRC:
        
        new_id = parent.bot.database.insert.form_response_coll(parent.id, user.id, q, r)
        return cls(parent, new_id, user=user, questions=q, responses=r)
    
################################################################################
    @classmethod
    async def load(cls: Type[FRC], parent: Form, data: Tuple[Any, ...]) -> FRC:
        
        return cls(
            parent=parent,
            _id=data[0],
            user=await parent.bot.fetch_user(data[2]),
            questions=data[3],
            responses=data[4]
        )
    
################################################################################
    @property
    def user(self) -> User:
        
        return self._user
    
################################################################################
    @property
    def questions(self) -> List[str]:
        
        return self._questions
    
################################################################################
    @property
    def responses(self) -> List[str]:
        
        return self._responses
    
################################################################################
    def compile(self) -> Embed:

        fields = []
        for question, response in zip(self.questions, self.responses):
            fields.append(EmbedField(name=question, value=response, inline=False))

        return U.make_embed(
            title=f"Application Responses for {self.user.display_name}",
            description=f"({self.user.mention})",
            fields=fields
        )

################################################################################
