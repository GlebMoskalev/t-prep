#!/bin/bash

echo "🚀 Запуск T-Prep Backend"
echo "========================"

# Устанавливаем переменные окружения по умолчанию
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-tprep_password}

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден. Копируем из env.example..."
    cp env.example .env
    echo "📝 Отредактируйте файл .env с вашими настройками Google OAuth"
    echo "   Особенно важны:"
    echo "   - GOOGLE_CLIENT_ID"
    echo "   - GOOGLE_CLIENT_SECRET" 
    echo "   - ANDROID_CLIENT_ID"
    echo ""
fi

# Проверяем установку зависимостей
if [ ! -d "venv" ]; then
    echo "📦 Создаем виртуальное окружение..."
    python3 -m venv venv
fi

echo "📦 Активируем виртуальное окружение..."
source venv/bin/activate

echo "📦 Устанавливаем зависимости..."
pip install -r requirements.txt

echo "🗄️  Запускаем базу данных..."
docker-compose up -d db

echo "⏳ Ждем запуска базы данных..."
sleep 5

echo "🚀 Запускаем сервер..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
