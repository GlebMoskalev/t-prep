#!/bin/bash

# Скрипт для создания .env файла из GitHub Secrets (для локального тестирования)

set -e

echo "🔧 Создание .env файла из GitHub Secrets..."

# Проверяем, что мы в корневой директории проекта
if [ ! -f "main.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории проекта"
    exit 1
fi

# Создаем .env файл
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://tprep_user:tprep_password@localhost:5432/tprep_db
POSTGRES_PASSWORD=tprep_password

# JWT
SECRET_KEY=your-very-secure-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth (Web)
GOOGLE_CLIENT_ID=16700008449-hd5rvf447ju8h6f5cpglgr3vva1nt77d.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Google OAuth (Android)
ANDROID_CLIENT_ID=your-android-client-id

# App settings
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000

# Logging
LOG_LEVEL=DEBUG
EOF

echo "✅ .env файл создан для локальной разработки"
echo "⚠️  ВНИМАНИЕ: Это локальные настройки для разработки"
echo "   Для продакшена используйте GitHub Secrets"
