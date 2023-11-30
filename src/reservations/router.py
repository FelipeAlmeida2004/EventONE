from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.database import get_async_session
from src.reservations.models import Reservation
from src.events.models import Event
from src.reservations.schemas import ReservationResponse, ReservationCreate, ReservationUpdate
from sqlalchemy import select

router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"]
)


@router.get("/", response_model=List[ReservationResponse])
async def get_events(session: AsyncSession = Depends(get_async_session)):
    query = select(Reservation)
    query_result = await session.scalars(query)
    result = query_result.all()

    return result


@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_event(reservation_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Reservation).where(Reservation.id == reservation_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None:
        raise HTTPException(status_code=404, detail="Reserva não foi encontrada")
    
    return result

@router.post("/", response_model=ReservationResponse)
async def create_event(payload: ReservationCreate, session: AsyncSession = Depends(get_async_session)):
    query = select(Event.capacity).where(Event.id == payload.event_id)
    query_result = await session.scalars(query)
    max_capacity = query_result.first()

    if not max_capacity:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    query = select(Reservation.num_guests).where(Reservation.event_id == payload.event_id)
    query_result = await session.scalars(query)
    num_guests_array = query_result.all()
    num_guest = sum(num_guests_array)

    if num_guest + payload.num_guests > max_capacity:
        raise HTTPException(status_code=400, detail="Reservas esgotadas")
    
    new_reservation = Reservation(
        num_guests=payload.num_guests,
        user_id=payload.user_id,
        event_id=payload.event_id
    )

    session.add(new_reservation)

    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Reserva já foi cadastrada") 
    return new_reservation

@router.patch("/{reservation_id}", response_model=ReservationResponse)
async def update_event(reservation_id: int, payload: ReservationUpdate, session: AsyncSession = Depends(get_async_session)):
    query = select(Reservation).where(Reservation.id == reservation_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None:
        raise HTTPException(status_code=404, detail="Reserva não foi encontrada")
    
    for field, value in payload.model_dump().items():
        if value is not None:
            setattr(result, field, value)
    
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Reserva já foi cadastrada")
    return result


@router.delete("/{reservation_id}", status_code=204)
async def delete_event(reservation_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Reservation).where(Reservation.id == reservation_id)
    query_result = await session.scalars(query)
    result = query_result.first()

    if result is None:
        raise HTTPException(status_code=404, detail="Reserva não foi encontrada")
    
    session.delete(result)

    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Reserva já foi cadastrada")
    return result