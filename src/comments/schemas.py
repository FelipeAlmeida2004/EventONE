from typing import Optional
from src.schemas import CustomBase
from pydantic import PositiveInt, Field


class ContentSchema(CustomBase):
    title: str = Field(..., examples=["Título"])
    text: str = Field(..., examples=["Conteúdo do comentário"])
    raiting: int = Field(..., ge=1, le=10, examples=[5])


class CommentResponse(CustomBase):
    id: PositiveInt
    content: ContentSchema
    user_id: PositiveInt = Field(..., examples=[1])
    event_id: PositiveInt = Field(..., examples=[1])


class CommentCreate(CustomBase):
    content: ContentSchema
    user_id: PositiveInt = Field(..., examples=[1])
    event_id: PositiveInt = Field(..., examples=[1])


class CommentUpdate(CustomBase):
    content: Optional[ContentSchema] = None
    user_id: Optional[int] = Field(None, examples=[1])
    event_id: Optional[int] = Field(None, examples=[1])
