from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.database import get_async_session
from src.events.models import Event
from src.events.schemas import EventResponse, EventCreate, EventUpdate
from sqlalchemy import select

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


@router.get("/", response_model=List[EventResponse])
async def get_events(session: AsyncSession = Depends(get_async_session)):
    query = select(Event)
    query_result = await session.scalars(query)
    result = query_result.all()

    return result


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Event).where(Event.id == event_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    return result

@router.post("/", response_model=EventResponse)
async def create_event(payload: EventCreate, session: AsyncSession = Depends(get_async_session)):
    new_event = Event(
        name=payload.name,
        date=payload.date,
        location=payload.location,
        user_id=payload.user_id,
        capacity=payload.capacity,
        content=payload.content
    )

    session.add(new_event)

    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Evento já foi cadastrado") 
    return new_event

@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(event_id: int, payload: EventUpdate, session: AsyncSession = Depends(get_async_session)):
    query = select(Event).where(Event.id == event_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    for field, value in payload.model_dump().items():
        if value is not None:
            setattr(result, field, value)
    
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Evento já foi cadastrado")
    return result


@router.delete("/{event_id}", status_code=204)
async def delete_event(event_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Event).where(Event.id == event_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    session.delete(result)

    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Evento já foi cadastrado")
    return result