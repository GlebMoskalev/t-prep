#!/bin/bash

# Быстрое исправление для деплоя на VM
# Этот скрипт можно запустить на VM для исправления проблемы с паролем

set -e

echo "🔧 Быстрое исправление деплоя на VM"
echo "===================================="

# Устанавливаем переменную окружения
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-tprep_password}

echo "📋 POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}"

# Переходим в директорию проекта
cd /opt/t-prep

# Выполняем миграции с правильным паролем
echo "🗄️  Выполняем миграции с правильным паролем..."
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-tprep_password}
./scripts/migrate-db.sh

# Проверяем статус
echo "📊 Статус контейнеров:"
docker compose -f docker-compose.prod.yml ps

# Проверяем API
echo "🔍 Проверяем API..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ API работает!"
else
    echo "❌ API не отвечает"
    echo "📋 Логи:"
    docker compose -f docker-compose.prod.yml logs web --tail=20
fi

echo "🎉 Исправление завершено!"
