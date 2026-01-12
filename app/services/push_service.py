# app/services/push_service.py
import asyncio
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from app.core.config import settings
from app.db.database import SessionLocal
from firebase_admin import credentials, initialize_app, messaging
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)


class PushNotificationService:
    def __init__(self):
        self.is_initialized = False
        self._initialize_fcm()
    
    def _initialize_fcm(self):
        """Инициализация Firebase Admin SDK"""
        if hasattr(settings, 'FCM_SERVICE_ACCOUNT_FILE') and settings.FCM_SERVICE_ACCOUNT_FILE:
            file_path = settings.FCM_SERVICE_ACCOUNT_FILE
            # Пропускаем дефолтное значение
            if file_path == 'path-to-file':
                logger.warning("⚠️ FCM_SERVICE_ACCOUNT_FILE not configured, push notifications disabled")
                return
            try:
                with open(file_path, 'r') as file:
                    cred_dict = json.load(file)
                    cred = credentials.Certificate(cred_dict)
                    initialize_app(cred)
                    self.is_initialized = True
                    logger.info("✅ FCM initialized with credentials from env variable")
                    return
            except FileNotFoundError:
                logger.error(f"❌ FCM credentials file not found: {file_path}")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON in FCM credentials: {e}")
    
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
        if not self.is_initialized:
            return {"error": "Push service not initialized"}
        
        if not fcm_token:
            return {"error": "Empty FCM token"}
        
        try:
            # Создаем сообщение для Android
            android_config = messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    sound='default',
                    click_action='FLUTTER_NOTIFICATION_CLICK',
                    channel_id='high_importance_channel'
                )
            )
            
            # Создаем сообщение для APNs (iOS)
            
            # Создаем уведомление
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image
            )
            
            # Создаем сообщение
            message = messaging.Message(
                token=fcm_token,
                notification=notification,
                data=data or {},
                android=android_config
            )
            
            # Отправляем сообщение
            response = messaging.send(message)
            
            logger.info(f"✅ Push sent to {fcm_token[:15]}...: {response}")
            return {
                "success": True,
                "message_id": response,
                "result": {"name": response}
            }
            
        except messaging.UnregisteredError:
            logger.warning(f"❌ Token not registered: {fcm_token[:15]}...")
            return {"error": "token_not_registered", "message": "Token is not registered"}
            
        except messaging.InvalidArgumentError:
            logger.warning(f"❌ Invalid token: {fcm_token[:15]}...")
            return {"error": "invalid_token", "message": "Invalid FCM token"}
            
        except FirebaseError as e:
            error_msg = str(e)
            logger.error(f"❌ Firebase error sending push to {fcm_token[:15]}...: {error_msg}")
            return {"error": "firebase_error", "message": error_msg}
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Error sending push to {fcm_token[:15]}...: {error_msg}", exc_info=True)
            return {"error": "send_failed", "message": error_msg}

    async def send_study_reminders(self):
        """Отправка напоминаний о повторении карточек"""
        if not self.is_initialized:
            logger.warning("Push service not initialized, skipping reminders")
            return
        
        from app.models.user import User
        
        print("AAAAA")
        db = SessionLocal()
        try:
            current_time = datetime.now()
        
            users_with_due_cards = db.query(
                User.id,
                User.push_id
            ).filter(
                User.push_id.isnot(None)
            ).distinct().all()
            
            sent_count = 0
            print(users_with_due_cards.__len__())
            for user in users_with_due_cards:
                result = self.send_push(
                    fcm_token=user.push_id,
                    title="📚 T-Prep: Время учиться!",
                    body=f"Время повторить уроки!",
                    data={
                        "type": "study_reminder",
                        "userId": str(user.id),
                        "timestamp": current_time.isoformat(),
                        "click_action": "FLUTTER_NOTIFICATION_CLICK"
                    }
                )
                print(result)

                if not result.get("error"):
                    sent_count += 1
                    logger.info(f"📨 Reminder sent to user {user.id} ( cards due)")
                else:
                    print(result.get("error"))

            logger.info(f"✅ Study reminders sent: {sent_count}/{len(users_with_due_cards)}")
            
        except Exception as e:
            logger.error(f"❌ Error sending study reminders: {e}", exc_info=True)
        finally:
            db.close()


push_service = PushNotificationService()