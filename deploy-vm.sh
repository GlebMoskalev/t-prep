#!/bin/bash

# Скрипт для деплоя T-Prep на VM через GitHub Actions

set -e

echo "🚀 Деплой T-Prep Backend на VM"
echo "==============================="

# Устанавливаем переменные окружения по умолчанию
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-tprep_password}

echo "📋 Переменные окружения:"
echo "   POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}"

# Переходим в директорию проекта
cd /opt/t-prep

# Останавливаем текущие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker compose -f docker-compose.prod.yml down || true

# Получаем последние изменения
echo "📥 Обновляем код из репозитория..."
git fetch origin
git reset --hard origin/main || git reset --hard origin/master

# Создаем .env файл из шаблона (если не существует)
if [ ! -f .env ]; then
    echo "📝 Создаем .env файл из шаблона..."
    cp env.prod.example .env
    echo "⚠️  Не забудьте настроить .env файл с реальными значениями!"
fi

# Пересобираем и запускаем контейнеры
echo "🔨 Собираем и запускаем контейнеры..."
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

# Ждем запуска сервисов
echo "⏳ Ожидание запуска сервисов..."
sleep 15

# Выполняем миграции базы данных
echo "🗄️  Выполняем миграции базы данных..."
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-tprep_password}
./scripts/migrate-db.sh || {
    echo "❌ Ошибка при выполнении миграций"
    echo "📋 Логи контейнеров:"
    docker compose -f docker-compose.prod.yml logs web
    exit 1
}

# Проверяем статус
echo "📊 Статус контейнеров:"
docker compose -f docker-compose.prod.yml ps

# Проверяем здоровье API
echo "🔍 Проверяем работу API..."
sleep 5

if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ API работает корректно!"
    echo "🌐 Доступно по адресу: http://localhost"
    echo "📊 Статус: http://localhost/health"
else
    echo "❌ API не отвечает"
    echo "📋 Логи контейнеров:"
    docker compose -f docker-compose.prod.yml logs web
    exit 1
fi

echo "🎉 Деплой на VM завершен успешно!"
