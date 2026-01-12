from fastapi import APIRouter
from ..endpoints import auth, users, modules, cards, repetitions, push_test

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(modules.router, prefix="/modules", tags=["modules"])
api_router.include_router(cards.router, prefix="/modules/{module_id}/cards", tags=["cards"])
api_router.include_router(repetitions.router, prefix="/modules/{module_id}/interval-repetitions", tags=["interval_repetitions"])
api_router.include_router(push_test.router, prefix="/push-test", tags=["push_test"])