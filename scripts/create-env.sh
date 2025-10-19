#!/bin/bash

# Скрипт для создания файла .env на основе env.prod.example

if [ ! -f .env ]; then
    echo "📝 Создание файла .env на основе env.prod.example..."
    cp env.prod.example .env
    echo "✅ Файл .env создан!"
    echo "⚠️  Не забудьте изменить значения в файле .env перед деплоем!"
else
    echo "ℹ️  Файл .env уже существует"
fi
