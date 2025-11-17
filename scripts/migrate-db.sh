#!/bin/bash

# Скрипт для выполнения миграций базы данных в Docker

set -e

# Устанавливаем переменные окружения по умолчанию
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-tprep_password}

echo "🔄 Выполнение миграций базы данных..."

# Проверяем, что мы в Docker окружении
if [ -f docker-compose.prod.yml ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
else
    COMPOSE_FILE="docker-compose.yml"
fi

echo "📋 Используем файл: $COMPOSE_FILE"

# Ждем готовности базы данных
echo "⏳ Ожидание готовности базы данных..."
docker compose -f $COMPOSE_FILE exec -T db pg_isready -U tprep_user -d tprep_db || {
    echo "❌ База данных не готова"
    exit 1
}

echo "✅ База данных готова"

# Выполняем миграции Alembic
echo "🚀 Выполнение миграций Alembic..."
docker compose -f $COMPOSE_FILE exec -T web alembic upgrade head || {
    echo "❌ Ошибка при выполнении миграций"
    exit 1
}

echo "✅ Миграции выполнены успешно!"

# Проверяем статус миграций
echo "📊 Текущий статус миграций:"
docker compose -f $COMPOSE_FILE exec -T web alembic current

echo "🎉 Все миграции выполнены!"
