from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.database import get_async_session
from src.comments.models import Comment
from src.comments.schemas import CommentResponse, CommentCreate, CommentUpdate

from sqlalchemy import select

router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)

@router.get("/", response_model=List[CommentResponse])
async def get_comments(session: AsyncSession = Depends(get_async_session)):
    query = select(Comment)
    query_result = await session.scalars(query)
    result = query_result.all()

    return result

@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Comment).where(Comment.id == comment_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result in None:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar o comentário")

    return result

@router.post("/", response_model=CommentResponse, status_code=201)
async def create_comment(payload: CommentCreate, session: AsyncSession = Depends(get_async_session)):
    new_comment = Comment(
        content=payload.content.model_dump(),
        user_id=payload.user_id,
        event_id=payload.event_id
    )

    session.add(new_comment)
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Comentário já foi cadastrado")
    return new_comment

@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, payload: CommentUpdate, session: AsyncSession = Depends(get_async_session)):
    query = select(Comment).where(Comment.id == comment_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar o comentário")

    for field, value in payload.model_dump().items():
        if value is not None:
            setattr(result, field, value)

    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Comentário já foi cadastrado")
    return result

@router.delete("/{comment_id}", status_code=204)
async def delete_comment(comment_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Comment).where(Comment.id == comment_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None:
        raise HTTPException(status_code=400, detail="Não foi possível encontrar o comentário")

    session.delete(result)
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Comentário já foi cadastrado")
    return result