from fastapi import FastAPI
from src.users.router import router as user_router
from src.reservations.router import router as reservation_router
from src.events.router import router as events_router
from src.comments.router import router as comments_router
from src.config import settings

app = FastAPI(
    title=settings.app_name,
)

app.include_router(user_router)
app.include_router(reservation_router)
app.include_router(events_router)
app.include_router(comments_router)

