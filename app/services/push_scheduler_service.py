# app/services/push_scheduler.py
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

class PushScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
    async def send_scheduled_notifications(self):
        """Основная задача для отправки уведомлений"""
        from app.services.push_service import push_service

        logger.info(f"⏰ Running scheduled notification check at {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Отправляем учебные напоминания
            await push_service.send_study_reminders()
            
        except Exception as e:
            logger.error(f"❌ Error in scheduled task: {e}", exc_info=True)
    
    def start(self):
        """Запуск планировщика"""
        if self.scheduler.running:
            logger.warning("Scheduler already running")
            return
        
        # Основная задача - каждые 10 минут
        self.scheduler.add_job(
            self.send_scheduled_notifications,
            trigger=IntervalTrigger(minutes=settings.PUSH_INTERVAL_MINUTES),
            id="study_reminders",
            name="Учебные напоминания",
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info(f"🚀 Push scheduler started with {len(self.scheduler.get_jobs())} jobs")
        logger.info(f"📅 Next run: {self.scheduler.get_job('study_reminders').next_run_time}")
    
    def stop(self):
        """Остановка планировщика"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("🛑 Push scheduler stopped")

# Глобальный экземпляр
push_scheduler = PushScheduler()