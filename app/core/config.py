from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database - автоматически определяем URL в зависимости от окружения
    database_url: str = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Если DATABASE_URL не задан, формируем его автоматически
        if not self.database_url:
            # В Docker контейнере используем внутренний хост 'db'
            # В локальной разработке используем 'localhost'
            if os.getenv('DOCKER_CONTAINER') == '1' or os.path.exists('/.dockerenv'):
                host = 'db'
                print(f"🐳 Docker environment detected, using host: {host}")
            else:
                host = 'localhost'
                print(f"💻 Local environment detected, using host: {host}")
            
            postgres_password = os.getenv('POSTGRES_PASSWORD', 'tprep_password')
            self.database_url = f"postgresql://tprep_user:{postgres_password}@{host}:5432/tprep_db"
            print(f"🔗 Database URL: {self.database_url}")
    
    # JWT
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google OAuth
    google_client_id: str = "your-google-client-id"
    google_client_secret: str = "your-google-client-secret"
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"
    
    # Android OAuth (for mobile app)
    android_client_id: str = "your-android-client-id"
    
    # App settings
    debug: bool = True
    allowed_origins: str = "*"  # CORS origins, can be comma-separated
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Игнорировать неизвестные поля
    }
    
    FCM_API_KEY: str = "you-fcm-api-key"
    PUSH_INTERVAL_MINUTES: int = 10


settings = Settings()
