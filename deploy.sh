#!/bin/bash

# Скрипт для деплоя T-Prep в продакшн

set -e

echo "🚀 Деплой T-Prep Backend"
echo "========================"

# Устанавливаем переменные окружения по умолчанию
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-tprep_password}

echo "📋 Переменные окружения:"
echo "   POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}"

# Останавливаем существующие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker compose -f docker-compose.prod.yml down || true

# Собираем и запускаем контейнеры
echo "🔨 Собираем и запускаем контейнеры..."
docker compose -f docker-compose.prod.yml up --build -d

# Ждем готовности базы данных
echo "⏳ Ожидание готовности базы данных..."
sleep 10

# Выполняем миграции
echo "🗄️  Выполняем миграции базы данных..."
./scripts/migrate-db.sh

# Проверяем работу API
echo "🔍 Проверяем работу API..."
sleep 5

if curl -s http://localhost/health > /dev/null; then
    echo "✅ API работает корректно!"
    echo "🌐 Доступно по адресу: http://localhost"
    echo "📊 Статус: http://localhost/health"
else
    echo "❌ API не отвечает"
    echo "📋 Логи контейнеров:"
    docker compose -f docker-compose.prod.yml logs web
    exit 1
fi

echo "🎉 Деплой завершен успешно!"
