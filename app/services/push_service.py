# app/services/push_service.py
import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.config import settings
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)

class PushNotificationService:
    def __init__(self):
        self.push_service = None
        self.is_running = False
        
        if settings.FCM_API_KEY:
            # Импортируем здесь, чтобы не зависеть от установки библиотеки
            try:
                from firebase_admin import messaging, credentials
                import firebase_admin
                
                # Инициализация Firebase Admin SDK
                if not firebase_admin._apps:
                    # Если у вас есть service account key
                    # cred = credentials.Certificate("path/to/service-account-key.json")
                    # firebase_admin.initialize_app(cred)
                    
                    # Или инициализируем с помощью API ключа
                    from pyfcm import FCMNotification
                    self.push_service = FCMNotification(api_key=settings.FCM_API_KEY)
                    
                logger.info("✅ Push notification service initialized")
            except ImportError:
                logger.error("❌ Firebase libraries not installed. Run: pip install firebase-admin pyfcm")
        else:
            logger.warning("⚠️  FCM_API_KEY not configured. Push notifications disabled.")
    
    def send_push(
        self,
        fcm_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        image: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Отправка push-уведомления на одно устройство
        
        Args:
            fcm_token: Токен устройства
            title: Заголовок уведомления
            body: Текст уведомления
            data: Дополнительные данные
            image: URL изображения для уведомления
        
        Returns:
            Результат отправки
        """
        if not self.push_service:
            return {"error": "Push service not initialized"}
        
        try:
            # Используем метод notify из вашей версии библиотеки
            result = self.push_service.notify(
                fcm_token=fcm_token,
                notification_title=title,
                notification_body=body,
                notification_image=image,
                data_payload=data or {},
                android_config={
                    "priority": "high",
                    "notification": {
                        "sound": "default",
                        "click_action": "FLUTTER_NOTIFICATION_CLICK",
                        "channel_id": "high_importance_channel"
                    }
                }
            )
            
            logger.info(f"✅ Push sent to {fcm_token[:15]}...: {result.get('name', 'No name')}")
            return {"success": True, "result": result}
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Error sending push to {fcm_token[:15]}...: {error_msg}")
            
            # Обработка специфичных ошибок FCM
            if "registration-token-not-registered" in error_msg.lower() or "notregistered" in error_msg.lower():
                return {"error": "token_not_registered", "message": error_msg}
            elif "invalid-registration" in error_msg.lower():
                return {"error": "invalid_token", "message": error_msg}
            else:
                return {"error": "send_failed", "message": error_msg}
    
    async def send_push_async(
        self,
        fcm_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Асинхронная обертка для отправки push"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.send_push,
            fcm_token,
            title,
            body,
            data
        )
    
    def send_to_multiple(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Отправка уведомлений на несколько устройств
        
        Note: В вашей версии библиотеки нет встроенной мультирассылки,
        поэтому отправляем последовательно
        """
        results = []
        
        for token in tokens:
            if token:  # Проверяем, что токен не пустой
                result = self.send_push(token, title, body, data)
                results.append({
                    "token": token[:15] + "...",
                    "result": result
                })
        
        # Статистика
        success_count = sum(1 for r in results if r["result"].get("success") or not r["result"].get("error"))
        logger.info(f"📊 Batch send: {success_count}/{len(tokens)} successful")
        
        return results
    
    async def send_study_reminders(self):
        """Отправка напоминаний о повторении карточек"""
        if not self.push_service:
            logger.warning("Push service not initialized, skipping reminders")
            return
        
        from app.models.user import User
        
        db = SessionLocal()
        try:
            current_time = datetime.now()
            
            # Находим пользователей с карточками для повторения
            # Более сложный запрос для получения детальной информации
            query = db.query(
                User.id,
                User.push_token
            ).filter(
                User.push_token.isnot(None)
            ).group_by(User.id).distinct()
            
            users = query.all()
            
            sent_count = 0
            for user in users:
                result = await self.send_push_async(
                    fcm_token=user.push_token,
                    title="📚 T-Prep: Время учиться!",
                    body=f"У вас есть карточки для повторения",
                    data={
                        "type": "study_reminder",
                        "userId": str(user.id),
                        "timestamp": current_time.isoformat(),
                        "click_action": "FLUTTER_NOTIFICATION_CLICK"
                    }
                )

                if not result.get("error"):
                    sent_count += 1

                    logger.info(f"📨 Reminder sent to user ({user.id})")

            logger.info(f"✅ Study reminders sent: {sent_count}/{len(users)}")
            
        except Exception as e:
            logger.error(f"❌ Error sending study reminders: {e}", exc_info=True)
        finally:
            db.close()


push_service = PushNotificationService()