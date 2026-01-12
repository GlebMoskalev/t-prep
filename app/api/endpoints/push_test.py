# app/api/endpoints/push_test.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.push_service import push_service

router = APIRouter()


class TestPushRequest(BaseModel):
    fcm_token: str
    title: str = "🔔 Тестовый пуш"
    body: str = "Привет от T-Prep бэкенда!"
    data: Optional[Dict[str, str]] = None


@router.post("/send")
def send_test_push(request: TestPushRequest):
    """Отправить тестовый пуш на устройство"""
    result = push_service.send_push(
        fcm_token=request.fcm_token,
        title=request.title,
        body=request.body,
        data=request.data or {"type": "test", "click_action": "FLUTTER_NOTIFICATION_CLICK"}
    )
    return {
        "push_service_initialized": push_service.is_initialized,
        "result": result
    }


@router.get("/status")
def push_status():
    """Проверить статус push сервиса"""
    return {
        "initialized": push_service.is_initialized
    }
