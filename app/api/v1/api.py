from fastapi import APIRouter
from ..endpoints import auth, users, modules, cards

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(modules.router, prefix="/modules", tags=["modules"])
api_router.include_router(cards.router, prefix="/cards", tags=["cards"])
